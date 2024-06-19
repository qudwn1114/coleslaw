from django.conf import settings
from django.views.generic import View
from django.urls import reverse
from django.http import HttpRequest, JsonResponse, HttpResponse
from system_manage.models import ShopCategory, Agency, AgencyShop, Shop, Goods, SubCategory, MainCategory, GoodsOptionDetail
from django.db.models.functions import Concat
from django.db.models import CharField, F, Value as V, Func, Case, When, Prefetch
from django.core.serializers.json import DjangoJSONEncoder

import traceback, json, datetime

class AgencyShopCategoryListView(View):
    '''
        agency shop list api
    '''
    def get(self, request: HttpRequest, *args, **kwargs):
        agency_id = kwargs.get('agency_id')
        try:
            agency = Agency.objects.get(pk=agency_id)
            shop_category = AgencyShop.objects.filter(agency=agency, status=True).values('shop__shop_category').distinct()
            shop_category_id_list = list(shop_category.values_list('shop__shop_category', flat=True))
            

            queryset = ShopCategory.objects.filter(id__in=shop_category_id_list).annotate(
                    categoryImageUrl=Case(
                        When(image='', then=None),
                        When(image=None, then=None),
                        default=Concat(V(settings.SITE_URL), V(settings.MEDIA_URL), 'image', output_field=CharField())
                    )
                ).values(
                    'id',
                    'name',
                    'description',
                    'categoryImageUrl',
                ).order_by('id')

            return_data = {
                # 'data': list(queryset[startnum:endnum]),
                'data': list(queryset),
                'resultCd': '0000',
                'msg': '에이전시 가맹점 카테고리 리스트',
                'totalCnt' : queryset.count()
            }
        except:
            print(traceback.format_exc())
            return_data = {
                'data': [],
                'msg': '오류!',
                'resultCd': '0001',
            }
    
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")
    


class AgencyShopListView(View):
    '''
        agency shop list api
    '''
    def get(self, request: HttpRequest, *args, **kwargs):
        agency_id = kwargs.get('agency_id')
        shop_category_id = kwargs.get('shop_category_id')
        try:
            agency = Agency.objects.get(pk=agency_id)
        except:
            return_data = {
                'data': [],
                'msg': 'agency id 오류',
                'resultCd': '0001',
            }
        try:
            shop_category = ShopCategory.objects.get(pk=shop_category_id)
        except:
            return_data = {
                'data': [],
                'msg': 'shop_category id 오류',
                'resultCd': '0001',
            }
        try:
            # page = int(request.POST.get('page', 1))
            # startnum = 0 + (page-1)*10
            # endnum = startnum+10
            queryset = AgencyShop.objects.filter(agency=agency, shop__shop_category=shop_category, status=True).annotate(
                    shopId=F('shop_id'),
                    shopName=F('shop__name'),
                    shopDescription=F('shop__description'),
                    shopImageUrl=Case(
                        When(shop__image='', then=None),
                        When(shop__image=None, then=None),
                        default=Concat(V(settings.SITE_URL), V(settings.MEDIA_URL), 'shop__image', output_field=CharField())
                    ),
                    shopDetailUrl = Concat(V(settings.SITE_URL), V('/shop/'), 'id',  V('/'),output_field=CharField()),
                ).values(
                    'id',
                    'shopId',
                    'shopName',
                    'shopDescription',
                    'shopImageUrl',
                    'shopDetailUrl'
                ).order_by('-id')

            return_data = {
                # 'data': list(queryset[startnum:endnum]),
                'data': list(queryset),
                'resultCd': '0000',
                'msg': '에이전시 소속 가맹점 리스트',
                'totalCnt' : queryset.count()
            }
        except:
            print(traceback.format_exc())
            return_data = {
                'data': [],
                'msg': '오류!',
                'resultCd': '0001',
            }
    
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")
    

class ShopMainCategoryListView(View):
    '''
        shop 메인 카테고리 list api
    '''
    def get(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        try:
            shop = Shop.objects.get(pk=shop_id)
        except:
            return_data = {
                'data': [],
                'msg': 'shop id 오류',
                'resultCd': '0001',
            }
        
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        try:
            shop_sub_category = Goods.objects.filter(shop=shop, delete_flag=False).values('sub_category').distinct()
            shop_sub_category_id_list = list(shop_sub_category.values_list('sub_category', flat=True))
            shop_main_category_id_list = list(shop_sub_category.values_list('sub_category__main_category', flat=True))
            queryset = MainCategory.objects.filter(id__in=shop_main_category_id_list).values(
                    'id',
                    'name'
                ).order_by('name')
            
            for i in queryset:
                i['sub_category'] = list(SubCategory.objects.filter(id__in=shop_sub_category_id_list, main_category_id=i['id']).values(
                    'id',
                    'name'
                ).order_by('name'))

            return_data = {
                'data': list(queryset),
                'resultCd': '0000',
                'msg': '가맹점 카테고리 리스트',
                'totalCnt' : queryset.count()
            }
        except:
            print(traceback.format_exc())
            return_data = {
                'data': [],
                'msg': '오류!',
                'resultCd': '0001',
            }
    
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")
    

class ShopGoodsListView(View):
    '''
        shop goods list api
    '''
    def get(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        try:
            shop = Shop.objects.get(pk=shop_id)
        except:
            return_data = {
                'data': [],
                'msg': 'shop id 오류',
                'resultCd': '0001',
            }
        
        main_category_id = request.GET.get('main_category_id', '') 
        sub_category_id = request.GET.get('sub_category_id', '')

        filter_dict ={}

        if main_category_id:
            filter_dict['sub_category__main_category_id'] = main_category_id
            if sub_category_id:
                filter_dict['sub_category_id'] = sub_category_id

        filter_dict['shop'] = shop
        filter_dict['delete_flag'] = False
        filter_dict['status'] = True

        try:
            queryset = Goods.objects.filter(**filter_dict).annotate(
                    goodsImageThumbnailUrl=Case(
                        When(image_thumbnail='', then=None),
                        When(image_thumbnail=None, then=None),
                        default=Concat(V(settings.SITE_URL), V(settings.MEDIA_URL), 'image_thumbnail', output_field=CharField())
                    ),
                ).values(
                    'id',
                    'name',
                    'sale_price',
                    'price',
                    'status',
                    'option_flag',
                    'soldout',
                    'goodsImageThumbnailUrl'
                ).order_by('-id')

            return_data = {
                'data': list(queryset),
                'resultCd': '0000',
                'msg': '상품 리스트',
                'totalCnt' : queryset.count()
            }
        except:
            print(traceback.format_exc())
            return_data = {
                'data': [],
                'msg': '오류!',
                'resultCd': '0001',
            }
    
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")
    
class ShopGoodsDetailView(View):
    '''
        shop goods detail api
    '''
    def get(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        goods_id = kwargs.get('goods_id')
        try:
            goods = Goods.objects.get(pk=goods_id, shop_id=shop_id)
        except:
            return_data = {
                'data': {},
                'msg': 'id 오류',
                'resultCd': '0001',
            }

        try:
            data = {}
            data['id'] = goods.pk
            data['name'] = goods.name
            data['sale_price'] = goods.sale_price
            data['price'] = goods.price
            if goods.image:
                data['goodsImageThumbnailUrl'] = settings.SITE_URL + goods.image.url
            else:
                data['goodsImageThumbnailUrl'] = None
            data['status'] = goods.status
            data['soldout'] = goods.soldout
            data['option_flag'] =goods.option_flag
            if goods.option_flag and goods.option.all().exists():
                option_queryset = goods.option.all().values('id', 'required', 'name').order_by('id')
                for i in option_queryset:
                    i['option_detail'] = list(GoodsOptionDetail.objects.filter(goods_option_id=i['id']).values('id', 'name', 'price', 'stock', 'stock_flag', 'soldout').order_by('id'))
                data['option'] = list(option_queryset)
            else:
                data['option'] = None


            return_data = {
                'data': data,
                'resultCd': '0000',
                'msg': '상품 상세'
            }
        except:
            print(traceback.format_exc())
            return_data = {
                'data': data,
                'msg': '오류!',
                'resultCd': '0001',
            }
    
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")