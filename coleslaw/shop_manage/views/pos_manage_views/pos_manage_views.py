from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import View
from django.http import HttpRequest, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
from django.utils.decorators import method_decorator
from django.db.models import Min
from django.db import transaction
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from system_manage.decorators import permission_required
from shop_manage.views.shop_manage_views.auth_views import check_shop
from system_manage.models import ShopTable, Shop
import json

class ShopPosManageView(View):
    '''
        pos manage
    '''
    @method_decorator(permission_required(redirect_url='shop_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return redirect('shop_manage:notfound')
        context['shop'] = shop
        
        paginate_by = '20'
        page = request.GET.get('page', '1')
        search_type = request.GET.get('search_type', '')
        search_keyword = request.GET.get('search_keyword', '')

        filter_dict = {}
        filter_dict['shop'] = shop
        filter_dict['table_no__lte'] = 0 
        
        if search_keyword:
            context['search_type'] = search_type
            context['search_keyword'] = search_keyword
            filter_dict[search_type + '__icontains'] = search_keyword

        obj_list = ShopTable.objects.filter(**filter_dict).values(
            'id',
            'name',
            'table_no',
            'tid',
            'created_at'
        ).order_by('id')

        paginator = Paginator(obj_list, paginate_by)
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page = 1
            page_obj = paginator.page(page)
        except EmptyPage:
            page = 1
            page_obj = paginator.page(page)
        except InvalidPage:
            page = 1
            page_obj = paginator.page(page)

        pagelist = paginator.get_elided_page_range(page, on_each_side=3, on_ends=1)
        context['pagelist'] = pagelist
        context['page_obj'] = page_obj

        return render(request, 'pos_manage/pos_manage.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def put(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return JsonResponse({'message' : '가맹점 오류'},status = 400)
        
        request.PUT = json.loads(request.body)
        table_id = request.PUT['id']
        rq_type = request.PUT['type']
        try:
            shop_table = ShopTable.objects.get(pk=table_id, shop=shop)
        except:
            return JsonResponse({"message": "데이터 오류"},status=400)

        if rq_type == 'NAME':
            table_name = request.PUT['table_name'].strip()            
            shop_table.name = table_name
            shop_table.save()
        elif rq_type == 'TID':
            if shop_table.table_no == 0:
                return JsonResponse({"message": "메인 포스 tid 는 가맹점 관리에서 변경해주세요."}, status=400)

            tid = request.PUT['tid'].strip()
            shop_table.tid = tid
            shop_table.save()

        return JsonResponse({'message' : '변경되었습니다.'}, status = 201)
    
    @method_decorator(permission_required(raise_exception=True))
    def delete(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return JsonResponse({'message' : '가맹점 오류'},status = 400)
        
        request.DELETE = json.loads(request.body)
        table_id = request.DELETE['id']

        try:
            shop_table = ShopTable.objects.get(pk=table_id, shop=shop)
        except:
            return JsonResponse({"message": "데이터 오류"},status=400)
        
        if shop_table.table_no == 0:
            return JsonResponse({"message": "메인 pos는 삭제 불가능합니다."},status=400)
        
        if shop_table.table_no > 0:
            return JsonResponse({"message": "데이터 오류"},status=400)
        
        shop_table.delete()
        
        return JsonResponse({'message' : '삭제되었습니다.'}, status = 201)

class ShopPosCreateView(View):
    '''
        pos 생성
    '''
    @method_decorator(permission_required(redirect_url='shop_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return redirect('shop_manage:notfound')
        context['shop'] = shop

        return render(request, 'pos_manage/pos_create.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return JsonResponse({'message' : '가맹점 오류'},status = 400)
        
        table_name = request.POST['table_name'].strip()
        min_table_no = ShopTable.objects.filter(shop=shop, table_no__lte=0).aggregate(Min("table_no", default=0))['table_no__min']
        ShopTable.objects.create(
            shop=shop,
            name=table_name,
            tid=shop.main_tid,
            table_no= min_table_no - 1
        )
        
        return JsonResponse({'message' : '생성 완료', 'url':reverse('shop_manage:pos_manage', kwargs={'shop_id':shop.id})},  status = 201)


class ShopPosDetailView(View):
    '''
        가맹점 포스 정보 상세
    '''
    @method_decorator(permission_required(redirect_url='shop_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return redirect('shop_manage:notfound')
        context['shop'] = shop
        
        return render(request, 'pos_manage/shop_pos_detail.html', context)
    

class ShopPosEditView(View):
    '''
        가맹점 포스 정보 수정
    '''
    @method_decorator(permission_required(redirect_url='shop_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return redirect('shop_manage:notfound')
        context['shop'] = shop
        
        return render(request, 'pos_manage/shop_pos_edit.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def post(self, request: HttpRequest, *args, **kwargs):
        VIDEO_MAX_UPLOAD_SIZE = 209715200
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return JsonResponse({'message' : '가맹점 오류'},status = 400)
        
        pos_ad_video = request.FILES.get("pos_ad_video")
        receipt = request.POST['receipt'].strip()
        shop_receipt_flag = bool(request.POST.get('shop_receipt_flag', None))

        if pos_ad_video:
            if pos_ad_video.size > VIDEO_MAX_UPLOAD_SIZE:
                return JsonResponse({"message": "광고 비디오 용량은 200mb 제한입니다."}, status=400)
        
        shop.receipt = receipt
        shop.shop_receipt_flag = shop_receipt_flag
        if pos_ad_video:
            shop.pos_ad_video = pos_ad_video

        shop.save()
        return JsonResponse({'message' : '수정 완료', 'url':reverse('shop_manage:shop_pos_detail', kwargs={'shop_id':shop.id})},  status = 201)
    