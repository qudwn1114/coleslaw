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

from system_manage.models import Shop, ShopTable
from collections import Counter
import traceback, json, ast    

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
            shop_table = ShopTable.objects.get(table_no=mainpos_id, shop_id=shop_id)
        except:
            return_data = {'data': {},'msg': '테이블 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        code_list = ast.literal_eval(code_list)
        code_dict = Counter(code_list)
        for code, num in code_dict.items():
            # code, num
            print(code, num)
        
        return_data = {'data': {},'msg': '결제준비 완료.','resultCd': '0000'}
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")