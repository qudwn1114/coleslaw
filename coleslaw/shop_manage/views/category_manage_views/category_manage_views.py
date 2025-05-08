from django.shortcuts import render, redirect
from django.http import HttpRequest, JsonResponse
from django.views.generic import View
from django.views.decorators.http import require_http_methods
from django.db.models import ProtectedError, F
from django.db import IntegrityError, transaction
from django.utils.decorators import method_decorator
from system_manage.decorators import permission_required
from shop_manage.views.shop_manage_views.auth_views import check_shop
from system_manage.models import MainCategory, SubCategory
import json

class CategoryManageView(View):
    '''
    카테고리 관리
    '''
    @method_decorator(permission_required(redirect_url='shop_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return redirect('shop_manage:notfound')
        context['shop'] = shop

        context['MainCategory'] = MainCategory.objects.filter(shop=shop).order_by('rank')
        return render(request, 'category_manage/category_manage.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return JsonResponse({'message' : '가맹점 오류'},status = 400)

        categoryType = request.POST['categoryType']
        categoryNameKr = request.POST['categoryNameKr'].strip()
        categoryNameEn = request.POST['categoryNameEn'].strip()
        if categoryType == 'main':
            try:
                category = MainCategory.objects.create(
                    shop=shop,
                    name_kr = categoryNameKr,
                    name_en = categoryNameEn
                )
            except IntegrityError:
                return JsonResponse({'message':'이미 대분류에 존재하는 카테고리 입니다.'}, status = 400)
            return JsonResponse({'message' : '생성 완료', 'id':category.id, 'type':'main', 'data':list(MainCategory.objects.filter(shop=shop).order_by('rank').values('id', 'name_kr', 'name_en'))}, status = 201)

        elif categoryType == 'sub':
            parentCategoryId = request.POST['parentCategoryId']
            main_category = MainCategory.objects.get(pk=parentCategoryId, shop=shop)
            try:
                category = SubCategory.objects.create(
                    shop=shop,
                    main_category = main_category,
                    name_kr = categoryNameKr,
                    name_en = categoryNameEn
                )
            except IntegrityError:
                return JsonResponse({'message':'이미 소분류에 존재하는 카테고리 입니다.'}, status = 400)
            return JsonResponse({'message' : '생성 완료', 'id':category.id, 'type':'sub', 'data':list(main_category.sub_category.filter(shop=shop).order_by('rank').values('id', 'name_kr', 'name_en'))}, status = 201)
        else:
            return JsonResponse({'message':'전달값 오류..'}, status = 400)
        
    @method_decorator(permission_required(raise_exception=True))
    def put(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return JsonResponse({'message' : '가맹점 오류'},status = 400)
        
        request.PUT = json.loads(request.body)
        categoryType = request.PUT['categoryType']
        categoryId = request.PUT['categoryId']
        categoryNameKr = request.PUT['categoryNameKr'].strip()
        categoryNameEn = request.PUT['categoryNameEn'].strip()

        if categoryType == 'main':
            category = MainCategory.objects.get(id=categoryId, shop=shop)
            try:
                category.name_kr = categoryNameKr
                category.name_en = categoryNameEn
                category.save()
            except IntegrityError:
                return JsonResponse({'message':'이미 대분류에 존재하는 카테고리 입니다.'}, status = 400)            
            return JsonResponse({'message' : '수정 완료', 'id':category.id, 'type':'main', 'data':list(MainCategory.objects.filter(shop=shop).order_by('rank').values('id', 'name_kr', 'name_en'))}, status = 201)
        elif categoryType == 'sub':
            category = SubCategory.objects.get(id=categoryId, shop=shop)
            try:
                category.name_kr = categoryNameKr
                category.name_en = categoryNameEn
                category.save()
            except IntegrityError:
                return JsonResponse({'message':'이미 소분류에 존재하는 카테고리 입니다.'}, status = 400)
            return JsonResponse({'message' : '수정 완료', 'id':category.id, 'type':'sub', 'data':list(category.main_category.sub_category.filter(shop=shop).order_by('rank').values('id', 'name_kr', 'name_en'))}, status = 201)
        else:
            return JsonResponse({'message':'전달값 오류..'}, status = 400)

    @method_decorator(permission_required(raise_exception=True))
    def delete(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return JsonResponse({'message' : '가맹점 오류'},status = 400)
        
        request.DELETE = json.loads(request.body)
        categoryType = request.DELETE['categoryType']
        categoryId = request.DELETE['categoryId']
        if categoryType == 'main':
            category = MainCategory.objects.get(id=categoryId, shop=shop)
            try:
                category.delete()
            except ProtectedError:
                return JsonResponse({'message':'하위 노드들이 있어 삭제 불가능합니다.'}, status = 400)
            return JsonResponse({'message' : '삭제 완료', 'data':list(MainCategory.objects.filter(shop=shop).order_by('rank').values('id', 'name_kr', 'name_en'))}, status = 200)
        elif categoryType == 'sub':
            category = SubCategory.objects.get(id=categoryId, shop=shop)
            main_category = category.main_category
            try:
                category.delete()
            except ProtectedError:
                return JsonResponse({'message':'하위 노드들이 있어 삭제 불가능합니다.'}, status = 400)
            return JsonResponse({'message' : '삭제 완료', 'data':list(main_category.sub_category.filter(shop=shop).order_by('rank').values('id', 'name_kr', 'name_en'))}, status = 200)
        else:
            return JsonResponse({'message':'전달값 오류..'}, status = 400)

@require_http_methods(["POST"])
def sub_category(request: HttpRequest, *args, **kwargs):
    '''
    소분류 반환
    '''
    shop_id = kwargs.get('shop_id')
    shop = check_shop(pk=shop_id)
    if not shop:
        return JsonResponse({'message' : '가맹점 오류'},status = 400)

    parent_id = request.POST['parent_id']
    try:
        data = list(MainCategory.objects.get(pk=parent_id, shop=shop).sub_category.filter(shop=shop).order_by('rank').values('id', 'name_kr', 'name_en'))
        return JsonResponse({'data':data, 'type':'sub', 'message':'Sub Category List'}, status = 200)
    except Exception as e:
        return JsonResponse({'message':'데이터 오류..'}, status = 400)
    

@require_http_methods(["POST"])
def category(request: HttpRequest, *args, **kwargs):
    '''
    카테고리 반환
    '''
    shop_id = kwargs.get('shop_id')
    shop = check_shop(pk=shop_id)
    if not shop:
        return JsonResponse({'message' : '가맹점 오류'},status = 400)
    main_category = list(MainCategory.objects.filter(shop=shop).order_by('rank').values('id', 'name_kr', 'name_en'))
    sub_category = list(SubCategory.objects.filter(shop=shop).annotate(
        parent_id = F('main_category_id')
    ).order_by('rank').values('id', 'parent_id', 'name_kr', 'name_en'))
    
    data = {
        "main_category_list" : main_category,
        "sub_category_list" : sub_category
    }
    return JsonResponse(data, status = 200)



@require_http_methods(["POST"])
def update_category_rank(request: HttpRequest, *args, **kwargs):
    '''
        카테고리 순서 변경
    '''
    shop_id = kwargs.get('shop_id')
    shop = check_shop(pk=shop_id)
    if not shop:
        return JsonResponse({'message' : '가맹점 오류'},status = 400)
    data = json.loads(request.body)
    category_type = data.get('category_type', None)
    order_list = data.get('order_data', [])
    if category_type == 'main':
        category_ids = [item.get('id') for item in order_list]
        main_category_queryset = MainCategory.objects.filter(id__in=category_ids, shop_id=shop_id)
        if main_category_queryset.count() != len(category_ids):
            return JsonResponse({'message': '잘못된 ID가 포함되어 있습니다.'}, status=400)
        rank_map = {int(item['id']): item['rank'] for item in order_list}
        try:
            with transaction.atomic():
                for main_category in main_category_queryset:
                    new_rank = rank_map.get(main_category.id)
                    setattr(main_category, 'rank', new_rank)
                MainCategory.objects.bulk_update(main_category_queryset, ['rank'])
        except Exception as e:
            print(e)
            return JsonResponse({'message': f'에러 발생: {str(e)}'}, status=400)

    elif category_type == 'sub':
        category_ids = [item.get('id') for item in order_list]
        sub_category_queryset = SubCategory.objects.filter(id__in=category_ids, shop_id=shop_id)
        if sub_category_queryset.count() != len(category_ids):
            return JsonResponse({'message': '잘못된 ID가 포함되어 있습니다.'}, status=400)
        rank_map = {int(item['id']): item['rank'] for item in order_list}
        try:
            with transaction.atomic():
                for sub_category in sub_category_queryset:
                    new_rank = rank_map.get(sub_category.id)
                    setattr(sub_category, 'rank', new_rank)
                SubCategory.objects.bulk_update(sub_category_queryset, ['rank'])
        except Exception as e:
            print(e)
            return JsonResponse({'message': f'에러 발생: {str(e)}'}, status=400)
    else:
        return JsonResponse({'message': '유효하지 않은 카테고리 type 입니다.'}, status=400)
    
    return JsonResponse({'message': '순서가 성공적으로 저장되었습니다.'}, status=200)