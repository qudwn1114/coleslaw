from django.conf import settings
from django.views.generic import View
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
        shop checkout
    '''
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
            agencyId = request.POST.get('agencyId', None)
            checkoutList = request.POST['checkoutList']
            checkoutList = json.loads(checkoutList)
            finalPrice  = int(request.POST['finalPrice'])

            if agencyId:
                try:
                    agency = AgencyShop.objects.get(agency_id=agencyId, shop=shop).agency
                except:
                    return_data = json.dumps({'data': {},'msg': f'주문 가능한 상점이 아닙니다.','resultCd': '0001',}, ensure_ascii=False, cls=DjangoJSONEncoder)
                    return HttpResponse(return_data, content_type = "application/json")
            else:
                agency = None
            if finalPrice <= 0:
                return_data = json.dumps({'data': {},'msg': f'0이하 결제금액.','resultCd': '0001',}, ensure_ascii=False, cls=DjangoJSONEncoder)
                return HttpResponse(return_data, content_type = "application/json")

            code = uuid.uuid4().hex
            with transaction.atomic():
                checkout = Checkout.objects.create(
                    agency = agency,
                    shop = shop,
                    code = code
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
                    
                    checkout_detail = CheckoutDetail.objects.create(
                        checkout = checkout,
                        goods = goods,
                        quantity = quantity,
                        price = goodsPrice,
                        total_price = total
                    )
                                        
                    # 옵션있을경우 옵션 유효 체크
                    total = goods.sale_price * quantity
                    if goods.option_flag:
                        checkout_option_bulk_list = []

                        option = i['option']
                        for j in option:
                            optionId = j['optionId']
                            optionName = j['optionName']
                            optionDetailId = j['optionDetail']['optionDetailId']
                            optionDetailName = j['optionDetail']['optionDetailName']
                            optionDetailPrice = j['optionDetail']['optionDetailPrice']
                            try:
                                goods_option_detail = GoodsOptionDetail.objects.get(pk=optionDetailId, goods_option=optionId)
                            except:
                                raise ValueError(f'{goodsId} Goods Option Error')
                            
                            if goods_option_detail.price != optionDetailPrice:
                                raise ValueError(f'{goodsId} Goods Option Price Error')
                            total += optionDetailPrice

                            checkout_option_bulk_list.append(CheckoutDetailOption(checkout_detail=checkout_detail, goods_option_detail=goods_option_detail))

                        CheckoutDetailOption.objects.bulk_create(checkout_option_bulk_list)

                    if  total != totalPrice:
                        raise ValueError(f'{goodsId} Goods total price Error')
                      
                    checkout_detail.total_price = total
                    checkout_detail.save()
                    
                    # 총결제금액 합산
                    final += total

                if final != finalPrice:
                    raise ValueError(f'Final Price Error')
                
                checkout.final_price = final
                checkout.save()
                    
            return_data = {
                'data': {
                    'shop':shop.pk,
                    'code':checkout.code,
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