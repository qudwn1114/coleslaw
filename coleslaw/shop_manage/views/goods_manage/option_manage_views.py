from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, JsonResponse
from django.db import transaction
from django.views.generic import View
from django.utils.decorators import method_decorator
from system_manage.decorators import permission_required
from system_manage.models import Goods, GoodsOption, GoodsOptionDetail
from shop_manage.views.shop_manage_views.auth_views import check_shop

import json

class OptionManageView(View):
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
        pk = kwargs.get("pk")
        goods = get_object_or_404(Goods, pk=pk)
        context['goods'] = goods

        return render(request, 'goods_manage/option_manage.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return JsonResponse({'message' : '가맹점 오류'},status = 400)
        pk = kwargs.get("pk")
        try:
            goods= Goods.objects.get(pk=pk)
        except:
            return JsonResponse({'message' : '데이터 오류'},  status = 400)
        
        option_name = request.POST['option_name']
        option_detail = request.POST['option_detail']
        option_detail_list = option_detail.split(',')
        option_detail_list = [i.strip() for i in option_detail_list]
        option_count = goods.option.all().count()
        if len(option_detail_list) > 20:
            return JsonResponse({'message' : '옵션내용은 20개 까지 가능합니다.'},  status = 400)
        if option_count >=5:
            return JsonResponse({'message' : '더 이상 옵션을 등록 하실 수 없습니다.'},  status = 400)
        try:
            with transaction.atomic():
                goods_option = GoodsOption.objects.create(
                    goods=goods,
                    name = option_name.strip()
                )
                bulk_list = []
                for i in option_detail_list:
                    bulk_list.append(GoodsOptionDetail(goods_option=goods_option, name=i))
                GoodsOptionDetail.objects.bulk_create(bulk_list)
        except:
            return JsonResponse({'message' : '등록 에러'},  status = 400)
        
        return JsonResponse({'message' : '등록되었습니다.'},status = 202)
    
    @method_decorator(permission_required(raise_exception=True))
    def put(self, request: HttpRequest, *args, **kwargs):
        request.PUT = json.loads(request.body)
        option_id = request.PUT['option_id']
        try:
            goods_option = GoodsOption.objects.get(pk=option_id)
        except:
            return JsonResponse({'message' : '데이터 오류'},  status = 400)
        goods_option.required = not goods_option.required
        goods_option.save()
        
        return JsonResponse({'message' : '수정되었습니다.'},status = 200)
    
    @method_decorator(permission_required(raise_exception=True))
    def delete(self, request: HttpRequest, *args, **kwargs):
        request.DELETE = json.loads(request.body)
        option_id = request.DELETE['option_id']
        try:
            goods_option = GoodsOption.objects.get(pk=option_id)
        except:
            return JsonResponse({'message' : '데이터 오류'},  status = 400)
        goods_option.delete()
        
        return JsonResponse({'message' : '삭제되었습니다.'},status = 200)


class OptionDetailManageView(View):
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
            goods_option = GoodsOption.objects.get(pk=option_id)
        except:
            return JsonResponse({'message' : '데이터 오류'},  status = 400)
        
        option_detail_count = goods_option.option_detail.all().count()
        if option_detail_count >= 20:
            return JsonResponse({'message' : '옵션내용은 20개 까지 가능합니다.'},  status = 400)
        GoodsOptionDetail.objects.create(
            goods_option=goods_option,
            name=f'내용{option_detail_count+1}'
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
            option_price = request.PUT['option_price']
            option_stock = request.PUT['option_stock']
            try:
                goods_option_detail = GoodsOptionDetail.objects.get(pk=option_detail_id)
            except:
                return JsonResponse({'message' : '데이터 오류'},  status = 400)
            goods_option_detail.name = option_name
            goods_option_detail.price = option_price
            if goods_option_detail.stock_flag:
                goods_option_detail.stock = option_stock
            goods_option_detail.save()
        elif rq_type == 'STOCK_FLAG':
            option_detail_id = request.PUT['option_detail_id']
            try:
                goods_option_detail = GoodsOptionDetail.objects.get(pk=option_detail_id)
            except:
                return JsonResponse({'message' : '데이터 오류'},  status = 400)
            goods_option_detail.stock_flag = not goods_option_detail.stock_flag
            goods_option_detail.save()
        elif rq_type == 'SOLD_OUT':
            option_detail_id = request.PUT['option_detail_id']
            try:
                goods_option_detail = GoodsOptionDetail.objects.get(pk=option_detail_id)
            except:
                return JsonResponse({'message' : '데이터 오류'},  status = 400)
            goods_option_detail.soldout = not goods_option_detail.soldout
            goods_option_detail.save()
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
            goods_option_detail = GoodsOptionDetail.objects.get(pk=option_detail_id)
        except:
            return JsonResponse({'message' : '데이터 오류'},  status = 400)
        goods_option_detail.delete()
        
        return JsonResponse({'message' : '삭제되었습니다.'},status = 200)
