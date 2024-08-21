from django.views.generic import View
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.db.models import CharField, F, Value as V, Func, Case, When, Prefetch, Sum
from django.db.models.functions import Coalesce
from django.db import transaction, IntegrityError
from django.core.serializers.json import DjangoJSONEncoder
from system_manage.views.system_manage_views.auth_views import validate_phone
from django.utils import timezone, dateformat
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from system_manage.models import Shop,Checkout, CheckoutDetail, Order, OrderGoods, OrderGoodsOption, OrderPayment, ShopMember, ShopTable, Goods

import traceback, json, datetime, uuid, logging


class ShopPosOrderListView(View):
    '''
        pos order list
    '''
    def get(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        paginate_by = 50
        page = int(request.GET.get('page', 1))

        start_date = request.GET.get('start_date', '')
        end_date = request.GET.get('end_date', '')

        filter_dict = {}
        
        if start_date and end_date:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
            end_date = datetime.datetime.combine(end_date, datetime.time.max)
            filter_dict['created_at__lte'] = end_date
            filter_dict['created_at__gte'] = start_date
        else:
            date = timezone.now().date()
            filter_dict['date'] = date

        startnum = 0 + (page-1)*paginate_by
        endnum = startnum+paginate_by
    
        try:
            shop = Shop.objects.get(pk=shop_id)
        except:
            return_data = {'data': {},'msg': 'shop id 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        filter_dict['shop'] = shop
        try:
            queryset = Order.objects.filter(**filter_dict).exclude(status='0').annotate(
                orderStatus=Case(
                    When(status='0', then=V('결제대기')),
                    When(status='1', then=V('결제완료')),
                    When(status='2', then=V('취소')),
                    When(status='3', then=V('준비중')),
                    When(status='4', then=V('주문완료')),
                    When(status='5', then=V('수령완료')),
                    When(status='6', then=V('부분취소')),
                    default=V('결제완료'), output_field=CharField()
                ),
                paymentMethod = Case(
                    When(payment_method='0', then=V('키드결제')),
                    When(payment_method='1', then=V('현금결제')),
                    When(payment_method='2', then=V('분할결제')),
                    default=V('키드결제'), output_field=CharField()
                ),
                createdAt=Func(
                    F('created_at'),
                    V('%y.%m.%d %H:%i'),
                    function='DATE_FORMAT',
                    output_field=CharField()
                )
            ).values(
                'id',
                'order_no',
                'orderStatus',
                'final_price',
                'order_name_kr',
                'status',
                'paymentMethod',
                'createdAt'
            ).order_by('-id')

            return_data = {
                'data': list(queryset[startnum:endnum]),
                'paginate_by': paginate_by,
                'resultCd': '0000',
                'msg': '가맹점 주문 리스트',
                'totalCnt' : queryset.count()
            }
        except:
            print(traceback.format_exc())
            return_data = {
                'data': [],
                'msg': '오류!',
                'resultCd': '0001',
            }
    
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")
    

class ShopPosOrderDetailView(View):
    '''
        pos order detail
    '''
    def get(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        order_id = kwargs.get('order_id')
        try:
            order = Order.objects.get(pk=order_id, shop_id=shop_id)
        except:
            return_data = {'data': {},'msg': '주문 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        data = {}

        if order.shop_member:
            data['shop_member_id'] = order.shop_member.pk
            data['membername'] = order.shop_member.membername
        else:
            data['shop_member_id'] = None
            data['membername'] = None      

        if order.payment_method == '0':
            data['order_payment_method'] = '카드'
        elif order.payment_method == '1':
            data['order_payment_method'] = '현금'
        elif order.payment_method == '2':
            data['order_payment_method'] = '카드/현금'

        if order.status == '1':
            data['orderStatus'] = '결제완료'
        elif order.status == '2':
            data['orderStatus'] = '취소'
        elif order.status == '3':
            data['orderStatus'] = '준비중'    
        elif order.status == '4':
            data['orderStatus'] = '주문완료'
        elif order.status == '5':
            data['orderStatus'] = '수령완료'
        elif order.status == '6':
            data['orderStatus'] = '부분취소'

        data['status'] = order.status
        data['order_code'] = order.order_code
        data['order_no'] = order.order_no
        data['order_name_kr'] = order.order_name_kr
        data['final_price'] = order.final_price
        data['final_discount'] = order.final_discount
        data['final_additional'] = order.final_additional
        data['createdAt'] = order.created_at.strftime('%Y년 %m월 %d일 %H:%M')
        order_detail = order.order_goods.all().values(
            'id',
            'name_kr',
            'quantity',
            'total_price'
        )        
        for i in order_detail:
            i['option_detail'] = list(OrderGoodsOption.objects.filter(pk=i['id']).annotate(
                name_kr = F('goods_option_detail__name_kr'),
            ).values('name_kr'))
        data['order_detail'] = list(order_detail)

        order_payment = order.order_payment.all().annotate(
            paymentMethod=Case(
                When(payment_method='0', then=V('카드')),
                When(payment_method='1', then=V('현금')),
                default=V('카드'), output_field=CharField()
            ),
            approvalDate = F('tranDate'),                            
            cancelledAt=Case(
                When(cancelled_at=None, then=None),
                default=Func(
                    F('cancelled_at'),
                    V('%y.%m.%d %H:%i'),
                    function='DATE_FORMAT',
                    output_field=CharField()
                )
            ),
            createdAt=Func(
                F('created_at'),
                V('%y.%m.%d %H:%i'),
                function='DATE_FORMAT',
                output_field=CharField()
            )
        ).order_by('id').values(
            'id',
            'paymentMethod',
            'payment_method',
            'tid',
            'status',
            'issueCompanyName',
            'approvalDate',
            'approvalNumber',
            'cardNo',
            'amount',
            'taxAmount',
            'cashResceiptStatus',
            'cashReceiptcardNo',
            'cashReceiptApprovalNumber',
            'cancelledAt',
            'createdAt'
        )
        data['order_payment'] = list(order_payment)

        return_data = {
            'data': data,
            'resultCd': '0000',
            'msg': '주문상세 정보',
        }
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")


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
                        mainpos_id=checkout.mainpos_id,
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
                
                after_payment_cart = {}

                order_name_kr = ''
                order_name_en = ''
                if checkout.checkout_detail.all().exists():
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
                        
                        # # 결제후 상품
                        if i.goods.after_payment_goods:
                            after_payment_goods_id = str(i.goods.after_payment_goods)
                            if after_payment_goods_id in after_payment_cart:
                                after_payment_cart[f'{after_payment_goods_id}'] += i.quantity
                            else:
                                after_payment_cart[f'{after_payment_goods_id}'] = i.quantity

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
                else:
                    order_name_kr = '추가요금'
                    order_name_en = 'Additional Fee'

                # 추가 상품저장
                if after_payment_cart:
                    order.after_payment_cart = json.dumps(after_payment_cart, ensure_ascii=False)

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
    

class ShopPosCheckoutOrderDetailView(View):
    '''
        pos checkout order detail api
    '''
    def get(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        order_id = kwargs.get('order_id')
        code = kwargs.get('code')

        try:
            shop = Shop.objects.get(pk=shop_id)
        except:
            return_data = {'data': {},'msg': 'shop id 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")

        try:
            order = Order.objects.get(pk=order_id, shop=shop, order_code=code)
        except:
            return_data = {'data': {},'msg': 'order data 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        data = {}
        if order.shop_member:
            data['shop_member_id'] = order.shop_member.pk
            data['membername'] = order.shop_member.membername
        else:
            data['shop_member_id'] = None
            data['membername'] = None
        
        data['final_price'] = order.final_price
        data['final_discount'] = order.final_discount
        data['final_additional'] = order.final_additional
        data['payment_price'] = order.payment_price
        data['left_price'] = order.final_price - order.payment_price
        order_detail = order.order_goods.all().values(
            'id',
            'name_kr',
            'quantity',
            'total_price'
        )        
        for i in order_detail:
            i['option_detail'] = list(OrderGoodsOption.objects.filter(pk=i['id']).annotate(
                name_kr = F('goods_option_detail__name_kr'),
            ).values('name_kr'))
        data['order_detail'] = list(order_detail)

        return_data = {
            'data': data,
            'resultCd': '0000',
            'msg': f'주문 상세정보',
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
            if paymentMethod == 'CARD':
                paymentMethod = '0'
                payment_method = '0'
            elif paymentMethod == 'CASH':
                paymentMethod = '1'
                payment_method = '1'
            else:
                return_data = {'data': {},'msg': '옳바르지 않은 payment method','resultCd': '0001'}
                return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
                return HttpResponse(return_data, content_type = "application/json")
            
            tid = request.POST.get('tid', '')
            installment = request.POST.get('installment', '0')
            amount = request.POST.get('amount', '')
            if not amount:
                amount = 0
            else:
                amount = int(amount)
            taxAmount = request.POST.get('amountTax', '')
            if not taxAmount:
                taxAmount = 0
            else:
                taxAmount = int(taxAmount)

            approvalNumber = request.POST.get('approvalNumber', '')
            approvalDate = request.POST.get('approvalDate', '')
            if approvalDate:
                tranDate = approvalDate[:6]
                tranTime = approvalDate[6:]
            else:
                tranDate = timezone.now().strftime("%y%m%d")
                tranTime = timezone.now().strftime('%H%M')

            cardNo = request.POST.get('maskingCardNumber', '') #마스킹 되어진 카드번호

            issueCompanyNo = request.POST.get('issuerCode', '') #발급사코드
            issueCompanyName = request.POST.get('issuer', '') #발금사명
            acqCompanyNo = request.POST.get('acquirerCode', '') #매입사코드
            acqCompanyName = request.POST.get('acquirer', '') #매입사명


            additionalInfo = request.POST.get('additionalInfo', '')
            posEntryMode = request.POST.get('posEntryMode', '')
        
            try:
                order = Order.objects.get(pk=order_id, order_code=code)
            except:
                return_data = {'data': {},'msg': 'order id/code 오류','resultCd': '0001'}
                return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
                return HttpResponse(return_data, content_type = "application/json")
            
            payment_price = order.payment_price + amount
            left_price = order.final_price - payment_price
            
            order.payment_price = payment_price
            if not order.payment_method:
                order.payment_method = paymentMethod
            else:
                payment_method_list = list(order.order_payment.all().values_list('payment_method', flat=True))
                payment_method_list.append(payment_method)
                payment_method_list = list(set(payment_method_list))
                if len(payment_method_list) > 1:
                    paymentMethod = '2'
                    order.payment_method = paymentMethod

            order.status = '1'
            order.save()

            order_payment = OrderPayment.objects.create(
                order = order,

                status=True,
                payment_method=payment_method,

                tid = tid,
                installment=installment,
                approvalNumber = approvalNumber,
                tranDate = tranDate,
                tranTime = tranTime,
                cardNo = cardNo,
                issueCompanyNo=issueCompanyNo,
                issueCompanyName=issueCompanyName,
                acqCompanyNo=acqCompanyNo,
                acqCompanyName=acqCompanyName,
                additionalInfo = additionalInfo,
                posEntryMode = posEntryMode,
                amount = amount,
                taxAmount = taxAmount,
            )

            if order.order_type == '2':
                receipt_data = {}
                receipt_data['order_payment_id'] = order_payment.pk

                try:
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        f'shop_entry_{shop_id}',
                        {
                            'type': 'chat_message',
                            'message_type' : 'KIOSK',
                            'title': '* KIOSK 주문접수 *',
                            'message': receipt_data
                        }
                    )
                except:
                    pass


            # 재고관리
            if left_price <= 0:
                try:
                    shop_table = ShopTable.objects.get(shop=shop, table_no=order.table_no)
                    shop_table.cart = None
                    shop_table.total_price = 0
                    shop_table.total_discount = 0
                    shop_table.total_additional = 0
                    shop_table.save()

                    if shop_table.table_no > 0:
                        if order.after_payment_cart:
                            after_payment_cart = json.loads(order.after_payment_cart)
                            cart_list = []
                            after_payment_cart_total_price = 0
                            for k, v in after_payment_cart.items():
                                cart={}
                                try:
                                    after_payment_goods = Goods.objects.get(pk=k, shop=shop)
                                    cart['goodsId'] = after_payment_goods.pk
                                    cart['name_kr'] = after_payment_goods.name_kr
                                    cart['price'] = after_payment_goods.sale_price
                                    cart['discount'] = 0
                                    cart['quantity'] = int(v)
                                    cart['optionName'] = ''
                                    cart['optionPrice'] = 0
                                    cart['optionList'] = []
                                    cart_list.append(cart)
                                    after_payment_cart_total_price += after_payment_goods.sale_price
                                except:
                                    pass
                            cart_list = json.dumps(cart_list, ensure_ascii=False)
                            shop_table.cart = cart_list
                            shop_table.total_price = after_payment_cart_total_price
                            shop_table.save()
                except:
                    pass

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
                    'order_payment_id': order_payment.pk,
                    'order_code':order.order_code,
                    'left_price':left_price
                },
                'msg': '결제완료',
                'resultCd': '0000',
            }
            try:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'shop_{shop_id}_{order.mainpos_id}',
                    {
                        'type': 'chat_message',
                        'message_type' : 'COMPLETE',
                        'title': 'POS 듀얼 모니터',
                        'message': 'CLEAR'
                    }
                )
            except:
                pass

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


class ShopPosOrderPaymentCancelView(View):
    '''
        shop pos order cancel
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ShopPosOrderPaymentCancelView, self).dispatch(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        order_payment_id = kwargs.get('order_payment_id')
        try:
            order_payment = OrderPayment.objects.get(pk=order_payment_id, order__shop_id=shop_id)
        except:
            return_data = {'data': {},'msg': 'order payment id 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        order_payment.cancelled_at = timezone.now()
        order_payment.status = False
        order_payment.save()

        order = order_payment.order
        total_cancelled = OrderPayment.objects.filter(order=order, status=False).aggregate(sum=Coalesce(Sum('amount'), 0)).get('sum')
        if total_cancelled ==order.payment_price:
            order.status = '2'
        else:
            order.status = '6'
        order.save()

        return_data = {'data': {
            'order_id':order_payment.order.pk
        },'msg': '취소되었습니다.','resultCd': '0000'}
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")