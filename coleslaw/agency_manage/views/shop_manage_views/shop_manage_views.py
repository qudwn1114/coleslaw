from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import View
from django.http import HttpRequest, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.db import transaction
from system_manage.decorators import permission_required
from django.db.models import Exists, OuterRef
from system_manage.models import Shop, ShopCategory, ShopTable, Agency, AgencyShop
from agency_manage.views.agency_manage_views.auth_views import check_agency
import json


class ShopManageView(View):
    '''
        가맹점 관리 화면
    '''
    @method_decorator(permission_required(redirect_url='agency_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        agency_id = kwargs.get('agency_id')
        agency = check_agency(pk=agency_id)
        if not agency:
            return redirect('agency_manage:notfound')
        context['agency'] = agency
        
        paginate_by = '20'
        page = request.GET.get('page', '1')
        search_type = request.GET.get('search_type', '')
        search_keyword = request.GET.get('search_keyword', '')

        filter_dict = {}
        filter_dict['agency'] = agency

        if search_keyword:
            context['search_type'] = search_type
            context['search_keyword'] = search_keyword
            filter_dict[search_type + '__icontains'] = search_keyword

        agency_shops = AgencyShop.objects.filter(shop=OuterRef('pk'), agency=agency, status=True)
        obj_list = Shop.objects.filter(**filter_dict).annotate(
            agency_shop_status=Exists(agency_shops)
        ).values(
            'id',
            'name_kr',
            'name_en',
            'phone',
            'representative',
            'agency__name',
            'agency_shop_status',
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

        return render(request, 'agency_shop_manage/shop_manage.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def put(self, request: HttpRequest, *args, **kwargs):
        agency_id = kwargs.get('agency_id')
        agency = check_agency(pk=agency_id)
        if not agency:
            return JsonResponse({'message': '데이터오류'}, status = 400)

        request.PUT = json.loads(request.body)
        rq_type = request.PUT['type']
        shop_id = request.PUT['shop_id']
        try:
            agency_shop = AgencyShop.objects.get(shop_id=shop_id, agency=agency)
        except:
            return JsonResponse({"message": "데이터 오류"},status=400)
        if rq_type == 'STATUS':
            agency_shop.status = not agency_shop.status
            agency_shop.save()
        else:
            return JsonResponse({"message": "타입 오류"},status=400)
        
        return JsonResponse({'message' : '변경되었습니다.'}, status = 201)
    

class ShopCreateView(View):
    '''
        가맹점 생성
    '''
    @method_decorator(permission_required(redirect_url='agency_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        agency_id = kwargs.get('agency_id')
        agency = check_agency(pk=agency_id)
        if not agency:
            return redirect('agency_manage:notfound')
        context['agency'] = agency
        shop_category = ShopCategory.objects.all().values('id', 'name_kr').order_by('id')
        context['shop_category'] = shop_category

        return render(request, 'agency_shop_manage/shop_create.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def post(self, request: HttpRequest, *args, **kwargs):
        agency_id = kwargs.get('agency_id')
        agency = check_agency(pk=agency_id)
        if not agency:
            return JsonResponse({'message': '데이터오류'}, status = 400)
        
        shop_category_id = request.POST['shop_category_id']

        shop_name_kr = request.POST['shop_name_kr'].strip()
        shop_name_en = request.POST['shop_name_en'].strip()
        description = request.POST['description'].strip()

        representative = request.POST['representative']
        phone = request.POST['phone'].strip()
        registration_no = request.POST['registration_no'].strip()
        address = request.POST['address']
        address_detail = request.POST['address_detail'].strip()
        zipcode = request.POST['zipcode']
        image = request.FILES.get("image")
        location_image = request.FILES.get("location_image")
        waiting_time = int(request.POST['waiting_time'])
        logo_image1 = request.FILES.get("logo_image1")
        entry_image1 = request.FILES.get("entry_image1")
        logo_image2 = request.FILES.get("logo_image2")
        entry_image2 = request.FILES.get("entry_image2")
        table_time = int(request.POST['table_time'])
        additional_fee_time = int(request.POST['additional_fee_time'])
        try:
            agency = Agency.objects.get(pk=agency_id)
        except:
            return JsonResponse({'message': '에이전시 오류 입니다.'}, status=400)

        try:
            shop_category = ShopCategory.objects.get(pk=shop_category_id)
        except:
            return JsonResponse({'message': '카테고리 오류 입니다.'}, status=400)

        try:
            Shop.objects.get(name_kr=shop_name_kr)
            return JsonResponse({'message': '이미 존재하는 가맹점 한글명 입니다.'}, status=400)
        except:
            pass
        try:
            Shop.objects.get(name_en=shop_name_en)
            return JsonResponse({'message': '이미 존재하는 가맹점 영문명 입니다.'}, status=400)
        except:
            pass
        default_pos_ad_video = 'video/pos_ad/default.mp4'
        try:
            with transaction.atomic():
                shop = Shop.objects.create(
                    agency=agency,
                    shop_category=shop_category,
                    name_kr=shop_name_kr,
                    name_en=shop_name_en,
                    description=description,
                    representative=representative,
                    phone=phone,
                    registration_no=registration_no,
                    address=address,
                    address_detail=address_detail,
                    zipcode=zipcode,
                    image=image,
                    location_image=location_image,
                    waiting_time=waiting_time,
                    logo_image1=logo_image1,
                    entry_image1=entry_image1,
                    logo_image2=logo_image2,
                    entry_image2=entry_image2,
                    table_time=table_time,
                    additional_fee_time=additional_fee_time,
                    pos_ad_video = default_pos_ad_video
                )
                AgencyShop.objects.create(
                    agency=agency,
                    shop=shop
                )
        except:
            return JsonResponse({'message': '등록 실패.'}, status=400)


        return JsonResponse({'message' : '등록 되었습니다.', 'url':reverse("agency_manage:shop_detail", kwargs={"agency_id":agency_id, "pk" : shop.id})},  status = 202)
    

class ShopDetailView(View):
    '''
        가맹점 상세 화면
    '''
    @method_decorator(permission_required(redirect_url='agency_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        agency_id = kwargs.get('agency_id')
        agency = check_agency(pk=agency_id)
        if not agency:
            return redirect('agency_manage:notfound')
        context['agency'] = agency
        pk = kwargs.get("pk")
        data = get_object_or_404(Shop, pk=pk, agency=agency)
        context['data'] = data

        return render(request, 'agency_shop_manage/shop_detail.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def delete(self, request: HttpRequest, *args, **kwargs):
        agency_id = kwargs.get('agency_id')
        agency = check_agency(pk=agency_id)
        if not agency:
            return JsonResponse({'message': '데이터오류'}, status = 400)
        pk = kwargs.get('pk')
        try:
            shop = Shop.objects.get(pk=pk, agency=agency)
        except:
            return JsonResponse({"message": "데이터 오류"},status=400)
        
        shop.delete()

        return JsonResponse({'message' : '삭제되었습니다.', 'url':reverse('agency_manage:shop_manage', kwargs={'agency_id':agency_id})},  status = 202)
    

class ShopEditView(View):
    '''
        가맹점 수정 화면
    '''
    @method_decorator(permission_required(redirect_url='agency_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        agency_id = kwargs.get('agency_id')
        agency = check_agency(pk=agency_id)
        if not agency:
            return redirect('agency_manage:notfound')
        context['agency'] = agency

        pk = kwargs.get("pk")
        data = get_object_or_404(Shop, pk=pk, agency=agency)
        context['data'] = data
        shop_category = ShopCategory.objects.all().values('id', 'name_kr').order_by('id')
        context['shop_category'] = shop_category

        return render(request, 'agency_shop_manage/shop_edit.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def post(self, request: HttpRequest, *args, **kwargs):
        agency_id = kwargs.get('agency_id')
        agency = check_agency(pk=agency_id)
        if not agency:
            return JsonResponse({'message': '데이터오류'}, status = 400)
        pk = kwargs.get('pk')
        try:
            shop = Shop.objects.get(pk=pk, agency=agency)
        except:
            return JsonResponse({"message": "데이터 오류"},status=400)
        
        shop_category_id = request.POST['shop_category_id']
        shop_name_kr = request.POST['shop_name_kr'].strip()
        shop_name_en = request.POST['shop_name_en'].strip()
        description = request.POST['description'].strip()

        representative = request.POST['representative']
        phone = request.POST['phone'].strip()
        registration_no = request.POST['registration_no'].strip()
        address = request.POST['address']
        address_detail = request.POST['address_detail'].strip()
        zipcode = request.POST['zipcode']
        image = request.FILES.get("image")
        location_image = request.FILES.get("location_image")
        waiting_time = int(request.POST['waiting_time'])
        logo_image1 = request.FILES.get("logo_image1")
        entry_image1 = request.FILES.get("entry_image1")
        logo_image2 = request.FILES.get("logo_image2")
        entry_image2 = request.FILES.get("entry_image2")
        table_time = int(request.POST['table_time'])
        additional_fee_time = int(request.POST['additional_fee_time'])

        aligo_sender_key= request.POST['aligo_sender_key'].strip()
        aligo_entry_template_code1= request.POST['aligo_entry_template_code1'].strip()
        aligo_entry_template_code2= request.POST['aligo_entry_template_code2'].strip()

        try:
            shop_category = ShopCategory.objects.get(pk=shop_category_id)
        except:
            return JsonResponse({'message': '카테고리 오류 입니다.'}, status=400)

    
        if Shop.objects.filter(name_kr=shop_name_kr).exclude(pk=shop.pk).exists():
            return JsonResponse({'message': '이미 존재하는 가맹점 한글명 입니다.'}, status=400)
        if Shop.objects.filter(name_en=shop_name_en).exclude(pk=shop.pk).exists():
            return JsonResponse({'message': '이미 존재하는 가맹점 영문명 입니다.'}, status=400)
        try:
            with transaction.atomic():
                shop.shop_category = shop_category
                shop.name_kr = shop_name_kr
                shop.name_en = shop_name_en
                shop.description = description
                shop.representative = representative
                shop.phone = phone
                shop.registration_no = registration_no
                shop.address = address
                shop.address_detail = address_detail
                shop.zipcode = zipcode
                shop.waiting_time = waiting_time
                shop.table_time=table_time
                shop.additional_fee_time=additional_fee_time
                shop.aligo_sender_key = aligo_sender_key
                shop.aligo_entry_template_code1 =aligo_entry_template_code1
                shop.aligo_entry_template_code2 =aligo_entry_template_code2
                
                if image:
                    shop.image = image
                if location_image:
                    shop.location_image = location_image
                if logo_image1:
                    shop.logo_image1 = logo_image1
                if entry_image1:
                    shop.entry_image1 = entry_image1
                if logo_image2:
                    shop.logo_image2 = logo_image2
                if entry_image2:
                    shop.entry_image2 = entry_image2
                shop.save()
        except:
            return JsonResponse({'message': '수정오류'}, status=400)


        return JsonResponse({'message' : '수정 되었습니다.', 'url':reverse("agency_manage:shop_detail", kwargs={"agency_id":agency_id, "pk" : shop.id})},  status = 202)


