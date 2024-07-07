from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import View
from django.http import HttpRequest, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
from django.utils.decorators import method_decorator
from django.db.models import Max
from django.db import transaction
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from system_manage.decorators import permission_required
from shop_manage.views.shop_manage_views.auth_views import check_shop
from system_manage.models import ShopTable, Shop
import json

class ShopTableManageView(View):
    '''
        가맹점 테이블 관리
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
        
        if search_keyword:
            context['search_type'] = search_type
            context['search_keyword'] = search_keyword
            filter_dict[search_type + '__icontains'] = search_keyword

        obj_list = ShopTable.objects.filter(**filter_dict).exclude(table_no=0).values(
            'id',
            'name',
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

        return render(request, 'table_manage/table_manage.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def put(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return JsonResponse({'message' : '가맹점 오류'},status = 400)
        
        request.PUT = json.loads(request.body)
        table_id = request.PUT['id']
        table_name = request.PUT['table_name'].strip()
        try:
            shop_table = ShopTable.objects.get(pk=table_id, shop=shop)
        except:
            return JsonResponse({"message": "데이터 오류"},status=400)
        
        shop_table.name =table_name
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
            return JsonResponse({"message": "데이터 오류"},status=400)
        
        shop_table.delete()
        
        return JsonResponse({'message' : '삭제되었습니다.'}, status = 201)

class ShopTableCreateView(View):
    '''
        가맹점 테이블 등록
    '''
    @method_decorator(permission_required(redirect_url='shop_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return redirect('shop_manage:notfound')
        context['shop'] = shop

        return render(request, 'table_manage/table_create.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return JsonResponse({'message' : '가맹점 오류'},status = 400)
        
        table_name = request.POST['table_name'].strip()
        count = int(request.POST['count'])

        max_table_no = ShopTable.objects.filter(shop=shop).aggregate(Max("table_no", default=0))['table_no__max']

        try:
            bulk_list = []
            for i in range(1, count+1):
                bulk_list.append(ShopTable(shop=shop, table_no=max_table_no+i, name=f'{table_name}{max_table_no+i}'))

            ShopTable.objects.bulk_create(bulk_list)
        except:
            return JsonResponse({'message' : '생성 오류'},status = 400)
        
        return JsonResponse({'message' : '생성 완료', 'url':reverse('shop_manage:table_manage', kwargs={'shop_id':shop.id})},  status = 201)

