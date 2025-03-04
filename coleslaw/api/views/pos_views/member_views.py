from django.conf import settings
from django.views.generic import View
from django.urls import reverse
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.db.models import CharField, F, Value as V, Func, Q, Count
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from system_manage.models import Shop, ShopMember
from system_manage.views.system_manage_views.auth_views import validate_phone


import traceback, json, datetime

class ShopMemberListView(View):
    '''
        shop table list api
    '''
    def get(self, request, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        search = request.GET.get('search', '').strip()  # 검색어를 받아옴 (없으면 빈 문자열)

        # shop_id 검증
        try:
            shop = Shop.objects.get(pk=shop_id)
        except Shop.DoesNotExist:
            return JsonResponse({'data': {}, 'msg': 'shop id 오류', 'resultCd': '0001'}, json_dumps_params={'ensure_ascii': False})

        try:
            queryset = ShopMember.objects.filter(shop=shop)
            # 검색어가 있을 경우에만 필터링
            if search:
                queryset = queryset.filter(
                    Q(membername__icontains=search) | Q(phone__icontains=search)
                )

            queryset = queryset.annotate(
                couponCount=Count('shop_member_coupon', filter=Q(shop_member_coupon__status='0')),  # 미사용 쿠폰 개수만 집계
                createdAt=Func(
                    F('created_at'),
                    V('%y.%m.%d %H:%i'),
                    function='DATE_FORMAT',
                    output_field=CharField()
                ),
            ).values('id', 'membername', 'phone', 'couponCount', 'createdAt').order_by('id')

            return JsonResponse({
                'data': list(queryset),
                'resultCd': '0000',
                'msg': '가맹점 회원 리스트',
                'totalCnt': queryset.count()
            }, json_dumps_params={'ensure_ascii': False})

        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse({'data': [], 'msg': '오류!', 'resultCd': '0001'}, json_dumps_params={'ensure_ascii': False})
    

class ShopMemberCreateView(View):
    '''
        회원등록
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ShopMemberCreateView, self).dispatch(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        try:
            shop = Shop.objects.get(pk=shop_id)
        except:
            return_data = {'data': {},'msg': 'shop id 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        
        membername = request.POST['membername'].strip()
        phone = request.POST['phone']

        if not validate_phone(phone):
            return_data = {'data': {},'msg': '유효하지 않은 전화번호 형식입니다.','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        try:
            ShopMember.objects.get(shop=shop, phone=phone)
            return_data = {'data': {},'msg': '이미 가입된 번호입니다.','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        except:
            pass
            
        shop_member, created = ShopMember.objects.get_or_create(
            shop=shop, phone=phone,
            defaults={ 'membername' : membername }
        )

        return_data = {'data': {},'msg': '가입완료!','resultCd': '0000'}
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")
        
