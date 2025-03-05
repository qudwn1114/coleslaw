from django.conf import settings
from django.views.generic import View
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.db.models import CharField, F, Value as V, Func, Q, Count
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone

from system_manage.models import Shop, ShopMember, ShopCoupon, ShopMemberCoupon
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

        return_data = {'data': {'id':shop_member.pk,'membername':membername, 'phone':phone},'msg': '가입완료!','resultCd': '0000'}
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")
    

class ShopMemberCouponListView(View):
    '''
        shop member coupon list api
    '''
    def get(self, request, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        shop_member_id = kwargs.get('shop_member_id')
        # shop_id 검증
        try:
            shop = Shop.objects.get(pk=shop_id)
        except Shop.DoesNotExist:
            return JsonResponse({'data': {}, 'msg': 'shop id 오류', 'resultCd': '0001'}, json_dumps_params={'ensure_ascii': False})
        try:
            shop_member = ShopMember.objects.get(pk=shop_member_id, shop=shop)
        except:
            return JsonResponse({'data': {}, 'msg': 'shop member 오류', 'resultCd': '0001'}, json_dumps_params={'ensure_ascii': False})
        ShopMemberCoupon.objects.filter(shop_member=shop_member, status='0', expiration_date__lte=timezone.now()).update(status='2')
        try:
            queryset = ShopMemberCoupon.objects.filter(shop_member=shop_member).annotate(
                expirationDate=Func(
                    F('expiration_date'),
                    V('%y.%m.%d'),
                    function='DATE_FORMAT',
                    output_field=CharField()
                ),
                usedAt=Func(
                    F('used_at'),
                    V('%y.%m.%d %H:%i'),
                    function='DATE_FORMAT',
                    output_field=CharField()
                ),
            ).values('id', 'name', 'status', 'expirationDate', 'usedAt',).order_by('-id')
            return JsonResponse({
                'data': list(queryset),
                'resultCd': '0000',
                'msg': '회원 보유 쿠폰 리스트',
                'totalCnt': queryset.count()
            }, json_dumps_params={'ensure_ascii': False})
        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse({'data': [], 'msg': '오류!', 'resultCd': '0001'}, json_dumps_params={'ensure_ascii': False})
        
class ShopMemberCouponCreateView(View):
    '''
        shop coupon create api
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ShopMemberCouponCreateView, self).dispatch(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        shop_member_id = kwargs.get('shop_member_id')
        try:
            shop = Shop.objects.get(pk=shop_id)
        except Shop.DoesNotExist:
            return JsonResponse({'data': {}, 'msg': 'shop id 오류', 'resultCd': '0001'}, json_dumps_params={'ensure_ascii': False})
        if not shop.coupon_flag:
            return JsonResponse({'data': {}, 'msg': '쿠폰 기능을 사용할수 없는 가맹점입니다.', 'resultCd': '0001'}, json_dumps_params={'ensure_ascii': False})
        try:
            shop_member = ShopMember.objects.get(pk=shop_member_id, shop=shop)
        except:
            return JsonResponse({'data': {}, 'msg': 'shop member 오류', 'resultCd': '0001'}, json_dumps_params={'ensure_ascii': False})
        
        shop_coupon_id = request.POST['shop_coupon_id']
        quantity = int(request.POST['quantity'])
        if quantity < 1:
            return JsonResponse({'data': {}, 'msg': '수량은 1개 이상이어야 합니다.', 'resultCd': '0001'}, json_dumps_params={'ensure_ascii': False})

        try:
            shop_coupon = ShopCoupon.objects.get(pk=shop_coupon_id, shop=shop)
        except:
            return JsonResponse({'data': {}, 'msg': 'shop coupon id 오류', 'resultCd': '0001'}, json_dumps_params={'ensure_ascii': False})
        # 쿠폰 생성
        coupons = []
        if shop_coupon.expiration_period == 0:
            expiration_date = None
        else:
            expiration_date = timezone.now() + datetime.timedelta(days=shop_coupon.expiration_period)
            expiration_date = expiration_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        for _ in range(quantity):
            coupons.append(ShopMemberCoupon(
                shop_member=shop_member,
                shop_coupon=shop_coupon,
                name=shop_coupon.name,
                expiration_date=expiration_date
            ))

        ShopMemberCoupon.objects.bulk_create(coupons)
        return JsonResponse({'data': {'couponCount':ShopMemberCoupon.objects.filter(shop_member=shop_member, status='0').count()}, 'msg': '쿠폰이 성공적으로 발급되었습니다.', 'resultCd': '0000'}, json_dumps_params={'ensure_ascii': False})

class ShopMemberCouponDeleteView(View):
    '''
        shop coupon delete api
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ShopMemberCouponDeleteView, self).dispatch(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        shop_member_id = kwargs.get('shop_member_id')
        try:
            shop = Shop.objects.get(pk=shop_id)
        except Shop.DoesNotExist:
            return JsonResponse({'data': {}, 'msg': 'shop id 오류', 'resultCd': '0001'}, json_dumps_params={'ensure_ascii': False})
        if not shop.coupon_flag:
            return JsonResponse({'data': {}, 'msg': '쿠폰 기능을 사용할수 없는 가맹점입니다.', 'resultCd': '0001'}, json_dumps_params={'ensure_ascii': False})
        try:
            shop_member = ShopMember.objects.get(pk=shop_member_id, shop=shop)
        except:
            return JsonResponse({'data': {}, 'msg': 'shop member 오류', 'resultCd': '0001'}, json_dumps_params={'ensure_ascii': False})
        
        shop_member_coupon_id = request.POST['shop_member_coupon_id']
        try:
            shop_member_coupon = ShopMemberCoupon.objects.get(pk=shop_member_coupon_id, shop_member=shop_member)
        except:
            return JsonResponse({'data': {}, 'msg': 'shop member coupon id 오류', 'resultCd': '0001'}, json_dumps_params={'ensure_ascii': False})
        shop_member_coupon.delete()
        return JsonResponse({'data': {'couponCount':ShopMemberCoupon.objects.filter(shop_member=shop_member, status='0').count()}, 'msg': '쿠폰이 삭제되었습니다.', 'resultCd': '0000'}, json_dumps_params={'ensure_ascii': False})
    

class ShopMemberCouponStatusView(View):
    '''
        shop coupon status api
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ShopMemberCouponStatusView, self).dispatch(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        shop_member_id = kwargs.get('shop_member_id')
        try:
            shop = Shop.objects.get(pk=shop_id)
        except Shop.DoesNotExist:
            return JsonResponse({'data': {}, 'msg': 'shop id 오류', 'resultCd': '0001'}, json_dumps_params={'ensure_ascii': False})
        if not shop.coupon_flag:
            return JsonResponse({'data': {}, 'msg': '쿠폰 기능을 사용할수 없는 가맹점입니다.', 'resultCd': '0001'}, json_dumps_params={'ensure_ascii': False})
        try:
            shop_member = ShopMember.objects.get(pk=shop_member_id, shop=shop)
        except:
            return JsonResponse({'data': {}, 'msg': 'shop member 오류', 'resultCd': '0001'}, json_dumps_params={'ensure_ascii': False})
        
        shop_member_coupon_id = request.POST['shop_member_coupon_id']
        try:
            shop_member_coupon = ShopMemberCoupon.objects.get(pk=shop_member_coupon_id, shop_member=shop_member)
        except:
            return JsonResponse({'data': {}, 'msg': 'shop member coupon id 오류', 'resultCd': '0001'}, json_dumps_params={'ensure_ascii': False})
        if shop_member_coupon.status == '0':
            if shop_member_coupon.expiration_date < timezone.now():
                return JsonResponse({'data': {}, 'msg': '유효기간이 만료 된 쿠폰입니다.', 'resultCd': '0001'}, json_dumps_params={'ensure_ascii': False})
            shop_member_coupon.status = '1'
            shop_member_coupon.used_at = timezone.now()
            shop_member_coupon.save()
        elif shop_member_coupon.status == '1':
            if shop_member_coupon.expiration_date < timezone.now():
                return JsonResponse({'data': {'couponCount':ShopMemberCoupon.objects.filter(shop_member=shop_member, status='0').count()}, 'msg': '유효기간이 만료 된 쿠폰입니다.', 'resultCd': '0001'}, json_dumps_params={'ensure_ascii': False})
            shop_member_coupon.status = '0'
            shop_member_coupon.used_at = None
            shop_member_coupon.save()
            return JsonResponse({'data': {'couponCount':ShopMemberCoupon.objects.filter(shop_member=shop_member, status='0').count()}, 'msg': '취소되었습니다.', 'resultCd': '0000'}, json_dumps_params={'ensure_ascii': False})
        elif shop_member_coupon.status == '2':
            return JsonResponse({'data': {}, 'msg': '만료 된 쿠폰입니다.', 'resultCd': '0001'}, json_dumps_params={'ensure_ascii': False})
        

class ShopCouponListView(View):
    '''
        shop coupon list api
    '''
    def get(self, request, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        # shop_id 검증
        try:
            shop = Shop.objects.get(pk=shop_id)
        except Shop.DoesNotExist:
            return JsonResponse({'data': {}, 'msg': 'shop id 오류', 'resultCd': '0001'}, json_dumps_params={'ensure_ascii': False})

        try:
            queryset = ShopCoupon.objects.filter(shop=shop).values('id', 'name', 'expiration_period').order_by('id')

            return JsonResponse({
                'data': list(queryset),
                'resultCd': '0000',
                'msg': '가맹점 쿠폰 리스트',
                'totalCnt': queryset.count()
            }, json_dumps_params={'ensure_ascii': False})

        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse({'data': [], 'msg': '오류!', 'resultCd': '0001'}, json_dumps_params={'ensure_ascii': False})
