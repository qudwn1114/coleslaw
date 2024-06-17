from django.conf import settings
from django.views.generic import View
from django.urls import reverse
from django.http import HttpRequest, JsonResponse, HttpResponse
from system_manage.models import Shop, Goods, GoodsOption, GoodsOptionDetail, Checkout, CheckoutDetail
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
                'data': [],
                'msg': 'shop id 오류',
                'resultCd': '0001',
            }
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        try:
            agency_name = request.POST['agency_name']
            checkout_list = request.POST['checkout_list']
            checkout_list = json.loads(checkout_list)
            code = uuid.uuid4().hex
            for i in checkout_list:
                goodsId = i['goodsId']
                goodsName = i['goodsName']
                quantity = i['quantity']
                goodsPrice = i['goodsPrice']
                totalPrice = i['totalPrice']

                try:
                    goods = Goods.objects.get(pk=goodsId, shop=shop)
                except:
                    return_data = json.dumps({'data': {},'msg': f'{goodsId} Goods ID 오류','resultCd': '0001',}, ensure_ascii=False, cls=DjangoJSONEncoder)
                    return HttpResponse(return_data, content_type = "application/json")
                
                if goods.sale_price != goodsPrice:
                    return_data = json.dumps({'data': {},'msg': f'{goodsId} Goods 판매가격 불일치','resultCd': '0001',}, ensure_ascii=False, cls=DjangoJSONEncoder)
                    return HttpResponse(return_data, content_type = "application/json")
                
                if goods.sale_price * quantity != totalPrice:
                    return_data = json.dumps({'data': {},'msg': f'{goodsId} Goods total price 불일치','resultCd': '0001',}, ensure_ascii=False, cls=DjangoJSONEncoder)
                    return HttpResponse(return_data, content_type = "application/json")
                # 옵션있을경우

                if goods.option_flag:
                    option = i['option']
                    for j in option:
                        optionId = j['optionId']
                        optionName = j['optionName']
                        optionDetailId = j['optionDetail']['optionDetailId']
                        optionDetailName = j['optionDetail']['optionDetailName']
                        optionDetailPrice = j['optionDetail']['optionDetailPrice']


                

            # try:
            #     with transaction.atomic():
            #         checkout = Checkout.objects.create(
            #             shop = shop,
            #             code = code
            #         )

            #         for i in checkout_list:


            return_data = {
                'data': {},
                'resultCd': '0000',
                'msg': '주문정보 생성완료',
            }
        except:
            return_data = {
                'data': {},
                'msg': traceback.format_exc(),
                'resultCd': '0001',
            }
    
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")