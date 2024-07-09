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
from system_manage.models import Shop, ShopCategory, ShopTable, Agency, AgencyShop

class ShopManageView(View):
    '''
        가맹점 관리 화면
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

        obj_list = Shop.objects.filter(**filter_dict).values(
            'id',
            'name',
            'phone',
            'representative',
            'agency__name',
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

        return render(request, 'shop_manage/shop_manage.html', context)
    

class ShopCreateView(View):
    '''
        가맹점 생성
    '''
    @method_decorator(permission_required(redirect_url='system_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        shop_category = ShopCategory.objects.all().values('id', 'name').order_by('id')
        agency = Agency.objects.all().values('id', 'name').order_by('id')
        context['shop_category'] = shop_category
        context['agency'] = agency

        return render(request, 'shop_manage/shop_create.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def post(self, request: HttpRequest, *args, **kwargs):
        agency_id = request.POST['agency_id']
        shop_category_id = request.POST['shop_category_id']

        shop_name = request.POST['shop_name'].strip()
        description = request.POST['description'].strip()

        representative = request.POST['representative']
        phone = request.POST['phone'].strip()
        registration_no = request.POST['registration_no'].strip()
        address = request.POST['address']
        address_detail = request.POST['address_detail'].strip()
        zipcode = request.POST['zipcode']
        image = request.FILES.get("image")

        try:
            agency = Agency.objects.get(pk=agency_id)
        except:
            return JsonResponse({'message': '에이전시 오류 입니다.'}, status=400)

        try:
            shop_category = ShopCategory.objects.get(pk=shop_category_id)
        except:
            return JsonResponse({'message': '카테고리 오류 입니다.'}, status=400)

        try:
            Shop.objects.get(name=shop_name)
            return JsonResponse({'message': '이미 존재하는 가맹점 명 입니다.'}, status=400)
        except:
            pass
        try:
            with transaction.atomic():
                shop = Shop.objects.create(
                    agency=agency,
                    shop_category=shop_category,
                    name=shop_name,
                    description=description,
                    representative=representative,
                    phone=phone,
                    registration_no=registration_no,
                    address=address,
                    address_detail=address_detail,
                    zipcode=zipcode,
                    image=image
                )
                ShopTable.objects.create(
                    shop = shop,
                    table_no = 0,
                    name = 'DEFAULT'
                )
                AgencyShop.objects.create(
                    agency=agency,
                    shop=shop
                )
        except:
            return JsonResponse({'message': '등록 실패.'}, status=400)


        return JsonResponse({'message' : '등록 되었습니다.', 'url':reverse("system_manage:shop_detail", kwargs={"pk" : shop.id})},  status = 202)
    

class ShopDetailView(View):
    '''
        가맹점 상세 화면
    '''
    @method_decorator(permission_required(redirect_url='system_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        pk = kwargs.get("pk")
        data = get_object_or_404(Shop, pk=pk)
        context['data'] = data

        return render(request, 'shop_manage/shop_detail.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def delete(self, request: HttpRequest, *args, **kwargs):
        pk = kwargs.get('pk')
        try:
            shop = Shop.objects.get(pk=pk)
        except:
            return JsonResponse({"message": "데이터 오류"},status=400)
        
        shop.delete()

        return JsonResponse({'message' : '삭제되었습니다.', 'url':reverse('system_manage:shop_manage')},  status = 202)
    

class ShopEditView(View):
    '''
        가맹점 수정 화면
    '''
    @method_decorator(permission_required(redirect_url='system_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        pk = kwargs.get("pk")
        data = get_object_or_404(Shop, pk=pk)
        context['data'] = data
        shop_category = ShopCategory.objects.all().values('id', 'name').order_by('id')
        agency = Agency.objects.all().values('id', 'name').order_by('id')
        context['shop_category'] = shop_category
        context['agency'] = agency

        return render(request, 'shop_manage/shop_edit.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def post(self, request: HttpRequest, *args, **kwargs):
        pk = kwargs.get('pk')
        try:
            shop = Shop.objects.get(pk=pk)
        except:
            return JsonResponse({"message": "데이터 오류"},status=400)
        
        agency_id = request.POST['agency_id']
        shop_category_id = request.POST['shop_category_id']
        shop_name = request.POST['shop_name'].strip()
        description = request.POST['description'].strip()

        representative = request.POST['representative']
        phone = request.POST['phone'].strip()
        registration_no = request.POST['registration_no'].strip()
        address = request.POST['address']
        address_detail = request.POST['address_detail'].strip()
        zipcode = request.POST['zipcode']
        image = request.FILES.get("image")

        try:
            agency = Agency.objects.get(pk=agency_id)
        except:
            return JsonResponse({'message': '에이전시 오류 입니다.'}, status=400)

        try:
            shop_category = ShopCategory.objects.get(pk=shop_category_id)
        except:
            return JsonResponse({'message': '카테고리 오류 입니다.'}, status=400)

    
        if Shop.objects.filter(name=shop_name).exclude(pk=shop.pk).exists():
            return JsonResponse({'message': '이미 존재하는 가맹점 명 입니다.'}, status=400)
        
        shop.agency = agency
        shop.shop_category = shop_category
        shop.name = shop_name
        shop.description = description
        shop.representative = representative
        shop.phone = phone
        shop.registration_no = registration_no
        shop.address = address
        shop.address_detail = address_detail
        shop.zipcode = zipcode
        if image:
            shop.image = image
        shop.save()

        return JsonResponse({'message' : '수정 되었습니다.', 'url':reverse("system_manage:shop_detail", kwargs={"pk" : shop.id})},  status = 202)


