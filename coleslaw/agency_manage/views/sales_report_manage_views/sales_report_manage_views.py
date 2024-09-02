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

        shop_list = Shop.objects.filter(agency=agency).annotate(
            card=V(0),
            cash1=V(0),
            cash2=V(0),
            total=V(0),
        ).values('id', 'name_kr', 'card', 'cash1', 'cash2', 'total').order_by('name_kr')
        sales_report_list = []

        sum_card_price = 0
        sum_cash1_price = 0
        sum_cash2_price = 0
        sum_total_price = 0

        if shop_list:
            for i in range(1,  days+1):
                d = f"{year_month}-{format(i, '02')}"
                filter_dict['status']=True
                filter_dict['amount__gt']=0
                filter_dict['order__date'] = d
                queryset = OrderPayment.objects.filter(**filter_dict).annotate(
                    paymentMethod = Case(
                        When(payment_method='0', then=V('0')),
                        When(Q(payment_method='1') & Q(approvalNumber=''), then=V('1')),
                        When(Q(payment_method='1'), then=V('1-1')),
                        default=V('0'), output_field=CharField()
                    ),
                ).values(
                    'order__shop_id',
                    'paymentMethod',
                ).annotate(
                    total_sale_price=Sum("amount")
                ).order_by('order__shop_id')
                day_total = 0 
                day_card = 0
                day_cash1 = 0
                day_cash2 = 0
                for j in shop_list:
                    new_queryset = queryset.filter(order__shop_id=j['id'])
                    total = 0 
                    card = 0
                    cash1 = 0
                    cash2 = 0
                    for k in new_queryset:
                        if k['paymentMethod'] == '0':
                            card = k['total_sale_price']
                            day_card += card
                            j['card'] += card
                        elif k['paymentMethod'] == '1':
                            cash1 = k['total_sale_price']
                            day_cash1 += cash1
                            j['cash1'] += cash1
                        elif k['paymentMethod'] == '1-1':
                            cash2 = k['total_sale_price']
                            day_cash2 += cash2
                            j['cash2'] += cash2

                        _total = k['total_sale_price']
                        total += _total
                        day_total += _total
                        j['total'] += _total

                    sales_report_list.append({"date":d, "name_kr": j['name_kr'], "card":card, "cash1": cash1, "cash2": cash2, "total": total})
                sales_report_list.append({"date":"", "name_kr":"합계", "card":day_card, "cash1":day_cash1, "cash2": day_cash2, "total":day_total}) 

            for i in shop_list:
                sum_card_price += i['card']
                sum_cash1_price += i['cash1']
                sum_cash2_price += i['cash2']
                sum_total_price += i['total']
                sales_report_list.append({"date":year_month, "name_kr":i['name_kr'], "card":i['card'], "cash1":i['cash1'], "cash2": i['cash2'], "total":i['total']}) 

            sales_report_list.append({"date":"", "name_kr":"전체합계", "card":sum_card_price, "cash1":sum_cash1_price, "cash2":sum_cash2_price, "total":sum_total_price}) 

        if excel:
            filename = f"{agency.name} {year_month} 가맹점 별 매출"
            headers = ['일자별', '가맹점', '카드매출', '현금매출(O)', '현금매출(X)', '합계']
            response = HttpResponse(content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'%s.xlsx' % urllib.parse.quote(filename.encode('utf-8'))
            wb = Workbook()
            ws = wb.active
            ws.title = "가맹점 별 매출"
            # Add headers
            ws.append(headers)

            for i in sales_report_list:
                ws.append([i["date"], i["name_kr"], i['card'], i['cash1'], i['cash2'], i['total']])
            wb.save(response)
            return response

        context['sum_total_price'] = sum_total_price
        context['sales_report_list'] = sales_report_list

        return render(request, 'agency_sales_report_manage/sales_report_manage.html', context)