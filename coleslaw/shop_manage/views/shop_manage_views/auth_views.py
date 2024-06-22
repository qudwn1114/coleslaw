from django.shortcuts import render, redirect, resolve_url
from django.contrib.auth import login
from django.urls import reverse
from django.views.generic import View, TemplateView
from django.http import HttpRequest, JsonResponse
from django.db.models import F, Sum, Value as V, Func, Sum, CharField
from django.db.models.functions import Coalesce
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.contrib.auth import update_session_auth_hash
from django.utils.decorators import method_decorator
from system_manage.decorators import  permission_required
from system_manage.models import Shop, ShopAdmin, Order


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
        card_sales = daily_order.filter(payment_method="CARD")
        cash_sales = daily_order.filter(payment_method="CASH")
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
        카테고리 반환
    '''
    shop_id = kwargs.get('shop_id')
    shop = check_shop(pk=shop_id)
    if not shop:
        return JsonResponse({}, status = 400)

    daily_order = Order.objects.filter(shop=shop, date=timezone.now().date()).exclude(status='0')
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

@require_http_methods(["GET"])
def shop_main_orders(request: HttpRequest, *args, **kwargs):
    '''
        주문내역
    '''
    shop_id = kwargs.get('shop_id')
    shop = check_shop(pk=shop_id)
    if not shop:
        return JsonResponse({}, status = 400)
    
    filter_dict = {}
    filter_dict['shop'] = shop
    filter_dict['date'] = timezone.now().date()
    order_list = Order.objects.filter(**filter_dict).annotate(
        createdAt = Func(
            F('created_at'),
            V('%y.%m.%d %H:%i'),
            function='DATE_FORMAT',
            output_field=CharField()
        )
    ).exclude(status='0').values(
        'id',
        'order_no',
        'order_name',
        'order_code',
        'order_membername',
        'order_phone',
        'final_price',
        'order_complete_sms',
        'status',
        'createdAt'
    ).order_by('-created_at')[:10]

    data = {
        'order_list' : list(order_list)
    }
    return JsonResponse(data, status = 200)


class LoginView(View):
    '''
        가맹점 관리자 로그인 화면
    '''
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        if request.user.is_authenticated:
            if request.user.is_superuser:
                context['shop_list'] = Shop.objects.all().annotate(shop_id=F('id')).values('shop_id', 'name')
            else:
                context['shop_list'] = ShopAdmin.objects.filter(user=request.user).annotate(name=F('shop__name')).values('shop_id', 'name')
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