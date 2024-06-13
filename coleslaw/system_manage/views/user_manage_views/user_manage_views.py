from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import View
from django.http import HttpRequest, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.db import transaction

from system_manage.decorators import permission_required
from system_manage.models import Profile
from system_manage.views.system_manage_views.auth_views import validate_birth, validate_phone

import json, logging, traceback

class UserManageView(View):
    '''
        회원관리 화면
    '''
    @method_decorator(permission_required(redirect_url='system_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        paginate_by = '20'
        page = request.GET.get('page', '1')
        search_type = request.GET.get('search_type', '')
        search_keyword = request.GET.get('search_keyword', '')

        filter_dict = {}

        if search_keyword:
            context['search_type'] = search_type
            context['search_keyword'] = search_keyword
            filter_dict[search_type + '__icontains'] = search_keyword

        obj_list = User.objects.filter(**filter_dict).values(
            'id',
            'username',
            'is_active',
            'is_superuser',
            'profile__membername',
            'date_joined',
            'profile__phone',
        ).order_by('-date_joined')


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

        return render(request, 'user_manage/user_manage.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def put(self, request: HttpRequest, *args, **kwargs):
        request.PUT = json.loads(request.body)
        rq_type = request.PUT['type']
        user_id = request.PUT['user_id']
        try:
            user = User.objects.get(pk=user_id)
        except:
            return JsonResponse({"message": "데이터 오류"},status=400)
        if rq_type == 'ACTIVE':
            is_active = bool(request.PUT['is_active'])
            user.is_active = is_active
            user.save()
        elif rq_type == 'SUPERUSER':
            if user.is_superuser:
                user.is_superuser = False
            else:
                user.is_superuser = True
            user.save()
        else:
            return JsonResponse({"message": "타입 오류"},status=400)
        
        return JsonResponse({'message' : '변경되었습니다.'}, status = 201)
    

class UserCreateView(View):
    '''
        회원 생성
    '''
    @method_decorator(permission_required(redirect_url='system_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}

        return render(request, 'user_manage/user_create.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def post(self, request: HttpRequest, *args, **kwargs):
        membername = request.POST['membername'].strip()
        username = request.POST['username']
        password = request.POST['password']
        phone = request.POST['phone']
        address = request.POST['address']
        address_detail = request.POST['address_detail'].strip()
        zipcode = request.POST['zipcode']
        birth = request.POST['birth']
        gender = request.POST['gender']

        try:
            User.objects.get(username=username)
            return JsonResponse({'message': '아이디가 이미 존재합니다'}, status=400)
        except:
            pass

        if not validate_phone(phone):
            return JsonResponse({"message": "유효하지 않은 전화번호 형식입니다."},status=400)
        
        if not validate_birth(birth):
            return JsonResponse({"message": "유효하지 않은 날짜 형식입니다. ex) 1990-01-01"}, status=400)
        
        try:
            with transaction.atomic(): 
                user = User.objects.create_user(
                    username=username,
                    password=password
                )
                user.profile.membername = membername
                user.profile.birth = birth
                user.profile.zipcode = zipcode
                user.profile.address = address
                user.profile.address_detail = address_detail
                user.profile.phone =phone
                user.profile.gender = gender
                user.save()

        except Exception as e:
            logger = logging.getLogger('my')
            logger.error(traceback.format_exc())
            return JsonResponse({'message': '가입 오류'}, status=400)


        return JsonResponse({'message' : '등록 되었습니다.', 'url':reverse('system_manage:user_manage')},  status = 202)


class UserDetailView(View):
    '''
        회원 상세 화면
    '''
    @method_decorator(permission_required(redirect_url='system_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        pk = kwargs.get("pk")
        data = get_object_or_404(User, pk=pk)
        context['data'] = data

        return render(request, 'user_manage/user_detail.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def delete(self, request: HttpRequest, *args, **kwargs):
        pk = kwargs.get('pk')
        try:
            user = User.objects.get(pk=pk)
        except:
            return JsonResponse({"message": "데이터 오류"},status=400)
        
        user.delete()
        
        return JsonResponse({'message' : '삭제되었습니다.', 'url':reverse('system_manage:user_manage')},  status = 202)
    

class UserEditView(View):
    '''
        회원 수정 화면
    '''
    @method_decorator(permission_required(redirect_url='system_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        pk = kwargs.get("pk")
        data = get_object_or_404(User, pk=pk)
        context['data'] = data

        return render(request, 'user_manage/user_edit.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def post(self, request: HttpRequest, *args, **kwargs):
        pk = kwargs.get("pk")
        try:
            data = User.objects.get(pk=pk)
        except:
            return JsonResponse({'message': '사용자 정보 오류'}, status=400)
        
        membername = request.POST['membername']
        phone = request.POST['phone']
        address = request.POST['address']
        address_detail = request.POST['address_detail']
        zipcode = request.POST['zipcode']
        birth = request.POST['birth']
        gender = request.POST['gender']

        if not validate_phone(phone):
            return JsonResponse({"message": "유효하지 않은 전화번호 형식입니다."},status=400)
        
        if not validate_birth(birth):
            return JsonResponse({"message": "유효하지 않은 날짜 형식입니다. ex) 1990-01-01"}, status=400)

        data.profile.membername = membername.strip()
        data.profile.phone = phone
        data.profile.birth = birth
        data.profile.address = address
        data.profile.address_detail = address_detail.strip()
        data.profile.zipcode = zipcode
        data.profile.gender = gender
        data.save()

        return JsonResponse({'message' : '수정되었습니다.', 'url':reverse('system_manage:user_detail', kwargs={'pk':pk})},  status = 202)