from django.views.generic import View
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.db.models import CharField, F, Value as V, Func, Case, When, Prefetch, Sum
from django.db import transaction, IntegrityError
from django.core.serializers.json import DjangoJSONEncoder
from system_manage.views.system_manage_views.auth_views import validate_phone
from django.utils import timezone, dateformat
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from system_manage.models import ShopTable, Goods, GoodsOption, GoodsOptionDetail
from api.views.sms_views.sms_views import send_sms

import traceback, json, datetime, uuid, logging

class AddShopTableView(View):
    '''
        상품담기
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(AddShopTableView, self).dispatch(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        table_no = kwargs.get('table_no')
        try:
            shop_table = ShopTable.objects.get(table_no=table_no, shop_id=shop_id)
        except:
            return_data = {'data': {},'msg': '테이블 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        goods_id = request.POST['goods_id']
        quantity = int(request.POST['quantity'])
        optionList = request.POST['optionList']
        optionList = json.loads(optionList)
        optionList.sort()

        if quantity <= 0:
            return_data = {'data': {},'msg': 'quantity must larger than 0','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")

        try:
            goods = Goods.objects.get(pk=goods_id, shop=shop_table.shop)
        except:
            return_data = {'data': {},'msg': 'Goods ID 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        if goods.soldout:
            return_data = {'data': {},'msg': '품절 상품입니다.','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        optionName = ''
        optionPrice = 0
        for i in optionList:
            try:
                goods_option_detail = GoodsOptionDetail.objects.get(pk=i, goods_option__goods=goods)
            except:
                return_data = {'data': {},'msg': 'Goods Option Error','resultCd': '0001'}
                return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
                return HttpResponse(return_data, content_type = "application/json")
            if goods_option_detail.soldout:
                return_data = {'data': {},'msg': f'옵션 {goods_option_detail.name} 품절','resultCd': '0001'}
                return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
                return HttpResponse(return_data, content_type = "application/json")
            
            optionName += f'{goods_option_detail.name} / '
            optionPrice += goods_option_detail.price
            
        if optionName:
            optionName = optionName.strip().rstrip('/')

        if shop_table.cart:
            is_new = True
            cart_list = json.loads(shop_table.cart)
            addtional_price = 0
            for i in cart_list:
                if i['goodsId'] == goods.pk:
                    # 이미 담긴 상품일때
                    if i['optionList'] == optionList:
                        is_new = False
                        i['quantity'] += quantity
                        addtional_price = quantity * i['price']
                        break

            if is_new:
                data={}
                data['goodsId'] = goods.pk
                data['name'] = goods.name
                data['price'] = goods.price
                data['quantity'] = quantity
                data['optionName'] = optionName
                data['optionPrice'] = optionPrice
                data['optionList'] = optionList
                cart_list.append(data)
                addtional_price = quantity * goods.price
            
            cart_list = json.dumps(cart_list, ensure_ascii=False)
            shop_table.cart = cart_list
            shop_table.total_price += addtional_price
            shop_table.save()

            return_data = {'data': {},'msg': '상품이 추가 되었습니다.','resultCd': '0000'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")

            
        else:
            data={}
            data['goodsId'] = goods.pk
            data['name'] = goods.name
            data['price'] = goods.price
            data['quantity'] = quantity
            data['optionName'] = optionName
            data['optionPrice'] = optionPrice
            data['optionList'] = optionList
            cart_list = json.dumps([data], ensure_ascii=False)

            shop_table.total_price = goods.price * quantity
            shop_table.cart = cart_list
            shop_table.save()
            
            return_data = {'data': {},'msg': '상품이 담겼습니다.','resultCd': '0000'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")