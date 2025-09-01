from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import View
from django.http import HttpRequest, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from system_manage.decorators import permission_required
from shop_manage.views.shop_manage_views.auth_views import check_shop
from system_manage.models import ShopCoupon
import json

class ShopCouponManageView(View):
    '''
        가맹점 쿠폰 관리
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

        obj_list = ShopCoupon.objects.filter(**filter_dict).values(
            'id',
            'name',
            'expiration_period',
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

        return render(request, 'coupon_manage/coupon_manage.html', context)
    

class ShopCouponCreateView(View):
    '''
        가맹점 쿠폰 등록
    '''
    @method_decorator(permission_required(redirect_url='shop_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return redirect('shop_manage:notfound')
        context['shop'] = shop

        return render(request, 'coupon_manage/coupon_create.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return JsonResponse({'message': _('ERR_DATA_INVALID')}, status=400)
        
        coupon_name = request.POST['coupon_name'].strip()
        expiration_period = int(request.POST['expiration_period'])

        shop_coupon = ShopCoupon.objects.create(shop=shop, name=coupon_name, expiration_period=expiration_period)
        
        return JsonResponse({'message' : _('MSG_CREATED'), 'url':reverse('shop_manage:coupon_detail', kwargs={'shop_id':shop.id, 'pk': shop_coupon.pk})},  status = 201)
    

class ShopCouponDetailView(View):
    '''
        가맹점 쿠폰 상세
    '''
    @method_decorator(permission_required(redirect_url='shop_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        shop_id = kwargs.get('shop_id')
        pk = kwargs.get('pk')
        shop = check_shop(pk=shop_id)
        if not shop:
            return redirect('shop_manage:notfound')
        context['shop'] = shop

        shop_coupon = get_object_or_404(ShopCoupon, pk=pk, shop=shop)
        context['shop_coupon'] = shop_coupon

        return render(request, 'coupon_manage/coupon_detail.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def delete(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        pk = kwargs.get("pk")
        shop = check_shop(pk=shop_id)
        if not shop:
            return JsonResponse({'message': _('ERR_DATA_INVALID')}, status=400)
        
        try:
            shop_coupon= ShopCoupon.objects.get(pk=pk, shop=shop)
        except:
            return JsonResponse({'message': _('ERR_DATA_INVALID')}, status=400)
        
        shop_coupon.delete()
        
        return JsonResponse({'message' : _('MSG_DELETED'), 'url':reverse('shop_manage:coupon_manage', kwargs={'shop_id':shop.id})},  status = 202)


class ShopCouponEditView(View):
    '''
        가맹점 쿠폰 수정
    '''
    @method_decorator(permission_required(redirect_url='shop_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        shop_id = kwargs.get('shop_id')
        pk = kwargs.get('pk')
        shop = check_shop(pk=shop_id)
        if not shop:
            return redirect('shop_manage:notfound')
        context['shop'] = shop

        shop_coupon = get_object_or_404(ShopCoupon, pk=pk, shop=shop)
        context['shop_coupon'] = shop_coupon

        return render(request, 'coupon_manage/coupon_edit.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        pk = kwargs.get("pk")
        shop = check_shop(pk=shop_id)
        if not shop:
            return JsonResponse({'message': _('ERR_DATA_INVALID')}, status=400)
        
        try:
            shop_coupon= ShopCoupon.objects.get(pk=pk, shop=shop)
        except:
            return JsonResponse({'message': _('ERR_DATA_INVALID')}, status=400)
        
        coupon_name = request.POST['coupon_name'].strip()
        expiration_period = int(request.POST['expiration_period'])

        shop_coupon.name= coupon_name
        shop_coupon.expiration_period=expiration_period
        shop_coupon.save()
        
        return JsonResponse({'message' : _('MSG_UPDATED'), 'url':reverse('shop_manage:coupon_detail', kwargs={'shop_id':shop.id, 'pk': shop_coupon.pk})},  status = 201)
