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

from system_manage.models import Shop, ShopTable, ShopMember, ShopTableLog, Goods
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
            
            now_time = timezone.now()
            for i in queryset:
                if shop.table_time > 0:
                    if i['entry_time']:
                        end_time = i['entry_time'] + datetime.timedelta(minutes=shop.table_time)
                        if now_time > end_time: # 초과
                            diff = now_time - end_time
                            diff_sec = round(diff.total_seconds())
                            day = divmod(diff_sec, 3600)[0]
                            minute = divmod(diff_sec - (day*3600), 60)[0]
                            i['leftTime'] = None
                            i['overTime'] = f"{day}:{str(minute).zfill(2)}"
                        else:
                            diff = end_time - now_time
                            diff_sec = round(diff.total_seconds())
                            day = divmod(diff_sec, 3600)[0]
                            minute = divmod(diff_sec - (day*3600), 60)[0]
                            i['leftTime'] = f"{day}:{str(minute).zfill(2)}"
                            i['overTime'] =  None
                    else:
                        i['leftTime'] = None
                        i['overTime'] = None
                else:
                    if i['entry_time']:
                        i['leftTime'] = '무제한'
                    else:
                        i['leftTime'] = None
                    i['overTime'] = None


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

        # 가맹점 이용시간 사용시
        additional_price = 0
        additional_dict = {}

        if shop_table.shop.table_time > 0:
            if shop_table.entry_time:
                now_time = timezone.now()
                end_time = shop_table.entry_time + datetime.timedelta(minutes=shop_table.shop.table_time)
                if now_time > end_time:                      
                    diff = now_time - end_time
                    diff_sec = round(diff.total_seconds())
                    minutes = divmod(diff_sec, 60)[0]
                    if shop_table.shop.additional_fee_time > 0:
                        over_count = divmod(minutes, shop_table.shop.additional_fee_time)[0]
                        if over_count > 0:
                            if shop_table.cart:
                                cart_list = json.loads(shop_table.cart)
                                for i in cart_list:
                                    try:
                                        goods = Goods.objects.get(pk=i['goodsId'], shop_id=shop_id)
                                        if goods.additional_fee_goods:
                                            additional_fee_goods = Goods.objects.get(pk=goods.additional_fee_goods, shop_id=shop_id)
                                            if additional_fee_goods.pk in additional_dict:
                                                additional_dict[f'{additional_fee_goods.pk}'] += i['quantity']
                                            else:
                                                additional_dict[f'{additional_fee_goods.pk}'] = i['quantity']
                                    except:
                                        pass
                                if additional_dict:
                                    for k, v in additional_dict.items():
                                        cart={}
                                        try:
                                            is_new = True
                                            additional_goods = Goods.objects.get(pk=k, shop=shop_table.shop)
                                            for i in cart_list:
                                                if i['goodsId'] == additional_goods.pk:
                                                    # 이미 담긴 상품일때
                                                    if not i['optionList'] and i['discount'] == 0:
                                                        is_new = False
                                                        adjusted_quantity = int(v) * over_count - i['quantity']
                                                        i['quantity'] = int(v) * over_count
                                                        additional_price += adjusted_quantity * i['price']
                                                        break
                                            if is_new:
                                                cart['goodsId'] = additional_goods.pk
                                                cart['name_kr'] = additional_goods.name_kr
                                                cart['price'] = additional_goods.sale_price
                                                cart['discount'] = 0
                                                cart['quantity'] = int(v) * over_count
                                                cart['optionName'] = ''
                                                cart['optionPrice'] = 0
                                                cart['optionList'] = []
                                                cart_list.append(cart)
                                                additional_price += int(v) * over_count * additional_goods.sale_price
                                        except:
                                            pass

                                    cart_list = json.dumps(cart_list, ensure_ascii=False)
                                    shop_table.cart = cart_list
                                    shop_table.total_price += additional_price
                                    shop_table.save()
                                    cart_list = json.loads(cart_list)       
                                                          
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
        data['agencyName'] = shop_table.shop.agency.name
        data['shopName'] = shop_table.shop.name_kr
        data['shopDescription'] = shop_table.shop.description
        data['shopRepresentative'] = shop_table.shop.representative
        data['shopRegistrationNo'] = shop_table.shop.registration_no
        data['shopPhone'] = shop_table.shop.phone
        data['shopAddress'] = shop_table.shop.address
        data['shopAddressDetail'] = shop_table.shop.address_detail
        data['shopZipcode'] = shop_table.shop.zipcode
        data['shopReceipt'] = shop_table.shop.receipt

        return_data = {
            'data': data,
            'resultCd': '0000',
            'msg': 'tid 정보',
        }
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")