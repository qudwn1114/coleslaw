from django.shortcuts import render, redirect, resolve_url, get_object_or_404
from django.urls import reverse
from django.views.generic import View
from django.http import HttpRequest, JsonResponse
from django.db.models import CharField, F, Value as V, Func, Sum, When, Case, Q, FloatField, Count, Exists, OuterRef
from django.db.models.functions import Cast, Concat
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
from django.conf import settings
from django.db import transaction, IntegrityError
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.core.files.base import ContentFile
from system_manage.utils import resize_with_padding, generate_code
from system_manage.decorators import  permission_required
from system_manage.models import Shop, ShopAdmin, SubCategory, Goods, MainCategory

from shop_manage.views.shop_manage_views.auth_views import check_shop

from urllib.parse import quote
from PIL import Image
from io import BytesIO
import json

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
        context['cur_url'] = quote(request.get_full_path())
        
        return render(request, 'goods_manage/goods_manage.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def put(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return JsonResponse({'message' : '가맹점 오류'},status = 400)
        
        request.PUT = json.loads(request.body)
        rq_type = request.PUT['type']
        goods_id = request.PUT['goods_id']
        try:
            goods = Goods.objects.get(pk=goods_id, shop=shop)
        except:
            return JsonResponse({"message": "데이터 오류"},status=400)
        if rq_type == 'STATUS':
            goods.status = not goods.status
            goods.save()
        elif rq_type == 'SOLDOUT':
            goods.soldout = not goods.soldout
            goods.save()
        elif rq_type == 'PRICE':
            value = request.PUT['value']
            goods.price = value
            goods.save()
        elif rq_type == 'SALE_PRICE':
            value = request.PUT['value']
            goods.sale_price = value
            goods.save()
        elif rq_type == 'STOCK':
            value = request.PUT['value']
            goods.stock = value
            goods.save()
        elif rq_type == 'STOCK_FLAG':
            goods.stock_flag = not goods.stock_flag
            goods.save()
        elif rq_type == 'OPTION_FLAG':
            if not goods.option_flag:
                if not goods.option.all().exists():
                    return JsonResponse({'message' : '옵션사용을 하시려면 옵션등록이 되어있어야합니다.'},status = 400)
                
            goods.option_flag = not goods.option_flag
            goods.save()
        else:
            return JsonResponse({"message": "타입 오류"},status=400)
        
        return JsonResponse({'message' : '변경되었습니다.'}, status = 201)
    

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
        context['cur_url'] = quote(request.get_full_path())
        prev_url = request.GET.get('prev_url', None)
        if not prev_url:
            prev_url = reverse("shop_manage:goods_manage", kwargs={'shop_id':shop.pk})
        context['prev_url'] = prev_url

        return render(request, 'goods_manage/goods_create.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return JsonResponse({'message' : '가맹점 오류'},status = 400)
        
        code = "ROOTME_"+generate_code()
        
        sub_category_id = request.POST['sub_category']
        name_kr = request.POST['goods_name_kr'].strip()
        name_en = request.POST['goods_name_en'].strip()
        price = request.POST['price'] 
        sale_price = request.POST['sale_price'] 
        stock = request.POST['stock']
        status = bool(request.POST.get('status', None))
        soldout = bool(request.POST.get('soldout', None))
        stock_flag = bool(request.POST.get('stock_flag', None))
        kiosk_display = bool(request.POST.get('kiosk_display', None))
        image = request.FILES.get('image', None)
        after_payment_goods_id_list = request.POST['after_payment_goods_id_list']

        try:
            sub_category = SubCategory.objects.get(pk=sub_category_id, shop=shop)
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

        after_payment_goods_id_list = after_payment_goods_id_list.replace(' ', '')            
        if after_payment_goods_id_list:
            after_payment_goods = ''
            after_payment_goods_id_list = after_payment_goods_id_list.split(',')
            for i in after_payment_goods_id_list:
                try:
                    g = Goods.objects.get(pk=int(i), shop=shop).pk
                    after_payment_goods += f"{i},"
                except:
                    return JsonResponse({'message' : '결제 후 상품 형식 오류..'},status = 400)
            if after_payment_goods:
                after_payment_goods = after_payment_goods.strip().rstrip(',')
            else:
                after_payment_goods = None
        else:
            after_payment_goods = None

        try:
            with transaction.atomic():
                goods = Goods.objects.create(
                    code=code,
                    shop=shop,
                    sub_category=sub_category,
                    name_kr=name_kr,
                    name_en=name_en,
                    price=price,
                    sale_price=sale_price,
                    stock=stock,
                    image=image,
                    image_thumbnail=image_thumbnail,
                    status=status,
                    soldout=soldout,
                    kiosk_display=kiosk_display,
                    stock_flag=stock_flag,
                    after_payment_goods=after_payment_goods
                )
        except IntegrityError:
            return JsonResponse({'message' : '잠시후 다시 시도해주세요.'},status = 400)
        except:
            return JsonResponse({'message' : '등록오류'},status = 400)
        
        prev_url = request.GET.get('prev_url', None)
        next_url = reverse('shop_manage:goods_detail', kwargs={'shop_id':shop.id, 'pk':goods.id})
        
        return JsonResponse({'message' : '생성 완료', 'url': f"{next_url}?prev_url={prev_url}" if prev_url else next_url},  status = 201)
    

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

        context['cur_url'] = quote(request.get_full_path())
        prev_url = request.GET.get('prev_url', None)
        if not prev_url:
            prev_url = reverse("shop_manage:goods_manage", kwargs={'shop_id':shop.pk})
        context['prev_url'] = prev_url

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
        context['cur_url'] = quote(request.get_full_path())
        prev_url = request.GET.get('prev_url', None)
        if not prev_url:
            prev_url = reverse('shop_manage:goods_detail', kwargs={'shop_id':shop.id, 'pk':goods.id})
        context['prev_url'] = prev_url

        context['main_category'] = MainCategory.objects.filter(shop=shop).order_by('name_kr').values('id', 'name_kr')
        context['sub_category'] = SubCategory.objects.filter(main_category=goods.sub_category.main_category, shop=shop).order_by('name_kr').values('id', 'name_kr')

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
        name_kr = request.POST['goods_name_kr'].strip()
        name_en = request.POST['goods_name_en'].strip()
        price = request.POST['price']
        sale_price = request.POST['sale_price']
        image = request.FILES.get('image', None)
        status = bool(request.POST.get('status', None))
        soldout = bool(request.POST.get('soldout', None))
        stock_flag = bool(request.POST.get('stock_flag', None))
        option_flag = bool(request.POST.get('option_flag', None))
        kiosk_display = bool(request.POST.get('kiosk_display', None))
        after_payment_goods_id_list = request.POST['after_payment_goods_id_list']
        additional_fee_goods_id = request.POST['additional_fee_goods_id']

        try:
            sub_category = SubCategory.objects.get(pk=sub_category_id, shop=shop)
        except:
            return JsonResponse({'message' : '소분류 카테고리 데이터 오류'},status = 400)
        
        if option_flag:
            if not goods.option.all().exists():
                return JsonResponse({'message' : '옵션사용을 하시려면 옵션등록이 되어있어야합니다.'},status = 400)
        after_payment_goods_id_list = after_payment_goods_id_list.replace(' ', '')            
        if after_payment_goods_id_list:
            after_payment_goods = ''
            after_payment_goods_id_list = after_payment_goods_id_list.split(',')
            for i in after_payment_goods_id_list:
                try:
                    g = Goods.objects.get(pk=int(i), shop=shop).pk
                    if g == goods.pk:
                        return JsonResponse({'message' : '결제후 상품은 동일상품으로 불가능합니다.'},status = 400)
                    after_payment_goods += f"{i},"
                except:
                    return JsonResponse({'message' : '결제 후 상품 형식 오류..'},status = 400)
            if after_payment_goods:
                after_payment_goods = after_payment_goods.strip().rstrip(',')
            else:
                after_payment_goods = None
        else:
            after_payment_goods = None
        
        if additional_fee_goods_id:
            try:
                additional_fee_goods = Goods.objects.get(pk=additional_fee_goods_id, shop=shop).pk
                if additional_fee_goods == goods.pk:
                    return JsonResponse({'message' : '결제후 상품은 동일상품으로 불가능합니다.'},status = 400)
            except:
                additional_fee_goods = None
        else:
            additional_fee_goods = None

        try:
            goods.sub_category  = sub_category
            goods.name_kr = name_kr
            goods.name_en = name_en
            goods.price = price
            goods.sale_price = sale_price
            goods.status = status
            goods.soldout = soldout
            goods.stock_flag = stock_flag
            goods.option_flag = option_flag
            goods.kiosk_display = kiosk_display
            goods.after_payment_goods = after_payment_goods
            goods.additional_fee_goods = additional_fee_goods
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

        prev_url = request.GET.get('prev_url', None)
        if not prev_url:
            prev_url = reverse('shop_manage:goods_detail', kwargs={'shop_id':shop.id, 'pk':goods.id})

        return JsonResponse({'message' : '수정 완료', 'url':prev_url},  status = 201)
        

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
    filter_dict['shop'] = shop
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
            When(image_thumbnail='', then=Concat(V(settings.SITE_URL), V(settings.MEDIA_URL), V('image/goods/default.jpg'))),
            When(image_thumbnail=None, then=Concat(V(settings.SITE_URL), V(settings.MEDIA_URL), V('image/goods/default.jpg'))),
            default=Concat(V(settings.SITE_URL), V(settings.MEDIA_URL), 'image_thumbnail', output_field=CharField())
        ),
        mainCategoryNameKr = F('sub_category__main_category__name_kr'),
        subCategoryNameKr = F('sub_category__name_kr'),
        createdAt=Func(
            F('created_at'),
            V('%y.%m.%d %H:%i'),
            function='DATE_FORMAT',
            output_field=CharField()
        )
    ).values(
        'id',
        'code',
        'imageThumbnailUrl',
        'name_kr',
        'price',
        'sale_price',
        'stock',
        'mainCategoryNameKr',
        'subCategoryNameKr',
        'status',
        'soldout',
        'stock_flag',
        'option_flag',
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