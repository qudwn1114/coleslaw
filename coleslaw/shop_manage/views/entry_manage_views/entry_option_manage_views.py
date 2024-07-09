from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, JsonResponse
from django.db import transaction
from django.views.generic import View
from django.utils.decorators import method_decorator
from system_manage.decorators import permission_required
from system_manage.models import ShopEntryOption, ShopEntryOptionDetail
from shop_manage.views.shop_manage_views.auth_views import check_shop

import json, traceback

class ShopEntryOptionManageView(View):
    '''
        옵션관리
    '''
    @method_decorator(permission_required(redirect_url='shop_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return redirect('shop_manage:notfound')
        context['shop'] = shop

        return render(request, 'entry_manage/entry_option_manage.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return JsonResponse({'message' : '가맹점 오류'},status = 400)
        
        option_name = request.POST['option_name']
        option_detail = request.POST['option_detail']
        option_detail_list = option_detail.split(',')
        option_detail_list = [i.strip() for i in option_detail_list]
        option_count = ShopEntryOption.objects.filter(shop=shop).count()
        if len(option_detail_list) > 5:
            return JsonResponse({'message' : '옵션내용은 5개 까지 가능합니다.'},  status = 400)
        if option_count >=5:
            return JsonResponse({'message' : '더 이상 옵션을 등록 하실 수 없습니다.'},  status = 400)
        try:
            with transaction.atomic():
                shop_entry_option = ShopEntryOption.objects.create(
                    shop=shop,
                    name = option_name.strip()
                )
                bulk_list = []
                for i in option_detail_list:
                    bulk_list.append(ShopEntryOptionDetail(shop_entry_option=shop_entry_option, name=i, image='image/goods/default.jpg'))
                ShopEntryOptionDetail.objects.bulk_create(bulk_list)
        except:
            return JsonResponse({'message' : '등록 에러'},  status = 400)
        
        return JsonResponse({'message' : '등록되었습니다.'},status = 202)
    
    @method_decorator(permission_required(raise_exception=True))
    def put(self, request: HttpRequest, *args, **kwargs):
        request.PUT = json.loads(request.body)
        option_id = request.PUT['option_id']
        try:
            shop_entry_option = ShopEntryOption.objects.get(pk=option_id)
        except:
            return JsonResponse({'message' : '데이터 오류'},  status = 400)
        shop_entry_option.required = not shop_entry_option.required
        shop_entry_option.save()
        
        return JsonResponse({'message' : '수정되었습니다.'},status = 200)
    
    @method_decorator(permission_required(raise_exception=True))
    def delete(self, request: HttpRequest, *args, **kwargs):
        request.DELETE = json.loads(request.body)
        option_id = request.DELETE['option_id']
        try:
            shop_entry_option = ShopEntryOption.objects.get(pk=option_id)
        except:
            return JsonResponse({'message' : '데이터 오류'},  status = 400)
        shop_entry_option.delete()
        
        return JsonResponse({'message' : '삭제되었습니다.'},status = 200)


class ShopEntryOptionDetailManageView(View):
    '''
        옵션상세관리
    '''
    @method_decorator(permission_required(raise_exception=True))
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return JsonResponse({'message' : '가맹점 오류'},status = 400)
        option_id = request.POST['option_id']
        try:
            shop_entry_option = ShopEntryOption.objects.get(pk=option_id)
        except:
            return JsonResponse({'message' : '데이터 오류'},  status = 400)
        
        option_detail_count = shop_entry_option.entry_option_detail.all().count()
        if option_detail_count >= 5:
            return JsonResponse({'message' : '옵션내용은 20개 까지 가능합니다.'},  status = 400)
        ShopEntryOptionDetail.objects.create(
            shop_entry_option=shop_entry_option,
            name=f'내용{option_detail_count+1}',
            image='image/goods/default.jpg'
        )

        return JsonResponse({'message' : '등록되었습니다.'},status = 202)
    
    @method_decorator(permission_required(raise_exception=True))
    def put(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return JsonResponse({'message' : '가맹점 오류'},status = 400)
        request.PUT = json.loads(request.body)
        rq_type = request.PUT['type']
        if rq_type == 'DETAIL':
            option_detail_id = request.PUT['option_detail_id']
            option_name = request.PUT['option_name']
            try:
                shop_entry_option_detail = ShopEntryOptionDetail.objects.get(pk=option_detail_id)
            except:
                return JsonResponse({'message' : '데이터 오류'},  status = 400)
            shop_entry_option_detail.name = option_name
            shop_entry_option_detail.save()
        else:
            return JsonResponse({'message' : 'TYPE ERROR'},status = 400)
        
        return JsonResponse({'message' : '수정되었습니다.'},status = 201)

    
    @method_decorator(permission_required(raise_exception=True))
    def delete(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return JsonResponse({'message' : '가맹점 오류'},status = 400)
        request.DELETE = json.loads(request.body)
        option_detail_id = request.DELETE['option_detail_id']
        try:
            shop_entry_option_detail = ShopEntryOptionDetail.objects.get(pk=option_detail_id)
        except:
            return JsonResponse({'message' : '데이터 오류'},  status = 400)
        shop_entry_option_detail.delete()
        
        return JsonResponse({'message' : '삭제되었습니다.'},status = 200)


class ShopEntryOptionDetailImageView(View):
    '''
        이미지 등록
    '''
    @method_decorator(permission_required(raise_exception=True))
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return JsonResponse({'message' : '가맹점 오류'},status = 400)
        option_detail_id = request.POST['option_detail_id']
        image = request.FILES.get('image', None)

        print(option_detail_id)

        try:
            shop_entry_option_detail = ShopEntryOptionDetail.objects.get(pk=option_detail_id, shop_entry_option__shop=shop)
        except:
            return JsonResponse({'message' : '데이터 오류'},  status = 400)
        
        if not image:
            return JsonResponse({'message' : '이미지를 넣어주세요.'},status = 400)

        shop_entry_option_detail.image = image
        shop_entry_option_detail.save()

        return JsonResponse({'message' : '등록되었습니다.'},status = 202)