from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import View
from django.http import HttpRequest, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
from django.db.models import CharField, F, Value as V, Func, Sum, Case, When, IntegerField
from django.db.models.functions import Coalesce, Cast
from django.utils.decorators import method_decorator
from django.db import transaction
from django.utils import timezone
from system_manage.decorators import permission_required
from system_manage.models import PersonType

class PersonTypeManageView(View):
    '''
        사람타입 관리
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


        obj_list = PersonType.objects.filter(**filter_dict).values(
            'id',
            'name',
            'created_at'
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

        return render(request, 'person_type_manage/person_type_manage.html', context)

class PersonTypeCreateView(View):
    '''
        사람타입 등록
    '''
    @method_decorator(permission_required(redirect_url='system_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}

        return render(request, 'person_type_manage/person_type_create.html', context)

    @method_decorator(permission_required(raise_exception=True))
    def post(self, request: HttpRequest, *args, **kwargs):
        person_type_name = request.POST['person_type_name'].strip()
        image = request.FILES.get("image")

        try:
            PersonType.objects.get(name=person_type_name)
            return JsonResponse({'message': '이미 존재하는 이름 입니다.'}, status=400)
        except:
            pass

        person_type = PersonType.objects.create(
            name=person_type_name,
            image=image
        )

        return JsonResponse({'message' : '등록 되었습니다.', 'url':reverse("system_manage:person_type_detail", kwargs={"pk" : person_type.id})},  status = 202)


class PersonTypeDetailView(View):
    '''
        사람타입 상세
    '''
    @method_decorator(permission_required(redirect_url='system_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        pk = kwargs.get('pk')

        person_type = get_object_or_404(PersonType, pk=pk)
        context['person_type'] = person_type

        return render(request, 'person_type_manage/person_type_detail.html', context)
    

    @method_decorator(permission_required(raise_exception=True))
    def delete(self, request: HttpRequest, *args, **kwargs):
        pk = kwargs.get('pk')
        try:
            person_type = PersonType.objects.get(pk=pk)
        except:
            return JsonResponse({"message": "데이터 오류"},status=400)
        
        person_type.delete()

        return JsonResponse({'message' : '삭제되었습니다.', 'url':reverse('system_manage:person_type_manage')},  status = 202)



class PersonTypeEditView(View):
    '''
        사람타입 수정
    '''
    @method_decorator(permission_required(redirect_url='system_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        pk = kwargs.get('pk')
        
        person_type = get_object_or_404(PersonType, pk=pk)
        context['person_type'] = person_type

        return render(request, 'person_type_manage/person_type_edit.html', context)
    

    @method_decorator(permission_required(raise_exception=True))
    def post(self, request: HttpRequest, *args, **kwargs):
        pk = kwargs.get('pk')
        try:
            person_type = PersonType.objects.get(pk=pk)
        except:
            return JsonResponse({"message": "데이터 오류"},status=400)

        person_type_name = request.POST['person_type_name'].strip()
        image = request.FILES.get("image")

        if PersonType.objects.filter(name=person_type_name).exclude(pk=person_type.pk).exists():
            return JsonResponse({'message': '이미 존재하는 이름 입니다.'}, status=400)

        person_type.name = person_type_name
        if image:
            person_type.image = image
        person_type.save()

        return JsonResponse({'message' : '수정 되었습니다.', 'url':reverse("system_manage:person_type_detail", kwargs={"pk" : person_type.id})},  status = 202)
