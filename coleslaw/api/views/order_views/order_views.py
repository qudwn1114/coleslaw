from django.views.generic import View
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.db.models import CharField, F, Value as V, Func, Case, When, Prefetch, Sum
from django.db import transaction, IntegrityError
from django.core.serializers.json import DjangoJSONEncoder
from system_manage.views.system_manage_views.auth_views import validate_phone
from django.utils import timezone, dateformat
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from api.views.pos_views.order_views import issue_order_no

from system_manage.models import Shop,Checkout, CheckoutDetail, Order, OrderGoods, OrderGoodsOption, OrderPayment, SmsLog
from api.views.sms_views.sms_views import send_sms

import portone_server_sdk as portone

portone_client = portone.PaymentClient(secret=settings.PORTONE_API_SECRET)

import traceback, json, datetime, uuid, logging

class ShopOrderCreateView(View):
    '''
        shop 주문생성
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ShopOrderCreateView, self).dispatch(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        checkout_id = kwargs.get('checkout_id')
        code = kwargs.get('code')
        try:
            shop = Shop.objects.get(pk=shop_id)
        except:
            return_data = {'data': {},'msg': 'shop id 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")

        try:
            checkout = Checkout.objects.get(pk=checkout_id, code=code)
        except:
            return_data = {'data': {},'msg': 'checkout id/code 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        # 한시간
        if (timezone.now() - checkout.created_at).seconds >= 3600:
            return_data = {'data': {},'msg': '주문 시간초과.. 장바구니에서 다시 주문해주세요.','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")

        membername = request.POST['membername'].strip()
        phone = request.POST['phone']

        if not validate_phone(phone):
            return_data = {'data': {},'msg': '유효하지 않은 전화번호 형식입니다.','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        total_quantity = checkout.checkout_detail.all().aggregate(sum=Sum('quantity')).get('sum')
        try:
            with transaction.atomic():
                try:
                    order_code = uuid.uuid4().hex
                    order_no = issue_order_no(shop, timezone.now().date())
                    order = Order.objects.create(
                        agency=checkout.agency,
                        shop=shop,
                        order_type='1',
                        order_membername=membername,
                        order_phone=phone, 
                        status='0', 
                        order_code = order_code,
                        order_no=order_no,
                        final_price = checkout.final_price
                    )
                except IntegrityError:
                    raise ValueError("주문번호 중복 다시 시도해주세요.")
                except:
                    raise ValueError("주문생성실패")
                order_name_kr = ''
                order_name_en = ''
                for i in checkout.checkout_detail.all():
                    if order_name_kr == '':
                        if total_quantity == 1:
                            order_name_kr = f"{i.goods.name_kr} {total_quantity}개"
                            order_name_en = f"{i.goods.name_en} {total_quantity}"
                        else:
                            order_name_kr = f"{i.goods.name_kr} 외 {total_quantity-1}개"
                            order_name_en = f"{i.goods.name_en} and {total_quantity-1} others"

                    if i.goods.soldout:
                        raise ValueError(f"{i.goods.name} 상품이 판매 중단되었습니다.")
                    
                    if i.goods.stock_flag:
                         if i.goods.stock < i.quantity:
                            raise ValueError(f'{i.goods.name_kr} Out of Stock')
                         
                    
                    discount = (i.sale_price + i.sale_option_price) - i.price
                    if discount == 0: #할인없을때
                        price = i.sale_price
                        option_price = i.sale_option_price
                    elif discount > 0:
                        if i.sale_price <= discount:
                            price = 0
                            option_price = i.sale_option_price - (discount - i.sale_price)
                        else:
                            price = i.sale_price - discount
                            option_price = i.sale_option_price
                    else:
                        raise ValueError(f"Check Out Error")

                    order_goods = OrderGoods.objects.create(
                        order=order, 
                        goods=i.goods,
                        price=price, 
                        option_price=option_price, 
                        sale_option_price=i.sale_option_price,
                        sale_price=i.sale_price,
                        name_kr=i.goods.name_kr, 
                        name_en=i.goods.name_en,
                        quantity=i.quantity,
                        option_kr=None, 
                        option_en=None, 
                        total_price=i.total_price
                    )

                    if i.checkout_detail_option.all().exists():
                        option_kr = [] 
                        option_en = [] 
                        order_goods_option_bulk_list = []
                        for j in i.checkout_detail_option.all().order_by('id'):
                            if j.goods_option_detail.soldout:
                                raise ValueError(f"{i.goods.name_kr} {j.goods_option_detail.name_kr} Option Soldout")
                            
                            if j.goods_option_detail.stock_flag:
                                if j.goods_option_detail.stock < i.quantity:
                                    raise ValueError(f'{i.goods.name_kr} {j.goods_option_detail.name_kr} Out of Stock')
                            
                            option_kr.append(f"{j.goods_option_detail.goods_option.name_kr} : {j.goods_option_detail.name_kr}")
                            option_en.append(f"{j.goods_option_detail.goods_option.name_en} : {j.goods_option_detail.name_en}")
                            order_goods_option_bulk_list.append(OrderGoodsOption(order_goods=order_goods, goods_option_detail=j.goods_option_detail))

                        OrderGoodsOption.objects.bulk_create(order_goods_option_bulk_list)
                        option_kr = ' / '.join(option_kr)
                        option_en = ' / '.join(option_en)
                        order_goods.option_kr = option_kr
                        order_goods.option_en = option_en
                        order_goods.save()

                order.order_name_kr=order_name_kr
                order.order_name_en=order_name_en
                order.save()
                    
            return_data = {
                'data': {
                    'shop_id':shop.pk,
                    'order_id':order.pk,
                    'order_name_kr':order_name_kr,
                    'order_name_en':order_name_en,
                    'order_membername':membername,
                    'order_phone':phone,
                    'order_code':order_code,
                    'final_price':checkout.final_price,
                },
                'msg': '결제준비완료',
                'resultCd': '0000',
            }
        except ValueError as e:
            return_data = {
                'data': {},
                'msg': str(e),
                'resultCd': '0001',
            }
        except:
            return_data = {
                'data': {},
                'msg': traceback.format_exc(),
                'resultCd': '0001',
            }
    
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")
    

class ShopOrderCompleteView(View):
    '''
        shop complete
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ShopOrderCompleteView, self).dispatch(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        code = kwargs.get('code')
        order_id = kwargs.get('order_id')
        try:
            shop = Shop.objects.get(pk=shop_id)
        except:
            return_data = {'data': {},'msg': 'shop id 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        logger = logging.getLogger('my')
        logger.error(str(dict(request.POST)))
        try:
            order = Order.objects.get(pk=order_id, order_code=code)
        except:
            return_data = {'data': {},'msg': 'order id/code 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        payment_id = request.POST['payment_id']
        try:
            payment = portone_client.get_payment(payment_id=payment_id)
        except Exception:
            return JsonResponse({'data': {},'msg': '결제 조회 실패','resultCd': '0001'})
        
        if payment.amount.total != order.final_price:
            return JsonResponse({'data': {},'msg': '금액 불일치','resultCd': '0001'})
        
        tranDate = timezone.now().strftime("%y%m%d")
        tranTime = timezone.now().strftime('%H%M')

        try:    
            order_payment = OrderPayment.objects.create(
                order = order,
                status=True,
                payment_method='0', #카드
                tranDate = tranDate,
                tranTime = tranTime,
                amount = order.final_price,
                approvalNumber = payment_id
            )
            order.payment_method = '0'
            order.payment_price = order.final_price
            order.status = '3'
            order.save()

            # 재고관리
            for i in order.order_goods.all():
                if i.goods.stock_flag:
                    if i.goods.stock - i.quantity <= 0:
                        goods_soldout = True
                    else:
                        goods_soldout = False
                    g = i.goods
                    g.stock -= i.quantity
                    g.soldout = goods_soldout
                    g.save()

                for j in i.order_goods_option.all():
                    if j.goods_option_detail.stock_flag:
                        god = j.goods_option_detail
                        if god.stock - i.quantity <= 0:
                            option_detail_soldout = True
                        else:
                            option_detail_soldout = False
                        
                        god.stock -= i.quantity
                        god.soldout = option_detail_soldout
                        god.save()
            
            #에이전시 행사때만 문자발송!
            if order.agency:
                message=f'주문완료[{order.order_no}]\n{order.shop.qr_order_message}\n▼주문내역\n{order.shop.qr_link}'
                sms_response = send_sms(phone=order.order_phone, message=message)
                SmsLog.objects.create(
                    shop=shop,
                    shop_name=shop.name_kr,
                    phone=order.order_phone,
                    message=message
                )
            
            try:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'shop_order_{shop_id}',
                    {
                        'type': 'chat_message',
                        'message_type' : 'ORDER',
                        'title': '* 주문접수 * ',
                        'message': f'[{order.order_no}] {order.order_name_kr}'
                    }
                )
                receipt_data = {}
                receipt_data['order_payment_id'] = order_payment.pk
                async_to_sync(channel_layer.group_send)(
                    f'shop_entry_{shop_id}',
                    {
                        'type': 'chat_message',
                        'message_type' : 'QR',
                        'title': '* QR 주문접수 *',
                        'message': receipt_data
                    }
                )
            except:
                pass

            return_data = {
                'data': {
                    'shop_name_kr':shop.name_kr,
                    'shop_name_en':shop.name_en,
                    'order_id':order.pk,
                    'order_no':order.order_no,
                    'order_membername':order.order_membername,
                    'order_phone':order.order_phone
                },
                'msg': '결제완료',
                'resultCd': '0000',
            }
        except:
            logger.error(traceback.format_exc())
            return_data = {
                'data': {},
                'msg': traceback.format_exc(),
                'resultCd': '0001',
            }

        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")

@csrf_exempt
def portone_payment_webhook(request):
    body = request.body.decode("utf-8")
    try:
        webhook = portone.webhook.verify(settings.PORTONE_WEBHOOK_SECRET, body, request.headers)
    except Exception:
        logger = logging.getLogger('my')
        logger.error(traceback.format_exc())
        return JsonResponse({"message": "웹훅 실패"}, json_dumps_params={"ensure_ascii": False}, status=400)
    payment_id = webhook.data.payment_id
    if webhook.type == "Transaction.Paid":
        if not OrderPayment.objects.filter(approvalNumber=payment_id).exists():
            try:
                payment = portone_client.get_payment(payment_id=payment_id)
            except portone.payment.GetPaymentError:
                return JsonResponse({"message": "결제정보 오류"}, json_dumps_params={"ensure_ascii": False}, status=400)
            if payment.amount.total != order.final_price:
                return JsonResponse({"message":"금액 불일치"}, json_dumps_params={"ensure_ascii": False}, status=400)
            try:
                order_id = int(payment_id.replace('order_', ''))
            except (AttributeError, ValueError):
                return JsonResponse({"message": "payment_id 오류"}, json_dumps_params={"ensure_ascii": False}, status=400)
            try:
                order = Order.objects.get(pk=order_id)
            except:
                return JsonResponse({"message": "order_id 오류"}, status=400)
            tranDate = timezone.now().strftime("%y%m%d")
            tranTime = timezone.now().strftime('%H%M')
            order_payment = OrderPayment.objects.create(
                order = order,
                status=True,
                payment_method='0', #카드
                tranDate = tranDate,
                tranTime = tranTime,
                amount = order.final_price,
                approvalNumber = payment_id
            )
            order.payment_method = '0'
            order.payment_price = order.final_price
            order.status = '1'
            order.save()

    elif webhook.type == "Transaction.Cancelled":
        order_id = json.loads(payment.custom_data)["order_id"]
        try:
            order = Order.objects.get(pk=order_id)
        except:
            return JsonResponse({"message": "order_id 오류"}, json_dumps_params={"ensure_ascii": False}, status=400)
        order.status = '2'
        order.save()
        OrderPayment.objects.filter(order=order, approvalNumber=payment_id).update(status=False, cancelled_at = timezone.now())
    else:
        pass
    return JsonResponse({"message": "웹훅결제"}, json_dumps_params={"ensure_ascii": False}, status=200)

    
class ShopOrderStatusView(View):
    '''
        shop status
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ShopOrderStatusView, self).dispatch(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        order_id = kwargs.get('order_id')
        try:
            shop = Shop.objects.get(pk=shop_id)
        except:
            return_data = {'data': {},'msg': 'shop id 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        order_status = request.POST['order_status']
        status = ['1', '3', '4', '5']
        try:
            order = Order.objects.get(pk=order_id, shop=shop)
        except:
            return_data = {'data': {},'msg': 'order id/code 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        if order_status not in status:
            return_data = {'data': {},'msg': '상태 값 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        order.status = order_status
        order.save()

        return_data = {'data': {}, 'msg': '상태가 변경되었습니다.','resultCd': '0000'}
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")

class ShopOrderCompleteSmsView(View):
    '''
        shop complete sms
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ShopOrderCompleteSmsView, self).dispatch(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        order_id = kwargs.get('order_id')
        try:
            shop = Shop.objects.get(pk=shop_id)
        except:
            return_data = {'data': {},'msg': 'shop id 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        try:
            order = Order.objects.get(pk=order_id, shop=shop)
        except:
            return_data = {'data': {},'msg': 'order id/code 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        if order.order_complete_sms:
            return_data = {'data': {},'msg': '이미 문자 발송 처리된 주문입니다.','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        if not order.order_phone:
            return_data = {'data': {},'msg': '연락처가 없습니다.','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        message=f'[{shop.name_kr}]\n주문번호 [{order.order_no}] 회원님 주문하신거 수령하세요~\n'
        sms_response = send_sms(phone=order.order_phone, message=message)
        SmsLog.objects.create(
            shop=shop,
            shop_name=shop.name_kr,
            phone=order.order_phone,
            message=message
        )
        if sms_response.status_code != 202:
            return_data = {'data': {},'msg': '전송실패','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        order.order_complete_sms = True
        order.save()
        

        return_data = {'data': {}, 'msg': '상태가 변경되었습니다.','resultCd': '0000'}
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")

    
class ShopOrderAlertTestView(View):
    '''
        주문 알림테스트
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ShopOrderAlertTestView, self).dispatch(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        logger = logging.getLogger('my')
        shop_id = kwargs.get('shop_id')
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'shop_order_{shop_id}',
                {
                    'type': 'chat_message',
                    'message_type' : 'ORDER',
                    'title': '* 주문접수 * ',
                    'message': f'주문테스트~~~~'
                }
            )
        except:
            logger.error(traceback.format_exc())
            return_data = {
                'data': {},
                'msg': traceback.format_exc(),
                'resultCd': '0001',
            }

        return_data = {'data': {}, 'msg': 'good','resultCd': '0000'}
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")