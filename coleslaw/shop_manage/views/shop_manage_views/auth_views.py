from django.shortcuts import render, redirect, resolve_url
from django.contrib.auth import login
from django.urls import reverse
from django.views.generic import View, TemplateView
from django.http import HttpRequest, JsonResponse
from django.db.models import F
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin


from django.utils.decorators import method_decorator
from system_manage.decorators import  permission_required
from system_manage.models import Shop, ShopAdmin


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
        
        return render(request, 'shop_admin_manage/shop_manage_main.html', context)
    

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