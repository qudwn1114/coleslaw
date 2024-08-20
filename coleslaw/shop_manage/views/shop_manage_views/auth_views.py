from django.shortcuts import render, redirect, resolve_url
from django.contrib.auth import login
from django.urls import reverse
from django.views.generic import View, TemplateView
from django.http import HttpRequest, JsonResponse
from django.db.models import F, Sum, Value as V, Func, CharField, Count
from django.db.models.functions import Coalesce, TruncHour, TruncMonth
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
from django.views.decorators.http import require_http_methods
from django.contrib.auth import update_session_auth_hash
from django.utils.decorators import method_decorator
from system_manage.decorators import  permission_required
from system_manage.models import Shop, ShopAdmin, Order, AgencyAdmin

from dateutil.relativedelta import relativedelta
import datetime


# Create your views here.
class HomeView(View):
    '''
        Shop 관리자 메인 화면
    '''
    @method_decorator(permission_required(redirect_url='shop_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return redirect('shop_manage:notfound')
        context['shop'] = shop

        daily_order = Order.objects.filter(shop=shop, date=timezone.now().date()).exclude(status='0')
        card_sales = daily_order.filter(payment_method="0")
        cash_sales = daily_order.filter(payment_method="1")
        cancel_sales = daily_order.filter(status='2')
        total_sales = daily_order.all().exclude(status='2')

        daily = {
            'card_sales' : card_sales.aggregate(sum=Coalesce(Sum('final_price'), 0)).get('sum'),
            'card_count' : card_sales.count(),
            'cash_sales' : cash_sales.aggregate(sum=Coalesce(Sum('final_price'), 0)).get('sum'),
            'cash_count' : cash_sales.count(),
            'cancel_sales' : cancel_sales.aggregate(sum=Coalesce(Sum('final_price'), 0)).get('sum'),
            'cancel_count' : cancel_sales.count(),
            'total_sales' : total_sales.aggregate(sum=Coalesce(Sum('final_price'), 0)).get('sum'),
            'total_count' : total_sales.count()
        }
        context['daily'] = daily
        return render(request, 'shop_admin_manage/shop_manage_main.html', context)

@require_http_methods(["GET"])
def shop_main_sales(request: HttpRequest, *args, **kwargs):
    '''
        판매현황
    '''
    shop_id = kwargs.get('shop_id')
    shop = check_shop(pk=shop_id)
    if not shop:
        return JsonResponse({}, status = 400)

    daily_order = Order.objects.filter(shop=shop, date=timezone.now().date()).exclude(status='0')
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
def shop_main_orders(request: HttpRequest, *args, **kwargs):
    '''
        주문내역
    '''
    shop_id = kwargs.get('shop_id')
    shop = check_shop(pk=shop_id)
    if not shop:
        return JsonResponse({}, status = 400)
    
    paginate_by = request.GET.get('paginate_by', '20')
    page = request.GET.get('page', '1')
    search_type = request.GET.get('search_type', '')
    search_keyword = request.GET.get('search_keyword', '')
    
    filter_dict = {}
    filter_dict['shop'] = shop
    if request.GET:
        dates = request.GET.get('dates', '')
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
        filter_dict['date'] = timezone.now().date()
    status_list = ['1', '2', '3', '4', '5']
    filter_dict['status__in'] = status_list
    if search_keyword:
        filter_dict[search_type + '__icontains'] = search_keyword

    order_list = Order.objects.filter(**filter_dict).annotate(
        createdAt = Func(
            F('created_at'),
            V('%y.%m.%d %H:%i'),
            function='DATE_FORMAT',
            output_field=CharField()
        )
    ).order_by('-created_at').values(
        'id',
        'order_no',
        'order_name_kr',
        'order_name_en',
        'order_code',
        'order_membername',
        'order_phone',
        'final_price',
        'order_complete_sms',
        'status',
        'createdAt'
    )

    paginator = Paginator(order_list, paginate_by)
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

    data = {
        'order_list' : list(page_obj)
    }
    return JsonResponse(data, status = 200)


@require_http_methods(["GET"])
def shop_sales_report(request: HttpRequest, *args, **kwargs):
    '''
        판매현황
    '''
    shop_id = kwargs.get('shop_id')
    shop = check_shop(pk=shop_id)
    if not shop:
        return JsonResponse({}, status = 400)
    data = {}
    report_type = request.GET.get('report_type', 'TODAY')
    today = timezone.now().date()
    dates = {}
    if report_type == 'TODAY':        
        order = Order.objects.filter(shop=shop, date=today).exclude(status__in=['0','2']).annotate(hour=TruncHour('updated_at')).values('hour').annotate(sum=Sum('final_price')).values('hour', 'sum').order_by('hour')
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
        order = Order.objects.filter(shop=shop, date__range=[start_date, end_date]).exclude(status__in=['0','2']).values('date').annotate(sum=Sum('final_price')).values('date', 'sum').order_by('date')
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
        order = Order.objects.filter(shop=shop, date__range=[start_date, end_date]).exclude(status__in=['0','2']).annotate(month=TruncMonth('date')).values('month').annotate(sum=Sum('final_price')).values('month', 'sum').order_by('month')
        
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
        가맹점 관리자 로그인 화면
    '''
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        if request.user.is_authenticated:
            shop_name_kr = request.GET.get('shop_name_kr', '')
            context['shop_name_kr'] = shop_name_kr
            filter_dict = {}
            if request.user.is_superuser:
                if shop_name_kr:
                    filter_dict['name_kr__icontains'] = shop_name_kr
                context['shop_list'] = Shop.objects.filter(**filter_dict).annotate(shop_id=F('id')).values('shop_id', 'name_kr')[:50]
            elif AgencyAdmin.objects.filter(user=request.user).exists():
                agency_id_list = list(AgencyAdmin.objects.filter(user=request.user).values_list('agency', flat=True))
                filter_dict['agency_id__in'] = agency_id_list
                if shop_name_kr:
                    filter_dict['name_kr__icontains'] = shop_name_kr 
                context['shop_list'] = Shop.objects.filter(**filter_dict).annotate(shop_id=F('id')).values('shop_id', 'name_kr')[:50]
            else:
                if shop_name_kr:
                    filter_dict['shop__name_kr__icontains'] = shop_name_kr
                filter_dict['user'] = request.user
                context['shop_list'] = ShopAdmin.objects.filter(**filter_dict).annotate(name_kr=F('shop__name_kr')).values('shop_id', 'name_kr')[:50]
            return render(request, 'shop_admin_manage/shop_manage_login_select.html', context)

        return render(request, 'shop_admin_manage/shop_manage_login.html', context)
    
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
        
        if user.is_superuser or ShopAdmin.objects.filter(user=user).exists():
            login(request, user)
            if 'next' in request.GET:
                url = request.GET.get('next')
                url = url.split('?next=')[-1]
            else:
                url = reverse('shop_manage:login')
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

        return JsonResponse({'message' : '변경되었습니다.', 'url':reverse('shop_manage:login')},  status = 202)
    

class PermissionDeniedView(LoginRequiredMixin, TemplateView):
    login_url = 'shop_manage:login'
    template_name='shop_admin_manage/permission_denied.html'
    

class NotFoundView(TemplateView):
    template_name='shop_admin_manage/not_found.html'
    

def check_shop(pk):
    try:
        shop = Shop.objects.get(pk=pk)
    except:
        return None
    return shop