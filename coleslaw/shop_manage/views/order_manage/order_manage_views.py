from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import View
from django.http import HttpRequest, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
from django.db.models import CharField, F, Value as V, Func
from django.utils.decorators import method_decorator
from django.db import transaction
from django.utils import timezone
from system_manage.decorators import permission_required
from system_manage.models import Order
from shop_manage.views.shop_manage_views.auth_views import check_shop

import json, datetime

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

        if request.GET:
            order_date_no = request.GET.get('order_date_no', '0') 
            dates = request.GET.get('dates', '')
            context['dates'] = dates
            if dates != '':
                startDate = dates.split(' - ')[0].strip()
                endDate = dates.split(' - ')[1].strip()
                format = '%m/%d/%Y'

                startDate = datetime.datetime.strptime(startDate, format)
                endDate = datetime.datetime.strptime(endDate, format)
                endDate = datetime.datetime.combine(endDate, datetime.time.max)
                filter_dict['created_at__lte'] = endDate
                filter_dict['created_at__gte'] = startDate
        else:
            order_date_no = '1'
            today = timezone.now().strftime("%m/%d/%Y")
            context['dates'] = f"{today} - {today}"
            filter_dict['date'] = timezone.now().date()
        status_list = ['1', '2', '3', '4', '5']
        filter_dict['status__in'] = status_list
        context['order_date_no'] = order_date_no
        
        if search_keyword:
            context['search_type'] = search_type
            context['search_keyword'] = search_keyword
            filter_dict[search_type + '__icontains'] = search_keyword

        obj_list = Order.objects.filter(**filter_dict).values(
            'id',
            'order_no',
            'order_name',
            'order_code',
            'order_membername',
            'order_phone',
            'final_price',
            'status',
            'created_at'
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

        return render(request, 'order_manage/order_manage.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def put(self, request: HttpRequest, *args, **kwargs):
        request.PUT = json.loads(request.body)
        order_id = request.PUT['order_id']
        order_status = request.PUT['order_status']
        status = ['1', '3', '4', '5']
        try:
            order = Order.objects.get(pk=order_id)
        except:
            return JsonResponse({'message' : '데이터 오류'},  status = 400)
        if order_status not in status:
            return JsonResponse({'message' : '상태 값 오류'},  status = 400)
        order.status = order_status
        order.save()
        
        return JsonResponse({'message' : '수정되었습니다.'},status = 200)
    