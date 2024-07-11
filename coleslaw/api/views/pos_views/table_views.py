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
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from system_manage.models import Shop, ShopTable, ShopMember, ShopTableLog
from system_manage.views.system_manage_views.auth_views import validate_phone


import traceback, json, datetime

class ShopTableListView(View):
    '''
        shop table list api
    '''
    def get(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        try:
            shop = Shop.objects.get(pk=shop_id)
        except:
            return_data = {'data': {},'msg': 'shop id 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        try:
            page = int(request.GET.get('page', 1))
            startnum = 0 + (page-1)*30
            endnum = startnum+30
            queryset = ShopTable.objects.filter(shop=shop).exclude(table_no=0).annotate(
                    membername=Case(
                        When(shop_member=None, then=V('비회원')),
                        default=F('shop_member__membername'), output_field=CharField()
                    ),
                    entryTime=Case(
                        When(entry_time=None, then=None),
                            default=Func(
                            F('entry_time'),
                            V('%y.%m.%d %H:%i'),
                            function='DATE_FORMAT',
                            output_field=CharField()
                        )
                    ),
                ).values(
                    'table_no',
                    'name',
                    'entry_time',
                    'membername',
                    'total_price',
                    'entryTime',
                ).order_by('table_no')

            return_data = {
                'data': list(queryset[startnum:endnum]),
                'resultCd': '0000',
                'msg': '가맹점 테이블 리스트',
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
    

class ShopTableAssignView(View):
    '''
        shop 테이블 배정
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ShopTableAssignView, self).dispatch(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        table_no = kwargs.get('table_no')
        try:
            shop_table = ShopTable.objects.get(table_no=table_no, shop_id=shop_id)
        except:
            return_data = {'data': {},'msg': '테이블 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        shop_member_id = int(request.POST['shop_member_id'])
        if shop_member_id == 0:
            shop_member = None
        else:
            try:
                shop_member = ShopMember.objects.get(pk=shop_member_id, shop=shop_table.shop)
            except:
                return_data = {'data': {},'msg': '사용자 오류','resultCd': '0001'}
                return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
                return HttpResponse(return_data, content_type = "application/json")
            
        if shop_table.shop_member or shop_table.entry_time or shop_table.cart:
            return_data = {'data': {},'msg': '테이블을 비워주세요.','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        try:
            with transaction.atomic():
                shop_table.shop_member = shop_member
                shop_table.total_price = 0
                shop_table.entry_time = timezone.now()
                shop_table.save()

                ShopTableLog.objects.create(
                    shop_table=shop_table,
                    shop_member=shop_member,
                    status=False
                )
        except:
            return_data = {'data': {},'msg': traceback.format_exc(),'resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        return_data = {'data': {},'msg': '테이블 배정 되었습니다.','resultCd': '0000'}
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")

class ShopTableExitView(View):
    '''
        shop 테이블 퇴장
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ShopTableExitView, self).dispatch(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        table_no = kwargs.get('table_no')
        try:
            shop_table = ShopTable.objects.get(table_no=table_no, shop_id=shop_id)
        except:
            return_data = {'data': {},'msg': '테이블 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
            
        try:
            with transaction.atomic():
                shop_table.shop_member = None
                shop_table.entry_time = None
                shop_table.cart = None
                shop_table.total_price = 0
                shop_table.save()
                ShopTableLog.objects.create(
                    shop_table=shop_table,
                    shop_member=shop_table.shop_member,
                    status=True
                )
        except:
            return_data = {'data': {},'msg': traceback.format_exc(),'resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        

        return_data = {'data': {},'msg': '테이블이 정리 되었습니다.','resultCd': '0000'}
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")