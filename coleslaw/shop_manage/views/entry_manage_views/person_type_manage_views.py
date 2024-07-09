from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import View
from django.http import HttpRequest, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
from django.db.models import CharField, F, Value as V, Func, Sum, When, Case, Q, FloatField, Count, Exists, OuterRef
from django.db.models.functions import Cast, Concat
from django.conf import settings
from django.utils.decorators import method_decorator
from django.db import transaction
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from system_manage.decorators import permission_required
from shop_manage.views.shop_manage_views.auth_views import check_shop
from system_manage.models import ShopPersonType, PersonType, Goods
import json

class PersonTypeManageView(View):
    '''
        입장 사람 변수 관리
    '''
    @method_decorator(permission_required(redirect_url='shop_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return redirect('shop_manage:notfound')
        context['shop'] = shop
        
        paginate_by = '20'
        page = request.GET.get('page', '1')
        search_type = request.GET.get('search_type', '')
        search_keyword = request.GET.get('search_keyword', '')

        filter_dict = {}
        filter_dict['shop'] = shop
        
        if search_keyword:
            context['search_type'] = search_type
            context['search_keyword'] = search_keyword
            filter_dict[search_type + '__icontains'] = search_keyword


        obj_list = ShopPersonType.objects.filter(**filter_dict).values(
            'id',
            'person_type__name',
            'description',
            'goods',
            'goods__name',
            'created_at'
        ).order_by('id')

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

        return render(request, 'entry_manage/person_type_manage.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def put(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return JsonResponse({'message' : '가맹점 오류'},status = 400)
        
        request.PUT = json.loads(request.body)
        reqType = request.PUT['reqType']

        if reqType == 'EMAIL':
            shop.entry_email = not shop.entry_email
        elif reqType == 'CAR':
            shop.entry_car_plate_no = not shop.entry_car_plate_no
        else:
            return JsonResponse({'message' : '코드오류'},  status = 400)
        
        shop.save()

        return JsonResponse({'message' : '수정완료'},  status = 201)


class PersonTypeCreateView(View):
    '''
        입장 사람 변수 등록
    '''
    @method_decorator(permission_required(redirect_url='shop_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return redirect('shop_manage:notfound')
        context['shop'] = shop

        shop_person_type_id_list = list(ShopPersonType.objects.filter(shop=shop_id).values_list('person_type', flat=True))
        person_type_list = PersonType.objects.exclude(id__in=shop_person_type_id_list).values('id', 'name')
        context['person_type_list'] = person_type_list

        return render(request, 'entry_manage/person_type_create.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return JsonResponse({'message' : '가맹점 오류'},status = 400)
        
        person_type_id = request.POST['person_type_id']
        description = request.POST['description'].strip()

        try:
            person_type = PersonType.objects.get(pk=person_type_id)
        except:
            return JsonResponse({'message' : '데이터 오류'},status = 400)
        
        try:
            ShopPersonType.objects.get(shop=shop, person_type=person_type)
            return JsonResponse({'message': '이미 등록된 이름입니다.'}, status=400)
        except:
            pass

        try:
            with transaction.atomic():
                shop_person_type = ShopPersonType.objects.create(
                    shop=shop,
                    person_type=person_type,
                    description=description
                )     
        except:
            return JsonResponse({'message' : '등록오류'},status = 400)
        
        return JsonResponse({'message' : '생성 완료', 'url':reverse('shop_manage:person_type_detail', kwargs={'shop_id':shop.id, 'pk':shop_person_type.id})},  status = 201)


class PersonTypeDetailView(View):
    '''
        입장 사람 변수 상세
    '''
    @method_decorator(permission_required(redirect_url='shop_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        shop_id = kwargs.get('shop_id')
        pk = kwargs.get('pk')

        shop = check_shop(pk=shop_id)
        if not shop:
            return redirect('shop_manage:notfound')
        context['shop'] = shop
        
        shop_person_type = get_object_or_404(ShopPersonType, pk=pk, shop=shop)
        context['shop_person_type'] = shop_person_type

        return render(request, 'entry_manage/person_type_detail.html', context)
    

    @method_decorator(permission_required(raise_exception=True))
    def delete(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return JsonResponse({'message' : '가맹점 오류'},status = 400)
        
        pk = kwargs.get("pk")
        try:
            shop_person_type= ShopPersonType.objects.get(pk=pk, shop=shop)
        except:
            return JsonResponse({'message' : '데이터 오류'},  status = 400)
        
        shop_person_type.delete()
        
        return JsonResponse({'message' : '삭제 완료', 'url':reverse('shop_manage:person_type_manage', kwargs={'shop_id':shop.id})},  status = 202)


class PersonTypeEditView(View):
    '''
        입장 사람 변수 수정
    '''
    @method_decorator(permission_required(redirect_url='shop_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        shop_id = kwargs.get('shop_id')
        pk = kwargs.get('pk')

        shop = check_shop(pk=shop_id)
        if not shop:
            return redirect('shop_manage:notfound')
        context['shop'] = shop
        
        shop_person_type = get_object_or_404(ShopPersonType, pk=pk, shop=shop)
        context['shop_person_type'] = shop_person_type

        shop_person_type_id_list = list(ShopPersonType.objects.filter(shop=shop_id).exclude(pk=pk).values_list('person_type', flat=True))
        person_type_list = PersonType.objects.exclude(id__in=shop_person_type_id_list).values('id', 'name')
        context['person_type_list'] = person_type_list

        return render(request, 'entry_manage/person_type_edit.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return JsonResponse({'message' : '가맹점 오류'},status = 400)
        
        pk = kwargs.get("pk")
        try:
            shop_person_type= ShopPersonType.objects.get(pk=pk, shop=shop)
        except:
            return JsonResponse({'message' : '데이터 오류'},  status = 400)
        
        person_type_id = request.POST['person_type_id']
        description = request.POST['description'].strip()

        try:
            person_type = PersonType.objects.get(pk=person_type_id)
        except:
            return JsonResponse({'message' : '데이터 오류'},status = 400)
        
        if ShopPersonType.objects.filter(shop=shop, person_type=person_type).exclude(pk=pk).exists():
            return JsonResponse({'message': '이미 등록되어있습니다.'}, status=400)
        
        shop_person_type.person_type = person_type
        shop_person_type.description = description
        shop_person_type.save()

        
        return JsonResponse({'message' : '수정 완료', 'url':reverse('shop_manage:person_type_detail', kwargs={'shop_id':shop.id, 'pk':shop_person_type.id})},  status = 201)
    

class PersonTypeGoodsManageView(View):
    '''
        입장 사람 상품 관리
    '''
    @method_decorator(permission_required(redirect_url='shop_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        shop_id = kwargs.get('shop_id')
        pk = kwargs.get('pk')
        shop = check_shop(pk=shop_id)
        if not shop:
            return redirect('shop_manage:notfound')
        context['shop'] = shop
        shop_person_type = get_object_or_404(ShopPersonType, pk=pk, shop=shop)
        context['shop_person_type'] = shop_person_type
        
        paginate_by = '20'
        page = request.GET.get('page', '1')
        search_type = request.GET.get('search_type', '')
        search_keyword = request.GET.get('search_keyword', '')

        filter_dict = {}
        filter_dict['shop'] = shop
        filter_dict['delete_flag'] = False
        
        if search_keyword:
            context['search_type'] = search_type
            context['search_keyword'] = search_keyword
            filter_dict[search_type + '__icontains'] = search_keyword

        obj_list = Goods.objects.filter(**filter_dict).annotate(
            imageThumbnailUrl=Case(
                When(image_thumbnail='', then=Concat(V(settings.SITE_URL), V(settings.MEDIA_URL), V('image/goods/default.jpg'))),
                When(image_thumbnail=None, then=Concat(V(settings.SITE_URL), V(settings.MEDIA_URL), V('image/goods/default.jpg'))),
                default=Concat(V(settings.SITE_URL), V(settings.MEDIA_URL), 'image_thumbnail', output_field=CharField())
            )
        ).values(
            'id',
            'imageThumbnailUrl',
            'name',
        ).order_by('id')

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

        return render(request, 'entry_manage/person_type_goods.html', context)
    
        
    @method_decorator(permission_required(raise_exception=True))
    def put(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return JsonResponse({'message' : '가맹점 오류'},status = 400)
        
        pk = kwargs.get("pk")
        try:
            shop_person_type= ShopPersonType.objects.get(pk=pk, shop=shop)
        except:
            return JsonResponse({'message' : '데이터 오류'},  status = 400)
        
        request.PUT = json.loads(request.body)
        goods_id = request.PUT['goods_id']

        try:
            goods = Goods.objects.get(pk=goods_id, shop=shop)
        except:
            return JsonResponse({'message' : '상품 데이터 오류'},  status = 400)
        
        if shop_person_type.goods:
            if shop_person_type.goods.pk == goods.pk:
                shop_person_type.goods = None
                shop_person_type.save()
                return JsonResponse({'message' : '수정완료'},  status = 201)

        shop_person_type.goods = goods
        shop_person_type.save()
        return JsonResponse({'message' : '수정완료'},  status = 201)
