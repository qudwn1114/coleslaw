from django.views.generic import View
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.db.models import CharField, F, Value as V, Func, Case, When, Prefetch, Sum
from django.db import transaction, IntegrityError
from django.core.serializers.json import DjangoJSONEncoder
from system_manage.views.system_manage_views.auth_views import validate_phone
from django.utils import timezone, dateformat
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from system_manage.models import Shop,Checkout, CheckoutDetail, Order, OrderGoods, OrderGoodsOption

import traceback, json, datetime, uuid, logging


class ShopKioskOrderCreateView(View):
    '''
        shop pos 주문생성
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ShopKioskOrderCreateView, self).dispatch(request, *args, **kwargs)
    
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
                        order_type='2', # kiosk
                        order_membername='',
                        order_phone='', 
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

                order.order_name_kr=order_name_kr
                order.order_name_en=order_name_en
                order.save()
            
            return_data = {
                'data': {
                    'shop_id':shop.pk,
                    'order_id':order.pk,
                    'order_name_kr':order_name_kr,
                    'order_name_en':order_name_en,
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