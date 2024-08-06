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
from system_manage.models import Shop, ShopCategory, ShopTable, Agency, AgencyShop
from agency_manage.views.agency_manage_views.auth_views import check_agency


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

        obj_list = Shop.objects.filter(**filter_dict).values(
            'id',
            'name_kr',
            'name_en',
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

        return render(request, 'agency_shop_manage/shop_manage.html', context)
    

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
        main_tid = request.POST['main_tid'].strip()
        waiting_time = int(request.POST['waiting_time'])
        logo_image1 = request.FILES.get("logo_image1")
        entry_image1 = request.FILES.get("entry_image1")
        logo_image2 = request.FILES.get("logo_image2")
        entry_image2 = request.FILES.get("entry_image2")

        receipt = request.POST['receipt'].strip()
        shop_receipt_flag = bool(request.POST.get('shop_receipt_flag', None))

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
                    main_tid=main_tid,
                    waiting_time=waiting_time,
                    logo_image1=logo_image1,
                    entry_image1=entry_image1,
                    logo_image2=logo_image2,
                    entry_image2=entry_image2,
                    receipt=receipt,
                    shop_receipt_flag=shop_receipt_flag,
                )
                ShopTable.objects.create(
                    shop = shop,
                    table_no = 0,
                    tid=main_tid,
                    name = 'DEFAULT'
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
        main_tid = request.POST['main_tid'].strip()
        waiting_time = int(request.POST['waiting_time'])
        logo_image1 = request.FILES.get("logo_image1")
        entry_image1 = request.FILES.get("entry_image1")
        logo_image2 = request.FILES.get("logo_image2")
        entry_image2 = request.FILES.get("entry_image2")

        receipt = request.POST['receipt'].strip()
        shop_receipt_flag = bool(request.POST.get('shop_receipt_flag', None))

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
                shop.main_tid = main_tid
                shop.waiting_time = waiting_time
                shop.receipt = receipt
                shop.shop_receipt_flag = shop_receipt_flag
                if image:
                    shop.image = image
                if logo_image1:
                    shop.logo_image1 = logo_image1
                if entry_image1:
                    shop.entry_image1 = entry_image1
                if logo_image2:
                    shop.logo_image2 = logo_image2
                if entry_image2:
                    shop.entry_image2 = entry_image2
                shop.save()
                
                main_pos = ShopTable.objects.get(shop=shop, table_no = 0)
                main_pos.tid = main_tid
                main_pos.save()
        except:
            return JsonResponse({'message': '수정오류'}, status=400)


        return JsonResponse({'message' : '수정 되었습니다.', 'url':reverse("agency_manage:shop_detail", kwargs={"agency_id":agency_id, "pk" : shop.id})},  status = 202)


