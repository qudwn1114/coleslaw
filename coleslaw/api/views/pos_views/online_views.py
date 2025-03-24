from django.conf import settings
from django.views.generic import View
from django.urls import reverse
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.db.models.functions import Concat
from django.db.models import CharField, F, Value as V, Func, Case, When, Prefetch
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction, IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from system_manage.models import Shop, ShopTable, Goods
from collections import Counter
import traceback, json    

class ShopOnlineEnterView(View):
    '''
        온라인 입장처리
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ShopOnlineEnterView, self).dispatch(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        mainpos_id = int(request.POST['mainpos_id'])
        code_list = request.POST['code_list']
        try:
            shop = Shop.objects.get(pk=shop_id)
        except:
            return_data = {'data': {},'msg': 'shop 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        try:
            shop_table = ShopTable.objects.get(table_no=mainpos_id, shop=shop, pos=shop.pos)
        except:
            return_data = {'data': {},'msg': '테이블 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        code_list = code_list.strip().rstrip(',')
        code_list = code_list.split(',')
        code_dict = Counter(code_list)
        if code_dict:
            cart_list = []
            cart_total_price = 0
            for code, num in code_dict.items():
                cart={}
                # code, num
                try:
                    goods = Goods.objects.get(code=code)
                    cart['goodsId'] = goods.pk
                    cart['name_kr'] = goods.name_kr
                    cart['price'] = goods.sale_price
                    cart['discount'] = 0
                    cart['quantity'] = int(num)
                    cart['optionName'] = ''
                    cart['optionPrice'] = 0
                    cart['optionList'] = []
                    cart_list.append(cart)
                    cart_total_price += goods.sale_price
                except:
                    return_data = {'data': {},'msg': f'{code} 온라인 상품등록이 필요합니다.','resultCd': '0001'}
                    return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
                    return HttpResponse(return_data, content_type = "application/json")
        else:
            return_data = {'data': {},'msg': f'{code_list} // {code_dict}','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")

        cart_list = json.dumps(cart_list, ensure_ascii=False)
        shop_table.cart = cart_list
        shop_table.total_discount = 0
        shop_table.total_additional = 0
        shop_table.total_price = cart_total_price
        shop_table.save()
        
        return_data = {'data': {"table_no":shop_table.table_no},'msg': '결제준비 완료.','resultCd': '0000'}
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")