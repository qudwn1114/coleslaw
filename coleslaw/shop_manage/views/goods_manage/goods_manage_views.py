from django.shortcuts import render, redirect, resolve_url, get_object_or_404
from django.urls import reverse
from django.views.generic import View
from django.http import HttpRequest, JsonResponse
from django.db.models import CharField, F, Value as V, Func, Sum, When, Case, Q, FloatField, Count
from django.db.models.functions import Cast, Concat
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
from django.conf import settings
from django.db import transaction
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.core.files.base import ContentFile
from system_manage.utils import resize_with_padding
from system_manage.decorators import  permission_required
from system_manage.models import Shop, ShopAdmin, SubCategory, Goods, MainCategory

from shop_manage.views.shop_manage_views.auth_views import check_shop

from PIL import Image
from io import BytesIO

# Create your views here.
class GoodsManageView(View):
    '''
        Shop 상품관리
    '''
    @method_decorator(permission_required(redirect_url='shop_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return redirect('shop_manage:notfound')
        context['shop'] = shop
        
        return render(request, 'goods_manage/goods_manage.html', context)
    

class GoodsCreateView(View):
    '''
        상품등록
    '''
    @method_decorator(permission_required(redirect_url='shop_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return redirect('shop_manage:notfound')
        context['shop'] = shop

        return render(request, 'goods_manage/goods_create.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return JsonResponse({'message' : '가맹점 오류'},status = 400)
        
        sub_category_id = request.POST['sub_category']
        name = request.POST['goods_name'].strip()
        price = request.POST['price'] 
        status = bool(request.POST.get('status', None))
        image = request.FILES.get('image', None)

        try:
            sub_category = SubCategory.objects.get(pk=sub_category_id)
        except:
            return JsonResponse({'message' : '소분류 카테고리 데이터 오류'},status = 400)
        if image:
            crop_img = resize_with_padding(img=Image.open(image), expected_size=(800, 800), fill=(255,255,255))
            img_io = BytesIO()
            crop_img.save(img_io, format='PNG', quality=100)
            image_thumbnail=ContentFile(img_io.getvalue(), image.name)
        else:
            image = 'image/goods/default.jpg'
            image_thumbnail='image/goods/default.jpg'
        try:
            with transaction.atomic():
                goods = Goods.objects.create(
                    shop=shop,
                    sub_category=sub_category,
                    name=name,
                    price=price,
                    image=image,
                    image_thumbnail=image_thumbnail,
                    status=status
                )     
        except:
            return JsonResponse({'message' : '등록오류'},status = 400)
        
        return JsonResponse({'message' : '생성 완료', 'url':reverse('shop_manage:goods_detail', kwargs={'shop_id':shop.id, 'pk':goods.id})},  status = 201)
    

class GoodsDetailView(View):
    '''
        상품상세
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
        
        goods = get_object_or_404(Goods, pk=pk, shop=shop)
        context['goods'] = goods

        return render(request, 'goods_manage/goods_detail.html', context)
    

    @method_decorator(permission_required(raise_exception=True))
    def delete(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return JsonResponse({'message' : '가맹점 오류'},status = 400)
        
        pk = kwargs.get("pk")
        try:
            goods= Goods.objects.get(pk=pk)
        except:
            return JsonResponse({'message' : '데이터 오류'},  status = 400)
        
        goods.delete_flag = True
        goods.save()
        
        return JsonResponse({'message' : '삭제 완료', 'url':reverse('shop_manage:goods_manage', kwargs={'shop_id':shop.id})},  status = 202)


class GoodsEditView(View):
    '''
        상품수정
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
        
        goods = get_object_or_404(Goods, pk=pk, shop=shop)
        context['goods'] = goods

        context['main_category'] = MainCategory.objects.all().values('id', 'name')
        context['sub_category'] = SubCategory.objects.filter(main_category=goods.sub_category.main_category).values('id', 'name')

        return render(request, 'goods_manage/goods_edit.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return JsonResponse({'message' : '가맹점 오류'},status = 400)
        
        pk = kwargs.get("pk")
        try:
            goods= Goods.objects.get(pk=pk)
        except:
            return JsonResponse({'message' : '데이터 오류'},  status = 400)
        
        sub_category_id = request.POST['sub_category']
        name = request.POST['goods_name'].strip()
        price = request.POST['price']
        image = request.FILES.get('image', None)
        status = bool(request.POST.get('status', None))
        try:
            sub_category = SubCategory.objects.get(pk=sub_category_id)
        except:
            return JsonResponse({'message' : '소분류 카테고리 데이터 오류'},status = 400)
        try:
            goods.sub_category  = sub_category
            goods.name = name
            goods.price = price
            goods.status = status
            if image:
                crop_img = resize_with_padding(img=Image.open(image), expected_size=(800, 800), fill=(255,255,255))
                img_io = BytesIO()
                crop_img.save(img_io, format='PNG', quality=100)
                image_thumbnail=ContentFile(img_io.getvalue(), image.name)

                goods.image = image
                goods.image_thumbnail = image_thumbnail

            goods.save()

        except:
            return JsonResponse({'message' : '수정오류'},status = 400)

        return JsonResponse({'message' : '수정 완료', 'url':reverse('shop_manage:goods_detail', kwargs={'shop_id':shop.id, 'pk':goods.id})},  status = 201)

        

@require_http_methods(["GET"])
def goods(request: HttpRequest, *args, **kwargs):
    '''
        상품 리스트
    '''
    shop_id = kwargs.get('shop_id')
    shop = check_shop(pk=shop_id)
    if not shop:
        return JsonResponse({'message' : '가맹점 오류'}, status = 400)
        
    # paging
    draw = int(request.GET.get('draw', 1)) # count. ajax요청에 의해 그려질 때 dataTable이 순차적으로 그려지는 것을 보장하기 위해 사용
    start = int(request.GET.get('start', 0)) #페이징 첫번째 레코드 값
    length = int(request.GET.get('length', 0)) #현재 페이지에 그려질 레코드 수

    # ordering
    order_idx = int(request.GET.get('order[0][column]', 0))
    order_dir = request.GET.get('order[0][dir]')
    order_col = 'columns[' + str(order_idx) + '][data]'
    order_col_name = request.GET.get(order_col, 'id')
    if (order_dir == "desc"):
        order_col_name =  str('-' + order_col_name)

    filter_dict = {}
    filter_dict['delete_flag'] =False
    search_type = request.GET.get('search_type', '')
    search_keyword = request.GET.get('search_keyword', '')

    main_category_id = request.GET.get('main_category_id', '')
    sub_category_id = request.GET.get('sub_category_id', '')

    if search_keyword:
        filter_dict[search_type + '__icontains'] = search_keyword
    if main_category_id:
        filter_dict['sub_category__main_category_id'] = main_category_id
        if sub_category_id:
            filter_dict['sub_category_id'] = sub_category_id

    goods_status = request.GET.get('status', '1')
    if goods_status == '1':
        pass
    elif goods_status == '2':
        filter_dict['status'] = True
    elif goods_status == '3':
        filter_dict['status'] = False
    
    queryset=Goods.objects.filter(**filter_dict).annotate(
        imageThumbnailUrl=Case(
            When(image_thumbnail='', then=Concat(V(request._current_scheme_host), V(settings.MEDIA_URL), V('image/goods/default.jpg'))),
            When(image_thumbnail=None, then=Concat(V(request._current_scheme_host), V(settings.MEDIA_URL), V('image/goods/default.jpg'))),
            default=Concat(V(request._current_scheme_host), V(settings.MEDIA_URL), 'image_thumbnail', output_field=CharField())
        ),
        goodsStatus=Case(
            When(status='0', then=V('판매중단')),
            When(status='1', then=V('판매중')),
        ),
        mainCategoryName = F('sub_category__main_category__name'),
        subCategoryName = F('sub_category__name'),
        createdAt=Func(
            F('created_at'),
            V('%Y.%m.%d'),
            function='DATE_FORMAT',
            output_field=CharField()
        )
    ).values(
        'id',
        'imageThumbnailUrl',
        'name',
        'price',
        'mainCategoryName',
        'subCategoryName',
        'status',
        'goodsStatus',
        'createdAt'
    ).order_by(order_col_name)

    total = queryset.count()
    
    paginator = Paginator(queryset, length)
    page_number = int(start / length + 1)
    page = request.GET.get('page', '')
    if page:
        page_number = page
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_number = 1
        page_obj = paginator.page(page_number)
    except EmptyPage:
        page_number = 1
        page_obj = paginator.page(page_number)
    except InvalidPage:
        page_number = 1
        page_obj = paginator.page(page_number)

    data = {
        'data': list(page_obj.object_list),
        'draw': draw,
        'recordsTotal': total,
        'recordsFiltered': total,
        'page' : page_number
    }
    return JsonResponse(data, status = 200)