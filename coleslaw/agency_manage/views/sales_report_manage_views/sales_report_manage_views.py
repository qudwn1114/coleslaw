from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View
from django.http import HttpRequest, JsonResponse
from django.http.response import HttpResponse

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.db.models import CharField, F, Value as V, Func, Case, When, Prefetch, Sum

from system_manage.utils import ResponseToXlsx
from system_manage.decorators import permission_required
from agency_manage.views.agency_manage_views.auth_views import check_agency
from system_manage.models import OrderPayment, Shop
import datetime, calendar
from openpyxl import Workbook
import urllib.parse



class AgencySalesReportManage(View):
    '''
        에이전시 가맹점 별 판매현황
    '''
    @method_decorator(permission_required(redirect_url='agency_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        agency_id = kwargs.get('agency_id')
        agency = check_agency(pk=agency_id)
        if not agency:
            return redirect('agency_manage:notfound')
        context['agency'] = agency

        year_month = request.GET.get('year_month', '')
        excel = request.GET.get('excel', None)

        filter_dict = {}
        filter_dict['order__agency'] = agency
        if year_month:
            try:
                datetime.datetime.strptime(year_month, '%Y-%m')
            except Exception as e:
                raise ValueError(e) 
        else:
            year_month = timezone.now().strftime('%Y-%m')

        context['year_month'] = year_month
        year = int(year_month.split('-')[0])
        month = int(year_month.split('-')[1])

        #이번달
        if year_month == timezone.now().strftime('%Y-%m'):
            days = int(timezone.now().day)
        #이번달 이후
        elif timezone.now() < datetime.datetime.strptime(year_month, '%Y-%m'):
            days = 0
        #지난달
        else:
            days = calendar.monthrange(year=year, month=month)[1]

        shop_list = Shop.objects.filter(agency=agency).values('id', 'name_kr').order_by('name_kr')
        sales_report_list = []
        sum_total_price = 0
        if shop_list:
            for i in range(1,  days+1):
                d = datetime.datetime.strptime(f"{year_month}-{format(i, '02')}", '%Y-%m-%d')
                filter_dict['status']=True
                filter_dict['order__date'] = d
                queryset = OrderPayment.objects.filter(**filter_dict).values(
                    'order__shop_id',
                    'payment_method',
                ).annotate(
                    total_sale_price=Sum("amount")
                ).order_by('order__shop_id')
                for j in shop_list:
                    new_queryset = queryset.filter(order__shop_id=j['id'])
                    total = 0 
                    card = 0
                    cash = 0
                    for k in new_queryset:
                        if k['payment_method'] == '0':
                            card = k['total_sale_price']
                        elif k['payment_method'] == '1':
                            cash = k['total_sale_price']
                        total += k['total_sale_price']
                    sales_report_list.append({"date":d, "name_kr": j['name_kr'], "card":card, "cash": cash, "total": total})

                    sum_total_price += total

                sales_report_list.append({"date":"", "name_kr":"", "card":"", "cash":"", "total":""})
        
        if excel:
            filename = f"{agency.name} {year_month} 가맹점 별 매출"
            headers = ['일자별', '가맹점', '카드매출', '현금매출', '합계']
            response = HttpResponse(content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'%s.xlsx' % urllib.parse.quote(filename.encode('utf-8'))
            wb = Workbook()
            ws = wb.active
            ws.title = "가맹점 별 매출"
            # Add headers
            ws.append(headers)

            for i in sales_report_list:
                ws.append([i["date"], i["name_kr"], i['card'], i['cash'], i['total']])
            wb.save(response)
            return response

        context['sum_total_price'] = sum_total_price
        context['sales_report_list'] = sales_report_list

        return render(request, 'agency_sales_report_manage/sales_report_manage.html', context)