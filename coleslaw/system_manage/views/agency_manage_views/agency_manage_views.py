from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import View
from django.http import HttpRequest, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.db import transaction
from system_manage.decorators import permission_required
from system_manage.models import Agency
import json

class AgencyManageView(View):
    '''
        에이전시 관리 화면
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

        obj_list = Agency.objects.filter(**filter_dict).values(
            'id',
            'name',
            'status',
            'created_at',
        ).order_by('-created_at')

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

        return render(request, 'agency_manage/agency_manage.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def put(self, request: HttpRequest, *args, **kwargs):
        request.PUT = json.loads(request.body)
        rq_type = request.PUT['type']
        agency_id = request.PUT['agency_id']
        try:
            agency = Agency.objects.get(pk=agency_id)
        except:
            return JsonResponse({"message": "데이터 오류"},status=400)
        if rq_type == 'STATUS':
            agency.status = not agency.status
            agency.save()
        else:
            return JsonResponse({"message": "타입 오류"},status=400)
        
        return JsonResponse({'message' : '변경되었습니다.'}, status = 201)

class AgencyCreateView(View):
    '''
        에이전시 등록
    '''
    @method_decorator(permission_required(redirect_url='system_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}

        return render(request, 'agency_manage/agency_create.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def post(self, request: HttpRequest, *args, **kwargs):
        agency_name = request.POST['agency_name'].strip()
        description = request.POST['description'].strip()
        image = request.FILES.get("image")
        
        try:
            Agency.objects.get(name=agency_name)
            return JsonResponse({'message': '이미 존재하는 에이전시 명 입니다.'}, status=400)
        except:
            pass

        agency = Agency.objects.create(
            name=agency_name,
            description=description,
            image=image
        )

        return JsonResponse({'message' : '등록 되었습니다.', 'url':reverse("system_manage:agency_detail", kwargs={"pk" : agency.id})},  status = 202)
    

class AgencyDetailView(View):
    '''
        에이전시 상세 화면
    '''
    @method_decorator(permission_required(redirect_url='system_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        pk = kwargs.get("pk")
        data = get_object_or_404(Agency, pk=pk)
        context['data'] = data

        return render(request, 'agency_manage/agency_detail.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def delete(self, request: HttpRequest, *args, **kwargs):
        pk = kwargs.get('pk')
        try:
            agency = Agency.objects.get(pk=pk)
        except:
            return JsonResponse({"message": "데이터 오류"},status=400)
        
        agency.delete()

        return JsonResponse({'message' : '삭제되었습니다.', 'url':reverse('system_manage:agency_manage')},  status = 202)
    

class AgencyEditView(View):
    '''
        에이전시 수정 화면
    '''
    @method_decorator(permission_required(redirect_url='system_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        pk = kwargs.get("pk")
        data = get_object_or_404(Agency, pk=pk)
        context['data'] = data

        return render(request, 'agency_manage/agency_edit.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def post(self, request: HttpRequest, *args, **kwargs):
        pk = kwargs.get('pk')
        try:
            agency = Agency.objects.get(pk=pk)
        except:
            return JsonResponse({"message": "데이터 오류"},status=400)
        
        agency_name = request.POST['agency_name'].strip()
        description = request.POST['description'].strip()
        image = request.FILES.get("image")
        qr_link = request.POST['qr_link'].strip()
    
        if Agency.objects.filter(name=agency_name).exclude(pk=agency.pk).exists():
            return JsonResponse({'message': '이미 존재하는 에이전시 명 입니다.'}, status=400)
        
        agency.name = agency_name
        agency.description = description
        agency.qr_link = qr_link
        if image:
            agency.image = image
        agency.save()

        return JsonResponse({'message' : '수정 되었습니다.', 'url':reverse("system_manage:agency_detail", kwargs={"pk" : agency.id})},  status = 202)