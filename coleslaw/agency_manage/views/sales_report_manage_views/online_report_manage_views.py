from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View
from django.http import HttpRequest, JsonResponse
from django.http.response import HttpResponse

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.db.models import CharField, F, Value as V, Func, Case, When, Prefetch, Sum, Q

from system_manage.decorators import permission_required
from agency_manage.views.agency_manage_views.auth_views import check_agency
from system_manage.models import OrderPayment, Shop
from dateutil.relativedelta import relativedelta
import datetime, requests
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
        excel = request.GET.get('excel', None)

        shop = Shop.objects.filter(agency=agency, tbridge=True).values('id', 'name_kr').order_by('id')
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
            date_name = f"{startDate} ~ {endDate}"
            shop_id_list = request.GET.getlist('shop', None) 
            shop_id_list = list(map(int, shop_id_list))
        else:
            order_date_no = '1'
            today = timezone.now()
            startDate = today.date()
            endDate = today.date()
            context['dates'] = f'{today.strftime("%m/%d/%Y")} - {today.strftime("%m/%d/%Y")}'
            date_name = f"{today.date()} ~ {today.date()}"
            shop_id_list = list(shop.values_list('id', flat=True))

        shop_id_list_string = ','.join(map(str, shop_id_list))

        URL = f'https://baumrootme.com/webpos/php/api/v1/agency_report.php'
        params = {'shop_id':shop_id_list_string, 'start_date':startDate, 'end_date':endDate}
        response = requests.get(URL, params=params)
        response_data = response.json()['list']

        sum_sale_amount = 0
        sum_cancel_amount = 0
        sum_total_amount = 0
        sum_confirm_amount = 0

        shop_total_dict = {}
        for i in shop_id_list:
            shop_total_dict[f'{i}'] = {'sale_amount':0, 'cancel_amount':0, 'total_amount':0, 'confirm_amount':0}

        for i in response_data:
            if i['shop_id'].isdigit():
                s = shop_total_dict.get(i['shop_id'])
                s['sale_amount'] += i['sale_amount']
                s['cancel_amount'] += i['cancel_amount']
                s['total_amount'] += i['total_amount']
                s['confirm_amount'] += i['confirm_amount']
                i['shop_id'] = shop.get(id=i['shop_id'])['name_kr']
                i['date'] = datetime.datetime.strptime(i['date'], '%Y-%m-%d').date()
            else:
                i['date'] = ''
        for k, v in shop_total_dict.items():
            sum_sale_amount += v['sale_amount']
            sum_cancel_amount += v['cancel_amount']
            sum_total_amount += v['total_amount']
            sum_confirm_amount += v['confirm_amount']
            response_data.append({'shop_id':shop.get(id=k)['name_kr'], 'date':'설정기간', 'sale_amount':v['sale_amount'], 'cancel_amount':v['cancel_amount'], 'total_amount':v['total_amount'], 'confirm_amount':v['confirm_amount']})
        
        response_data.append({'shop_id':'전체합계', 'date':'', 'sale_amount':sum_sale_amount, 'cancel_amount':sum_cancel_amount, 'total_amount':sum_total_amount, 'confirm_amount':sum_confirm_amount})


        if excel:
            filename = f"{agency.name} {date_name} 가맹점 별 온라인 판매 매출"
            headers = ['일자별', '가맹점', '판매금액', '취소금액', '합계', '확정금액']
            response = HttpResponse(content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'%s.xlsx' % urllib.parse.quote(filename.encode('utf-8'))
            wb = Workbook()
            ws = wb.active
            ws.title = "가맹점 별 온라인 판매 매출"
            # Add headers
            ws.append(headers)
            for i in response_data:
                ws.append([i["date"], i["shop_id"], i['sale_amount'],i['cancel_amount'], i['total_amount'], i['confirm_amount']])
            wb.save(response)
            return response

        context['date_name'] = date_name
        context['order_date_no'] = order_date_no
        context['shop_id_list'] = shop_id_list
        context['online_report_list'] = response_data
        context['sum_total_amount'] = sum_total_amount

        return render(request, 'agency_sales_report_manage/online_report_manage.html', context)
