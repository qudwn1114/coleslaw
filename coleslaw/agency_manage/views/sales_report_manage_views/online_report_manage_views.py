from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View
from django.http import HttpRequest, JsonResponse
from django.http.response import HttpResponse

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.db.models import CharField, F, Value as V, Func, Case, When, Prefetch, Sum, Q

from system_manage.utils import ResponseToXlsx
from system_manage.decorators import permission_required
from agency_manage.views.agency_manage_views.auth_views import check_agency
from system_manage.models import OrderPayment, Shop
from dateutil.relativedelta import relativedelta
import datetime, pandas
from openpyxl import Workbook
import urllib.parse

class AgencyOnlineReportManage(View):
    '''
        에이전시 가맹점 별 온라인 판매현황
    '''
    @method_decorator(permission_required(redirect_url='agency_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        agency_id = kwargs.get('agency_id')
        agency = check_agency(pk=agency_id)
        if not agency:
            return redirect('agency_manage:notfound')
        context['agency'] = agency

        condition = request.GET.get('condition', '')

        shop = Shop.objects.filter(agency=agency, tbridge=True).values('id', 'name_kr').order_by('name_kr')
        context['shop'] = shop

        if condition:
            order_date_no = request.GET.get('order_date_no', '0') 
            dates = request.GET.get('dates', '')
            context['dates'] = dates
            startDate = dates.split(' - ')[0].strip()
            endDate = dates.split(' - ')[1].strip()
            format = '%m/%d/%Y'
            startDate = datetime.datetime.strptime(startDate, format).date()
            endDate = datetime.datetime.strptime(endDate, format).date()
            if startDate < endDate - relativedelta(months=3):
                raise Exception('3달 이상은 안됩니다!')
            date_list = pandas.date_range(startDate, endDate, freq='d')
            date_name = f"{startDate} ~ {endDate}"
            shop_id_list = request.GET.getlist('shop', None) 
            shop_id_list = list(map(int, shop_id_list))
        else:
            order_date_no = '1'
            today = timezone.now()
            context['dates'] = f'{today.strftime("%m/%d/%Y")} - {today.strftime("%m/%d/%Y")}'
            date_list = [today]
            date_name = f"{today.date()} ~ {today.date()}"
            shop_id_list = list(shop.values_list('id', flat=True))

        context['date_name'] = date_name
        context['order_date_no'] = order_date_no

        shop = Shop.objects.filter(agency=agency, tbridge=True, id__in=shop_id_list).values('id', 'name_kr').order_by('name_kr')
        context['shop_id_list'] = shop_id_list

        return render(request, 'agency_sales_report_manage/online_report_manage.html', context)
