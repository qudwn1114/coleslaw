from django.shortcuts import render, redirect, resolve_url
from django.contrib.auth import login
from django.urls import reverse
from django.views.generic import View, TemplateView
from django.http import HttpRequest, JsonResponse
from django.db.models import F, Sum, Value as V, Func, CharField
from django.db.models.functions import Coalesce, TruncMonth, TruncHour
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.contrib.auth import update_session_auth_hash
from django.utils.decorators import method_decorator
from system_manage.decorators import  permission_required
from system_manage.models import Agency, AgencyAdmin, Order

from dateutil.relativedelta import relativedelta
import datetime


# Create your views here.
class HomeView(View):
    '''
        agency 관리자 메인 화면
    '''
    @method_decorator(permission_required(redirect_url='shop_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        agency_id = kwargs.get('agency_id')
        agency = check_agency(pk=agency_id)
        if not agency:
            return redirect('agency_manage:notfound')
        context['agency'] = agency
        
        return render(request, 'agency_admin_manage/agency_manage_main.html', context)

@require_http_methods(["GET"])
def agency_main_sales(request: HttpRequest, *args, **kwargs):
    '''
        판매현황
    '''
    agency_id = kwargs.get('agency_id')
    agency = check_agency(pk=agency_id)
    if not agency:
        return JsonResponse({}, status = 400)

    daily_order = Order.objects.filter(agency=agency, date=timezone.now().date()).exclude(status='0')
    card_sales = daily_order.filter(payment_method="0")
    cash_sales = daily_order.filter(payment_method="1")
    cancel_sales = daily_order.filter(status='2')
    total_sales = daily_order.all().exclude(status='2')

    data = {
        'card_sales' : card_sales.aggregate(sum=Coalesce(Sum('final_price'), 0)).get('sum'),
        'card_count' : card_sales.count(),
        'cash_sales' : cash_sales.aggregate(sum=Coalesce(Sum('final_price'), 0)).get('sum'),
        'cash_count' : cash_sales.count(),
        'cancel_sales' : cancel_sales.aggregate(sum=Coalesce(Sum('final_price'), 0)).get('sum'),
        'cancel_count' : cancel_sales.count(),
        'total_sales' : total_sales.aggregate(sum=Coalesce(Sum('final_price'), 0)).get('sum'),
        'total_count' : total_sales.count()
    }
    return JsonResponse(data, status = 200)


@require_http_methods(["GET"])
def agency_sales_report(request: HttpRequest, *args, **kwargs):
    '''
        판매현황
    '''
    agency_id = kwargs.get('agency_id')
    agency = check_agency(pk=agency_id)
    if not agency:
        return JsonResponse({}, status = 400)
    data = {}
    report_type = request.GET.get('report_type', 'TODAY')
    today = timezone.now().date()
    dates = {}
    if report_type == 'TODAY':        
        order = Order.objects.filter(agency=agency, date=today).exclude(status__in=['0','2']).annotate(hour=TruncHour('updated_at')).values('hour').annotate(sum=Sum('final_price')).values('hour', 'sum').order_by('hour')
        max_hour =  timezone.now().hour
        for i in range(max_hour+1):
            dates[f"{format(i, '02')}"] = 0
        for i in range(max_hour+1, 24):
            dates[f"{format(i, '02')}"] = None
        for i in order:
            dates[i['hour'].strftime('%H')] = i['sum']
        series_data = []
        for k, v in dates.items():
            x = f"{k}시"
            y = v
            series_data.append({"x":x, "y":y})

        data['title'] = '일 매출'
        data['title_en'] = 'Today'
        data['series_data'] =  series_data

    elif report_type == 'WEEK':
        week = ['월','화','수','목','금','토','일']
        days = 8
        start_date = today - datetime.timedelta(days=days-1)
        end_date = today
        for i in range(days):
            dates[start_date + datetime.timedelta(days=i)] = 0
        order = Order.objects.filter(agency=agency, date__range=[start_date, end_date]).exclude(status__in=['0','2']).values('date').annotate(sum=Sum('final_price')).values('date', 'sum').order_by('date')
        for i in order:
            dates[i['date']] = i['sum']
        series_data = []
        for k, v in dates.items():
            if today == k:
                x= f'오늘({week[k.weekday()]})'
            else:
                x= f'{k.strftime("%m.%d")}({week[k.weekday()]})'
            y = v
            series_data.append({"x":x, "y":y})

        data['title'] = '주간 매출'
        data['title_en'] = 'Week'
        data['series_data'] =  series_data

    elif report_type == 'MONTH':
        months = 8
        start_date = today.replace(day=1) - relativedelta(months=months-1)
        end_date = today
        order = Order.objects.filter(agency=agency, date__range=[start_date, end_date]).exclude(status__in=['0','2']).annotate(month=TruncMonth('date')).values('month').annotate(sum=Sum('final_price')).values('month', 'sum').order_by('month')
        
        for i in range(months):
            month = start_date + relativedelta(months=i)
            dates[f"{format(month.month, '02')}"] = 0
        for i in order:
            dates[i['month'].strftime("%m")] = i['sum']
        series_data = []
        
        for k, v in dates.items():
            x = f"{k}월"
            y = v
            series_data.append({"x":x, "y":y})
            
        data['title'] = '월간 매출'
        data['title_en'] = 'Month'
        data['series_data'] =  series_data
        
    return JsonResponse(data, status = 200)


class LoginView(View):
    '''
        에이전시 관리자 로그인 화면
    '''
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        if request.user.is_authenticated:
            agency_name = request.GET.get('agency_name', '')
            context['agency_name'] = agency_name
            filter_dict = {}
            if request.user.is_superuser:
                if agency_name:
                    filter_dict['name__icontains'] = agency_name
                context['agency_list'] = Agency.objects.filter(**filter_dict).annotate(agency_id=F('id')).values('agency_id', 'name')[:50]
            else:
                if agency_name:
                    filter_dict['shop__name__icontains'] = agency_name
                filter_dict['user'] = request.user
                context['agency_list'] = AgencyAdmin.objects.filter(**filter_dict).annotate(name=F('agency__name')).values('agency_id', 'name')[:50]
            return render(request, 'agency_admin_manage/agency_manage_login_select.html', context)

        return render(request, 'agency_admin_manage/agency_manage_login.html', context)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        username = request.POST['username']
        password = request.POST['password']
        try:
            user = User.objects.get(username=username)
        except:
            return JsonResponse({'message':'Incorrect username or password.'}, status = 400)
        
        if not user.check_password(raw_password=password):
            return JsonResponse({'message':'Incorrect username or password.'}, status = 400)
        if user.profile.withdrawal_at:
            return JsonResponse({'message':'Withdrawal account.'}, status = 400)
        if not user.is_active:
            return JsonResponse({'message':'Deactivated account.'}, status = 400)
        
        if user.is_superuser or AgencyAdmin.objects.filter(user=user).exists():
            login(request, user)
            if 'next' in request.GET:
                url = request.GET.get('next')
                url = url.split('?next=')[-1]
            else:
                url = reverse('agency_manage:login')
            return JsonResponse({'message':'Sign in completed.', 'url':url}, status = 200)

        else:
            return JsonResponse({'message':'Not an administrator.'}, status = 403)
        

class UserPasswordEditView(View):
    '''
        회원 비밀번호 변경
    '''
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        if not request.user.is_authenticated:
            return redirect(resolve_url('shop_manage:login'))
        return render(request, 'shop_admin_manage/user_password_edit.html', context)
    
    def post(self, request: HttpRequest, *args, **kwargs):        
        if not request.user.is_authenticated:
            return JsonResponse({"message": "로그인이 되어있지 않습니다."},status=401)
        user = request.user
        password = request.POST['password']
        new_password1 = request.POST['new_password1']
        new_password2 = request.POST['new_password2']
             
        if not user.check_password(raw_password=password):
            return JsonResponse({'message':'현재 비밀번호가 일치하지 않습니다.'}, status = 400)
        if new_password1 != new_password2:
            return JsonResponse({'message':'새로운 비밀번호가 일치하지 않습니다.'}, status = 400)
        
        user.set_password(new_password1)
        user.save()
        update_session_auth_hash(request, user)

        return JsonResponse({'message' : '변경되었습니다.', 'url':reverse('agency_manage:login')},  status = 202)
    

class PermissionDeniedView(LoginRequiredMixin, TemplateView):
    login_url = 'agency_manage:login'
    template_name='agency_admin_manage/permission_denied.html'
    

class NotFoundView(TemplateView):
    template_name='agency_admin_manage/not_found.html'
    

def check_agency(pk):
    try:
        agency = Agency.objects.get(pk=pk)
    except:
        return None
    return agency