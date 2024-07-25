from django.shortcuts import render
from django.http import HttpRequest, JsonResponse
from django.views.generic import View
from django.views.decorators.http import require_http_methods
from django.db.models import ProtectedError, F
from django.db import IntegrityError
from django.utils.decorators import method_decorator
from system_manage.decorators import permission_required
from system_manage.models import MainCategory, SubCategory
import json

class CategoryManageView(View):
    '''
    카테고리 관리
    '''
    @method_decorator(permission_required(redirect_url='system_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        context['MainCategory'] = MainCategory.objects.all().order_by('name')
        return render(request, 'category_manage/category_manage.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def post(self, request: HttpRequest, *args, **kwargs):
        categoryType = request.POST['categoryType']
        categoryNameKr = request.POST['categoryNameKr'].strip()
        categoryNameEn = request.POST['categoryNameEn'].strip()
        if categoryType == 'main':
            try:
                category = MainCategory.objects.create(
                    name_kr = categoryNameKr,
                    name_en = categoryNameEn
                )
            except IntegrityError:
                return JsonResponse({'message':'이미 대분류에 존재하는 카테고리 입니다.'}, status = 400)
            return JsonResponse({'message' : '생성 완료', 'id':category.id, 'type':'main', 'data':list(MainCategory.objects.all().order_by('name_kr').values('id', 'name_kr', 'name_en'))}, status = 201)

        elif categoryType == 'sub':
            parentCategoryId = request.POST['parentCategoryId']
            main_category = MainCategory.objects.get(pk=parentCategoryId)
            try:
                category = SubCategory.objects.create(
                    main_category = main_category,
                    name_kr = categoryNameKr
                )
            except IntegrityError:
                return JsonResponse({'message':'이미 소분류에 존재하는 카테고리 입니다.'}, status = 400)
            return JsonResponse({'message' : '생성 완료', 'id':category.id, 'type':'sub', 'data':list(main_category.sub_category.all().order_by('name_kr').values('id', 'name_kr', 'name_en'))}, status = 201)
        else:
            return JsonResponse({'message':'전달값 오류..'}, status = 400)
        
    @method_decorator(permission_required(raise_exception=True))
    def put(self, request: HttpRequest, *args, **kwargs):
        request.PUT = json.loads(request.body)
        categoryType = request.PUT['categoryType']
        categoryId = request.PUT['categoryId']
        categoryNameKr = request.POST['categoryNameKr'].strip()
        categoryNameEn = request.POST['categoryNameEn'].strip()

        if categoryType == 'main':
            category = MainCategory.objects.get(id=categoryId)
            try:
                category.name_kr = categoryNameKr
                category.name_en = categoryNameEn
                category.save()
            except IntegrityError:
                return JsonResponse({'message':'이미 대분류에 존재하는 카테고리 입니다.'}, status = 400)            
            return JsonResponse({'message' : '수정 완료', 'id':category.id, 'type':'main', 'data':list(MainCategory.objects.all().order_by('name_kr').values('id', 'name_kr', 'name_en'))}, status = 201)
        elif categoryType == 'sub':
            category = SubCategory.objects.get(id=categoryId)
            try:
                category.name_kr = categoryNameKr
                category.name_en = categoryNameEn
                category.save()
            except IntegrityError:
                return JsonResponse({'message':'이미 소분류에 존재하는 카테고리 입니다.'}, status = 400)
            return JsonResponse({'message' : '수정 완료', 'id':category.id, 'type':'sub', 'data':list(category.main_category.sub_category.all().order_by('name_kr').values('id', 'name_kr', 'name_en'))}, status = 201)
        else:
            return JsonResponse({'message':'전달값 오류..'}, status = 400)

    @method_decorator(permission_required(raise_exception=True))
    def delete(self, request: HttpRequest, *args, **kwargs):
        request.DELETE = json.loads(request.body)
        categoryType = request.DELETE['categoryType']
        categoryId = request.DELETE['categoryId']
        if categoryType == 'main':
            category = MainCategory.objects.get(id=categoryId)
            try:
                category.delete()
            except ProtectedError:
                return JsonResponse({'message':'하위 노드들이 있어 삭제 불가능합니다.'}, status = 400)
            return JsonResponse({'message' : '삭제 완료', 'data':list(MainCategory.objects.all().order_by('name_kr').values('id', 'name_kr', 'name_en'))}, status = 200)
        elif categoryType == 'sub':
            category = SubCategory.objects.get(id=categoryId)
            main_category = category.main_category
            try:
                category.delete()
            except ProtectedError:
                return JsonResponse({'message':'하위 노드들이 있어 삭제 불가능합니다.'}, status = 400)
            return JsonResponse({'message' : '삭제 완료', 'data':list(main_category.sub_category.all().order_by('name_kr').values('id', 'name_kr', 'name_en'))}, status = 200)
        else:
            return JsonResponse({'message':'전달값 오류..'}, status = 400)

@require_http_methods(["POST"])
def sub_category(request: HttpRequest):
    '''
    소분류 반환
    '''
    parent_id = request.POST['parent_id']
    try:
        data = list(MainCategory.objects.get(pk=parent_id).sub_category.all().order_by('name_kr').values('id', 'name_kr', 'name_en'))
        return JsonResponse({'data':data, 'type':'sub', 'message':'Sub Category List'}, status = 200)
    except Exception as e:
        return JsonResponse({'message':'데이터 오류..'}, status = 400)
    

@require_http_methods(["POST"])
def category(request: HttpRequest):
    '''
    카테고리 반환
    '''
    main_category = list(MainCategory.objects.all().order_by('name_kr').values('id', 'name_kr', 'name_en'))
    sub_category = list(SubCategory.objects.all().annotate(
        parent_id = F('main_category_id')
    ).order_by('name_kr').values('id', 'parent_id', 'name_kr', 'name_en'))
    
    data = {
        "main_category_list" : main_category,
        "sub_category_list" : sub_category
    }
    return JsonResponse(data, status = 200)