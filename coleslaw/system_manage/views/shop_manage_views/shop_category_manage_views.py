from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import View
from django.http import HttpRequest, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.db import transaction
from system_manage.decorators import permission_required
from system_manage.models import ShopCategory

class ShopCategoryManageView(View):
    '''
        가맹점 카테고리 관리 화면
    '''
    @method_decorator(permission_required(redirect_url='system_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        paginate_by = '20'
        page = request.GET.get('page', '1')
        search_type = request.GET.get('search_type', '')
        search_keyword = request.GET.get('search_keyword', '')

        filter_dict = {}

        if search_keyword:
            context['search_type'] = search_type
            context['search_keyword'] = search_keyword
            filter_dict[search_type + '__icontains'] = search_keyword

        obj_list = ShopCategory.objects.filter(**filter_dict).values(
            'id',
            'name_kr',
            'name_en',
            'created_at',
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

        return render(request, 'shop_manage/shop_category_manage.html', context)
    


class ShopCategoryCreateView(View):
    '''
        가맹점 카테고리 생성
    '''
    @method_decorator(permission_required(redirect_url='system_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}

        return render(request, 'shop_manage/shop_category_create.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_category_name_kr = request.POST['shop_category_name_kr'].strip()
        shop_category_name_en = request.POST['shop_category_name_en'].strip()
        description = request.POST['description'].strip()
        image = request.FILES.get("image")

        try:
            ShopCategory.objects.get(name_kr=shop_category_name_kr)
            return JsonResponse({'message': '이미 존재하는 카테고리 한글명 입니다.'}, status=400)
        except:
            pass

        try:
            ShopCategory.objects.get(name_en=shop_category_name_en)
            return JsonResponse({'message': '이미 존재하는 카테고리 영문명 입니다.'}, status=400)
        except:
            pass

        shop_category = ShopCategory.objects.create(
            name_kr=shop_category_name_kr,
            name_en=shop_category_name_en,
            description=description,
            image=image
        )

        return JsonResponse({'message' : '등록 되었습니다.', 'url':reverse("system_manage:shop_category_detail", kwargs={"pk" : shop_category.id})},  status = 202)
    


class ShopCategoryDetailView(View):
    '''
        가맹점 카테고리 상세 화면
    '''
    @method_decorator(permission_required(redirect_url='system_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        pk = kwargs.get("pk")
        data = get_object_or_404(ShopCategory, pk=pk)
        context['data'] = data

        return render(request, 'shop_manage/shop_category_detail.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def delete(self, request: HttpRequest, *args, **kwargs):
        pk = kwargs.get('pk')
        try:
            shop_category = ShopCategory.objects.get(pk=pk)
        except:
            return JsonResponse({"message": "데이터 오류"},status=400)
        
        shop_category.delete()

        return JsonResponse({'message' : '삭제되었습니다.', 'url':reverse('system_manage:shop_category_manage')},  status = 202)
    

class ShopCategoryEditView(View):
    '''
        가맹점 수정 화면
    '''
    @method_decorator(permission_required(redirect_url='system_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        pk = kwargs.get("pk")
        data = get_object_or_404(ShopCategory, pk=pk)
        context['data'] = data

        return render(request, 'shop_manage/shop_category_edit.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def post(self, request: HttpRequest, *args, **kwargs):
        pk = kwargs.get('pk')
        try:
            shop_category = ShopCategory.objects.get(pk=pk)
        except:
            return JsonResponse({"message": "데이터 오류"},status=400)
        
        shop_category_name_kr = request.POST['shop_category_name_kr'].strip()
        shop_category_name_en = request.POST['shop_category_name_en'].strip()
        description = request.POST['description'].strip()
        image = request.FILES.get("image")
    
        if ShopCategory.objects.filter(name_kr=shop_category_name_kr).exclude(pk=shop_category.pk).exists():
            return JsonResponse({'message': '이미 존재하는 카테고리 한글명 입니다.'}, status=400)
        
        if ShopCategory.objects.filter(name_en=shop_category_name_en).exclude(pk=shop_category.pk).exists():
            return JsonResponse({'message': '이미 존재하는 카테고리 영문명 입니다.'}, status=400)
        
        shop_category.name_kr = shop_category_name_kr
        shop_category.name_en = shop_category_name_en
        shop_category.description = description
        if image:
            shop_category.image = image
        shop_category.save()

        return JsonResponse({'message' : '수정 되었습니다.', 'url':reverse("system_manage:shop_category_detail", kwargs={"pk" : shop_category_name.id})},  status = 202)



    