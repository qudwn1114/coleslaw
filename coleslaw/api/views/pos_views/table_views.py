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
            paginate_by = 50
            page = int(request.GET.get('page', 1))
            startnum = 0 + (page-1)*paginate_by
            endnum = startnum+paginate_by
            queryset = ShopTable.objects.filter(shop=shop, table_no__gt=0).annotate(
                    membername=Case(
                        When(shop_member=None, then=V('비회원')),
                        default=F('shop_member__membername'), output_field=CharField()
                    ),
                    entryTime=Case(
                        When(entry_time=None, then=None),
                            default=Func(
                            F('entry_time'),
                            V('%m.%d %H:%i'),
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
                'paginate_by': paginate_by,
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
        table_no = int(kwargs.get('table_no'))
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
            
        if shop_table.shop_member or shop_table.entry_time:
            return_data = {'data': {},'msg': '테이블을 비워주세요.','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        try:
            with transaction.atomic():
                shop_table.shop_member = shop_member
                shop_table.total_price = 0
                shop_table.total_additional = 0
                shop_table.total_discount = 0
                shop_table.cart = None
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
        table_no = int(kwargs.get('table_no'))
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
    

class ShopTableDetailView(View):
    '''
        shop table detail api
    '''
    def get(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        table_no = int(kwargs.get('table_no'))
        
        try:
            shop_table = ShopTable.objects.get(table_no=table_no, shop_id=shop_id)
        except:
            return_data = {'data': {},'msg': '테이블 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        data = {}

        if shop_table.cart:
            cart_list = json.loads(shop_table.cart)
        else:
            cart_list = []

        if shop_table.shop_member:
            membername = shop_table.shop_member.membername
            phone = shop_table.shop_member.phone
        else:
            membername = None
            phone = None

        data['membername'] = membername
        data['phone'] = phone
        data['cart_list'] = cart_list
        data['cart_cnt'] = len(cart_list)
        data['cart_total_discount'] = shop_table.total_discount
        data['cart_total_price'] = shop_table.total_price
        data['cart_total_additional'] = shop_table.total_additional

        return_data = {
            'data': data,
            'resultCd': '0000',
            'msg': f'[no.{shop_table.table_no}] 테이블 회원 및 장바구니 정보',
        }

        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")

class ShopTableLogoutView(View):
    '''
        shop 테이블 로그아웃 api
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ShopTableLogoutView, self).dispatch(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        table_no = int(kwargs.get('table_no'))
        try:
            shop_table = ShopTable.objects.get(table_no=table_no, shop_id=shop_id)
        except:
            return_data = {'data': {},'msg': '테이블 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        if not shop_table.shop_member:
            return_data = {'data': {},'msg': '이미 로그아웃 처리된 테이블입니다.','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")

        try:
            with transaction.atomic():
                shop_table.shop_member = None
                shop_table.save()
        except:
            return_data = {'data': {},'msg': '테이블 로그아웃 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")

        
        return_data = {'data': {},'msg': '회원이 로그아웃 되었습니다.','resultCd': '0000'}
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")
    


class ShopMainPosTidView(View):
    '''
        shop main pos tid api
    '''
    def get(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        mainpos_id = int(kwargs.get('mainpos_id'))
        try:
            shop_table = ShopTable.objects.get(table_no=mainpos_id, shop_id=shop_id)
        except:
            return_data = {'data': {},'msg': '테이블 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        if shop_table.table_no > 0:
            return_data = {'data': {},'msg': 'table no 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")

        data = {}
        data['tid'] = shop_table.tid        

        return_data = {
            'data': data,
            'resultCd': '0000',
            'msg': 'tid 정보',
        }
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")