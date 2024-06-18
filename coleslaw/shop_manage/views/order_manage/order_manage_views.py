from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import View
from django.http import HttpRequest, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
from django.db.models import CharField, F, Value as V, Func
from django.utils.decorators import method_decorator
from django.db import transaction
from system_manage.decorators import permission_required
from system_manage.models import Order
from shop_manage.views.shop_manage_views.auth_views import check_shop

import json

class OrderManageView(View):
    '''
        주문내역 관리 화면
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

        obj_list = Order.objects.filter(**filter_dict).annotate(
            createdAt=Func(
                F('created_at'),
                V('%y.%m.%d %H:%i'),
                function='DATE_FORMAT',
                output_field=CharField()
            )
        ).values(
            'id',
            'order_name',
            'order_code',
            'order_phone',
            'final_price',
            'status',
            'createdAt'
        ).order_by('-created_at')

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

        return render(request, 'shop_manage/order_manage.html', context)
    