from django.views.generic import View
from django.http import HttpRequest, JsonResponse, HttpResponse
from system_manage.models import Shop,Checkout, CheckoutDetail, Order, OrderGoods
from django.db.models import CharField, F, Value as V, Func, Case, When, Prefetch, Sum
from django.db import transaction, IntegrityError
from django.core.serializers.json import DjangoJSONEncoder
from system_manage.views.system_manage_views.auth_views import validate_phone
from django.utils import timezone, dateformat
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import traceback, json, datetime, uuid

class ShopOrderCreateView(View):
    '''
        shop checkout
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
        
        membername = request.POST['membername'].strip()
        phone = request.POST['phone']

        if not validate_phone(phone):
            return_data = {'data': {},'msg': '유효하지 않은 전화번호 형식입니다.','resultCd': '0001'}
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
                order_name = ''
                order_goods_bulk_list = []
                for i in checkout.checkout_detail.all():
                    if order_name == '':
                        if total_quantity == 1:
                            order_name = f"{i.goods.name} {total_quantity}개"
                        else:
                            order_name = f"{i.goods.name} 외 {total_quantity-1}개"

                    option_price = 0
                    if i.checkout_detail_option.all().exists():
                        option = []
                        
                        for j in i.checkout_detail_option.all():
                            option.append(f"{j.goods_option_detail.goods_option.name} : {j.goods_option_detail.name}")
                            option_price += j.goods_option_detail.price
                        option = ' / '.join(option)
                    else:
                        option = None

                    if i.goods.soldout:
                        raise ValueError(f"{i.goods.name} 상품이 판매 중단되었습니다.")
                    
                    order_goods = OrderGoods(order=order, goods=i.goods, price=i.price, name=i.goods.name, quantity=i.quantity, option=option, option_price=option_price, total_price=(i.price+option_price)*i.quantity)
                    order_goods_bulk_list.append(order_goods)

                OrderGoods.objects.bulk_create(order_goods_bulk_list)
                order.order_name=order_name
                order.save()
                    
            return_data = {
                'data': {
                    'shop_id':shop.pk,
                    'order_id':order.pk,
                    'order_name':order_name,
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
        
        try:
            order = Order.objects.get(pk=order_id, order_code=code)
        except:
            return_data = {'data': {},'msg': 'order id/code 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        order.status = '1'
        order.save()

        return_data = {
            'data': {
                'shop_name':shop.name,
                'order_id':order.pk,
                'order_no':order.order_no,
                'order_membername':order.order_membername,
                'order_phone':order.order_phone
            },
            'msg': '결제완료',
            'resultCd': '0000',
        }

        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")