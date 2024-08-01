from django.views.generic import View
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.db.models import CharField, F, Value as V, Func, Case, When, Prefetch, Sum
from django.db import transaction, IntegrityError
from django.core.serializers.json import DjangoJSONEncoder
from system_manage.views.system_manage_views.auth_views import validate_phone
from django.utils import timezone, dateformat
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from system_manage.models import Shop,Checkout, CheckoutDetail, Order, OrderGoods, OrderGoodsOption, OrderPayment, ShopMember

import traceback, json, datetime, uuid, logging

class ShopPosOrderCreateView(View):
    '''
        shop pos 주문생성
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ShopPosOrderCreateView, self).dispatch(request, *args, **kwargs)
    
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
        
        shop_member_id = int(request.POST['shop_member_id'])
        if shop_member_id == 0:
            shop_member_id = None
            shop_member = None
        else:
            try:
                shop_member = ShopMember.objects.get(pk=shop_member_id, shop=shop)
            except:
                return_data = {'data': {},'msg': 'shop member id 오류','resultCd': '0001'}
                return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
                return HttpResponse(return_data, content_type = "application/json")
        
        if checkout.shop_member:
            if shop_member != checkout.shop_member:
                return_data = {'data': {},'msg': 'shop member 변경 오류','resultCd': '0001'}
                return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
                return HttpResponse(return_data, content_type = "application/json")
        else:
            checkout.shop_member = shop_member
            checkout.save()
        
        # 한시간
        if (timezone.now() - checkout.created_at).seconds >= 3600:
            return_data = {'data': {},'msg': '주문 시간초과.. 다시 주문해주세요.','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        total_quantity = checkout.checkout_detail.all().aggregate(sum=Sum('quantity')).get('sum')
        try:
            order_code = uuid.uuid4().hex
            order_no = Order.objects.filter(shop=shop ,date=timezone.now().date()).count() + 1
            with transaction.atomic():
                try:
                    order = Order.objects.create(
                        agency=checkout.agency,
                        shop=shop,
                        table_no=checkout.table_no,
                        shop_member=shop_member,
                        order_type='0',
                        order_membername='',
                        order_phone='', 
                        status='0', 
                        order_code = order_code,
                        order_no=order_no,
                        final_price = checkout.final_price,
                        final_additional = checkout.final_additional,
                        final_discount=checkout.final_discount
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

                    order_goods = OrderGoods.objects.create(
                        order=order, 
                        goods=i.goods,
                        price=i.price, 
                        name_kr=i.goods.name_kr, 
                        name_en=i.goods.name_en,
                        quantity=i.quantity,
                        option_kr=None, 
                        option_en=None, 
                        option_price=0, 
                        total_price=i.price*i.quantity
                    )

                    option_price = 0
                    if i.checkout_detail_option.all().exists():
                        option_kr = [] 
                        option_en = [] 
                        order_goods_option_bulk_list = []
                        for j in i.checkout_detail_option.all():
                            if j.goods_option_detail.soldout:
                                raise ValueError(f"{i.goods.name_kr} {j.goods_option_detail.name_kr} Option Soldout")
                            
                            if j.goods_option_detail.stock_flag:
                                if j.goods_option_detail.stock < i.quantity:
                                    raise ValueError(f'{i.goods.name_kr} {j.goods_option_detail.name_kr} Out of Stock')
                            
                            option_kr.append(f"{j.goods_option_detail.goods_option.name_kr} : {j.goods_option_detail.name_kr}")
                            option_en.append(f"{j.goods_option_detail.goods_option.name_en} : {j.goods_option_detail.name_en}")
                            option_price += j.goods_option_detail.price

                            order_goods_option_bulk_list.append(OrderGoodsOption(order_goods=order_goods, goods_option_detail=j.goods_option_detail))

                        OrderGoodsOption.objects.bulk_create(order_goods_option_bulk_list)
                        option_kr = ' / '.join(option_kr)
                        option_en = ' / '.join(option_en)
                        order_goods.option_kr = option_kr
                        order_goods.option_en = option_en
                        order_goods.option_price = option_price
                        order_goods.total_price += option_price
                        order_goods.save()

                order.order_name_kr=order_name_kr
                order.order_name_en=order_name_en
                order.save()
            
            if shop_member:
                membername = shop_member.membername
            else:
                membername = None
            return_data = {
                'data': {
                    'shop_id':shop.pk,
                    'order_id':order.pk,
                    'order_name_kr':order_name_kr,
                    'order_name_en':order_name_en,
                    'order_code':order_code,
                    'final_price':checkout.final_price,
                    'final_additional':checkout.final_additional,
                    'final_discount':checkout.final_discount,
                    'shop_member_id' : shop_member_id,
                    'membername' : membername
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
    



class ShopPosOrderCompleteView(View):
    '''
        shop pos order complete
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ShopPosOrderCompleteView, self).dispatch(request, *args, **kwargs)
    
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
        try:
            paymentMethod = request.POST.get('paymentMethod', '')
            if paymentMethod not in ['CARD', 'CASH']:
                return_data = {'data': {},'msg': '옳바르지 않은 payment method','resultCd': '0001'}
                return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
                return HttpResponse(return_data, content_type = "application/json")
            
            tid = request.POST.get('tid', '')
            approvalNumber = request.POST.get('approvalNumber', '')
            approvalDate = request.POST.get('approvalDate', '')
            maskingCardNumber = request.POST.get('maskingCardNumber', '')
            additionalInfo = request.POST.get('additionalInfo', '')
            posEntryMode = request.POST.get('posEntryMode', '')

            amount = request.POST.get('amount', '')
            if not amount:
                amount = 0
            else:
                amount = int(amount)
            taxAmount = request.POST.get('taxAmount', '')
            if not taxAmount:
                taxAmount = 0
            else:
                taxAmount = int(taxAmount)

        
            try:
                order = Order.objects.get(pk=order_id, order_code=code)
            except:
                return_data = {'data': {},'msg': 'order id/code 오류','resultCd': '0001'}
                return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
                return HttpResponse(return_data, content_type = "application/json")
            
            payment_price = order.payment_price + amount
            left_price = order.final_price - payment_price
            
            order.payment_price = payment_price
            if not paymentMethod:
                order.payment_method = paymentMethod
            order.status = '1'
            order.save()

            OrderPayment.objects.create(
                order = order,
                tid = tid,
                approvalNumber = approvalNumber,
                approvalDate = approvalDate,
                maskingCardNumber = maskingCardNumber,
                additionalInfo = additionalInfo,
                posEntryMode = posEntryMode,
                amount = amount,
                taxAmount = taxAmount,
            )

            # 재고관리
            if left_price == 0:
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

            return_data = {
                'data': {
                    'order_id':order.pk,
                    'order_code':order.order_code,
                    'left_price':left_price
                },
                'msg': '결제완료',
                'resultCd': '0000',
            }
        except:
            logger.error(str(dict(request.POST)))
            logger.error(traceback.format_exc())
            return_data = {
                'data': {},
                'msg': traceback.format_exc(),
                'resultCd': '0001',
            }

        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")
