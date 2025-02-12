from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import View
from django.http import HttpRequest, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
from django.db.models import Case, When, Value, IntegerField, CharField
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from system_manage.decorators import permission_required
from shop_manage.views.shop_manage_views.auth_views import check_shop
from system_manage.utils import ResponseToXlsx
from system_manage.models import SmsLog, Shop

from dateutil.relativedelta import relativedelta
import datetime

class SMSManageManageView(View):
    '''
        알림톡 관리
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

        condition = request.GET.get('condition', '')
        excel = request.GET.get('excel', None)

        if condition:
            order_date_no = request.GET.get('order_date_no', '0') 
            dates = request.GET.get('dates', '')
            context['dates'] = dates
            startDate = dates.split(' - ')[0].strip()
            endDate = dates.split(' - ')[1].strip()
            format = '%m/%d/%Y'
            startDate = datetime.datetime.strptime(startDate, format)
            endDate = datetime.datetime.strptime(endDate, format)
            endDate = endDate.replace(hour=23, minute=59, second=59, microsecond=999999)
            if startDate <= endDate - relativedelta(months=3, days=1):
                raise Exception('3달 이상은 안됩니다!')
            
            agency_id_list = request.GET.getlist('agency', None) 
            agency_id_list = list(map(int, agency_id_list))
        else:
            order_date_no = '1'
            today = timezone.now()
            startDate = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            endDate = today.replace(hour=23, minute=59, second=59, microsecond=999999)
            context['dates'] = f'{startDate.strftime("%m/%d/%Y")} - {today.strftime("%m/%d/%Y")}'

        context['order_date_no'] = order_date_no
        filter_dict = {}
        filter_dict['shop'] = shop
        filter_dict['created_at__lte'] = endDate
        filter_dict['created_at__gte'] = startDate

        obj_list = SmsLog.objects.filter(**filter_dict).annotate(
            price=Case(
                When(message_type='0', then=Value(15)),
                When(message_type='1', then=Value(15)),
                default=Value(0),  # 기본값 설정 (필요하면 변경)
                output_field=IntegerField()
            ),
            messageType = Case(
                When(message_type='0', then=Value('SMS')),
                When(message_type='1', then=Value('알림톡')),
                default=Value('오류'),  # 기본값 설정 (필요하면 변경)
                output_field=CharField()
            )
        ).values(
            'id',
            'messageType',
            'message',
            'price',
            'created_at'
        ).order_by('-id')

        if excel:
            filename = f"SMS Log"
            columns = ['ID', '메세지타입', '메세지', '가격', '날짜']
            xlsx_download = ResponseToXlsx(columns=columns, queryset=obj_list)
            return xlsx_download.download(filename=filename)

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
        context['sms'] = obj_list.filter(message_type='0').count()  * 15
        context['kakao'] = obj_list.filter(message_type='1').count() * 15
        context['total'] = obj_list.count()

        return render(request, 'sms_manage/sms_manage.html', context)