from django.conf import settings
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.http import HttpRequest, JsonResponse, HttpResponse
from system_manage.models import Shop, Goods, GoodsOption, GoodsOptionDetail, Checkout, CheckoutDetail, AgencyShop, CheckoutDetailOption
from django.db.models.functions import Concat
from django.db.models import CharField, F, Value as V, Func, Case, When, Prefetch
from django.db import transaction
from django.core.serializers.json import DjangoJSONEncoder

import traceback, json, datetime, uuid

class ShopCheckoutView(View):
    '''
        shop checkout QR
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ShopCheckoutView, self).dispatch(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        try:
            shop = Shop.objects.get(pk=shop_id)
        except:
            return_data = {
                'data': {},
                'msg': 'shop id 오류',
                'resultCd': '0001',
            }
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")

        try:
            agencyId = request.POST.get('agencyId')
            checkoutList = request.POST['checkoutList']
            checkoutList = json.loads(checkoutList)
            finalPrice  = int(request.POST['finalPrice'])

            if not agencyId:
                return_data = json.dumps({'data': {},'msg': f'Agency ID를 넣어주세요.','resultCd': '0001',}, ensure_ascii=False, cls=DjangoJSONEncoder)
                return HttpResponse(return_data, content_type = "application/json")

            try:
                agency = AgencyShop.objects.get(agency_id=agencyId, shop=shop).agency
            except:
                return_data = json.dumps({'data': {},'msg': f'주문 가능한 상점이 아닙니다.','resultCd': '0001',}, ensure_ascii=False, cls=DjangoJSONEncoder)
                return HttpResponse(return_data, content_type = "application/json")
            if finalPrice <= 0:
                return_data = json.dumps({'data': {},'msg': f'0이하 결제금액.','resultCd': '0001',}, ensure_ascii=False, cls=DjangoJSONEncoder)
                return HttpResponse(return_data, content_type = "application/json")

            code = uuid.uuid4().hex
            with transaction.atomic():
                checkout = Checkout.objects.create(
                    agency = agency,
                    shop = shop,
                    code = code,
                    table_no = None,
                    shop_member = None,
                    final_additional=0,
                    final_discount=0
                )
                final = 0
                for i in checkoutList:
                    total = 0
                    goodsId = i['goodsId']
                    goodsName = i['goodsName']
                    quantity = i['quantity']
                    goodsPrice = i['goodsPrice']
                    totalPrice = i['totalPrice']

                    try:
                        goods = Goods.objects.get(pk=goodsId, shop=shop)
                    except:
                        raise ValueError(f'{goodsId} Goods ID error')
                    
                    if goods.sale_price != goodsPrice:
                        raise ValueError(f'{goodsId} Goods prcie error')
                    if quantity <= 0:
                        raise ValueError(f'{goodsId} Goods quantity error')
                    if goods.soldout:
                        raise ValueError(f'{goods.name_kr} Soldout')
                    if goods.stock_flag:
                         if goods.stock < quantity:
                            raise ValueError(f'{goods.name_kr} Out of Stock')
                    
                    checkout_detail = CheckoutDetail.objects.create(
                        checkout = checkout,
                        goods = goods,
                        quantity = quantity,
                        price = goodsPrice,
                        sale_price = goodsPrice,
                        sale_option_price = 0,
                        total_price = total,
                    )
                                        
                    # 옵션있을경우 옵션 유효 체크
                    total = goods.sale_price * quantity
                    option_price = 0

                    if goods.option_flag:
                        checkout_option_bulk_list = []

                        option = i['option']
                        for j in option:
                            optionId = j['optionId']
                            optionName = j['optionName']
                            optionDetailId = j['optionDetail']['optionDetailId']
                            optionDetailName = j['optionDetail']['optionDetailName']
                            optionDetailPrice = int(j['optionDetail']['optionDetailPrice'])
                            try:
                                goods_option_detail = GoodsOptionDetail.objects.get(pk=optionDetailId, goods_option=optionId)
                            except:
                                raise ValueError(f'{goodsId} Goods Option Error')
                            
                            if goods_option_detail.price != optionDetailPrice:
                                raise ValueError(f'{goodsId} Goods Option Price Error')

                            if goods_option_detail.soldout:
                                raise ValueError(f'{goods.name_kr} {goods_option_detail.name_kr} Option Soldout')
                            
                            if goods_option_detail.stock_flag:
                                if goods_option_detail.stock < quantity:
                                    raise ValueError(f'{goods.name_kr} {goods_option_detail.name_kr} Out of Stock')
                            option_price += optionDetailPrice * quantity
                            checkout_option_bulk_list.append(CheckoutDetailOption(checkout_detail=checkout_detail, goods_option_detail=goods_option_detail))
                        total += option_price
                        CheckoutDetailOption.objects.bulk_create(checkout_option_bulk_list)

                        if total != totalPrice:
                            raise ValueError(f'{goodsId} Goods total price Error ...{total}')
                        
                    checkout_detail.price += option_price
                    checkout_detail.sale_option_price = option_price
                    checkout_detail.total_price = total
                    checkout_detail.save()
                    # 총결제금액 합산
                    final += total

                if final != finalPrice:
                    raise ValueError(f'Final Price Error {final}')
                
                checkout.final_price = final
                checkout.save()
                
            return_data = {
                'data': {
                    'shop_id':shop.pk,
                    'checkout_id':checkout.pk,
                    'code':checkout.code,
                    'final_price':checkout.final_price,
                    'final_discount':checkout.final_discount
                },
                'msg': '주문정보 생성완료',
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