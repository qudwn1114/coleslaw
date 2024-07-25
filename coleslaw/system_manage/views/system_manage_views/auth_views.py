from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.views.generic import View, TemplateView
from django.http import HttpRequest, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import F, Sum, Value as V, Func, CharField
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.core.validators import RegexValidator
from system_manage.decorators import permission_required
from system_manage.models import Order, MainCategory, SubCategory

import datetime

# Create your views here.
class HomeView(TemplateView):
    '''
        관리자 메인 화면
    '''
    template_name = 'system_manage/admin_main.html'
    @method_decorator(permission_required(redirect_url='system_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}

        return render(request, self.template_name, context)

@require_http_methods(["GET"])
def system_main_sales(request: HttpRequest, *args, **kwargs):
    '''
        판매현황
    '''
    daily_order = Order.objects.filter(date=timezone.now().date()).exclude(status='0')
    card_sales = daily_order.filter(payment_method="CARD")
    cash_sales = daily_order.filter(payment_method="CASH")
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

class LoginView(View):
    '''
        관리자 로그인 기능
    '''
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        if request.user.is_authenticated:
            return redirect('system_manage:home')
        
        return render(request, 'system_manage/admin_login.html', context)

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
        
        if user.is_superuser:
            login(request, user)
            if 'next' in request.GET:
                url = request.GET.get('next')
                url = url.split('?next=')[-1]
            else:
                url = reverse('system_manage:home')
            return JsonResponse({'message':'Sign in completed.', 'url':url}, status = 200)
        else:
            return JsonResponse({'message':'Not an administrator.'}, status = 403)

class PermissionDeniedView(LoginRequiredMixin, TemplateView):
    login_url = 'system_manage:login'
    template_name='system_manage/permission_denied.html'


class NotFoundView(LoginRequiredMixin, TemplateView):
    login_url = 'system_manage:login'
    template_name='system_manage/not_found.html'


def validate_username(username):
    '''
        아이디 유효성 체크
    '''
    try:
        RegexValidator(regex=r'^[a-zA-z0-9]{6,20}$')(username)
    except:
        return False

    return True

def validate_password(password):
    '''
        비밀번호 유효성 체크
    '''
    try:
        # Minimum eight characters Maximum 16 characters, at least one letter and one number
        RegexValidator(regex=r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,16}$')(password)
    except:
        return False

    return True


def validate_birth(birth):
    '''
    생년월일 유효성체크
    '''
    try:
        birth = datetime.datetime.strptime(birth, "%Y-%m-%d")
    except ValueError:
        return False
    
    return True

def validate_phone(phone):
    '''
        전화번호 유효성 체크
    '''
    try:
        RegexValidator(regex=r'^01([0-9]{1})([0-9]{4})([0-9]{4})$')(phone)
    except:
        return False

    return True