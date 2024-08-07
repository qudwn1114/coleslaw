from django.views.generic import View
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from system_manage.models import Shop, ShopTable, SubCategory

import json

class ShopPosCatgoryFixView(View):
    '''
        상품담기
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ShopPosCatgoryFixView, self).dispatch(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        mainpos_id = int(kwargs.get('mainpos_id'))
        try:
            shop = Shop.objects.get(pk=shop_id)
        except:
            return_data = {'data': {},'msg': 'shop id 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        try:
            shop_table = ShopTable.objects.get(table_no=mainpos_id, shop=shop)
        except:
            return_data = {'data': {},'msg': '테이블 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        if shop_table.table_no > 0:
            return_data = {'data': {},'msg': 'POS 홈에만 적용 가능합니다.','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        sub_category_id = request.POST['sub_category_id']
        try:
            sub_category = SubCategory.objects.get(pk=sub_category_id)
        except:
            return_data = {'data': {},'msg': '카테고리 ID 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        shop_table.fixed_category_id = sub_category
        shop_table.save()

        return_data = {'data': {},'msg': '고정되었습니다.','resultCd': '0000'}
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")
        
