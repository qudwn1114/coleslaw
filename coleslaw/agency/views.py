from django.shortcuts import render, redirect, resolve_url, get_object_or_404
from django.contrib.auth import login
from django.urls import reverse
from django.views.generic import View
from django.http import HttpRequest, JsonResponse

from django.utils.decorators import method_decorator
from system_manage.decorators import  permission_required
from system_manage.models import Agency, AgencyShop, Checkout, Order


# Create your views here.
class AgencyHomeView(View):
    '''
        agency main
    '''
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        agency_id = kwargs.get('agency_id')
        agency = get_object_or_404(Agency, pk=agency_id)
        context['agency'] = agency
        
        return render(request, 'agency/index.html', context)
    

class AgencyShopListView(View):
    '''
        agency shop list
    '''
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        agency_id = kwargs.get('agency_id')
        agency = get_object_or_404(Agency, pk=agency_id)
        context['agency'] = agency
        
        return render(request, 'agency/franchisee.html', context)
    

class AgencyShopView(View):
    '''
        agency shop
    '''
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        agency_shop_id = kwargs.get('agency_shop_id')
        agency_shop = get_object_or_404(AgencyShop, pk=agency_shop_id)
        context['agency_shop'] = agency_shop
        
        return render(request, 'agency/menus.html', context)

class AgencyBasketView(View):
    '''
        agency basket
    '''
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        agency_id = kwargs.get('agency_id')
        agency = get_object_or_404(Agency, pk=agency_id)
        context['agency'] = agency
        
        return render(request, 'agency/basket.html', context)    

class AgencyShopCheckoutView(View):
    '''
        agency checkout
    '''
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        agency_shop_id = kwargs.get('agency_shop_id')
        code = kwargs.get('code')
        agency_shop = get_object_or_404(AgencyShop, pk=agency_shop_id)
        checkout = get_object_or_404(Checkout, shop=agency_shop.shop, code=code)
        context['agency_shop'] = agency_shop
        context['checkout'] = checkout
        
        return render(request, 'agency/information.html', context)
    
class AgencyShopOrderCompleteView(View):
    '''
        agency order complete
    '''
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        agency_shop_id = kwargs.get('agency_shop_id')
        order_id = kwargs.get('order_id')
        agency_shop = get_object_or_404(AgencyShop, pk=agency_shop_id)
        order = get_object_or_404(Order, pk=order_id, shop=agency_shop.shop)
        context['agency_shop'] = agency_shop
        context['order'] = order
        
        return render(request, 'agency/complete.html', context)