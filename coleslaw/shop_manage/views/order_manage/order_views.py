from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, JsonResponse
from django.db import transaction
from django.views.generic import View
from system_manage.models import Goods, GoodsOption, GoodsOptionDetail
from shop_manage.views.shop_manage_views.auth_views import check_shop

class CheckoutView(View):
    '''
       checkout 
    '''
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return JsonResponse({'message' : '가맹점 오류'},status = 400)

        return JsonResponse({'message' : 'checkout 완료'},status = 202)
    
class OrderCreateView(View):
    '''
        order
    '''
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return JsonResponse({'message' : '가맹점 오류'},status = 400)

        return JsonResponse({'message' : '주문생성되었습니다.'},status = 202)

class OrderCompleteView(View):
    '''
        결제완료
    '''
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return JsonResponse({'message' : '가맹점 오류'},status = 400)

        return JsonResponse({'message' : '완료되었습니다.'},status = 202)