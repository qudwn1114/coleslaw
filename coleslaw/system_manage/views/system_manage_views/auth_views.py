from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.views.generic import View, TemplateView
from django.http import HttpRequest, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.decorators import method_decorator
from system_manage.decorators import permission_required
from django.core.validators import RegexValidator
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