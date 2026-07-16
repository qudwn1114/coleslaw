from django.conf import settings
from django.views.generic import View
from django.urls import reverse
from django.http import HttpRequest, JsonResponse, HttpResponse
from system_manage.models import ShopCategory, Agency, AgencyShop, Shop, Goods, SubCategory, MainCategory, GoodsOptionDetail
from django.db.models.functions import Concat
from django.db.models import CharField, F, Value as V, Func, Case, When, Prefetch
from django.core.serializers.json import DjangoJSONEncoder

from collections import defaultdict
import traceback, json, datetime

class AgencyShopCategoryListView(View):
    '''
        agency shop list api
    '''
    def get(self, request: HttpRequest, *args, **kwargs):
        agency_id = kwargs.get('agency_id')
        try:
            shop_category_ids = AgencyShop.objects.filter(
                agency_id=agency_id,
                status=True,
            ).values('shop__shop_category').distinct()

            queryset = (
                ShopCategory.objects.filter(id__in=shop_category_ids)
                .annotate(
                    categoryImageUrl=Case(
                        When(image='', then=None),
                        When(image__isnull=True, then=None),
                        default=Concat(
                            V(settings.SITE_URL),
                            V(settings.MEDIA_URL),
                            'image',
                            output_field=CharField()
                        )
                    )
                )
                .values(
                    'id',
                    'name_kr',
                    'name_en',
                    'description',
                    'categoryImageUrl',
                )
                .order_by('id')
            )
            data = list(queryset)

            return_data = {
                'data': data,
                'resultCd': '0000',
                'msg': '에이전시 가맹점 카테고리 리스트',
                'totalCnt': len(data),
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
                    shopNameKr=F('shop__name_kr'),
                    shopNameEn=F('shop__name_en'),
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
                    'shopNameKr',
                    'shopNameEn',
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
            # 판매중인 상품의 서브카테고리
            goods_sub_categories = Goods.objects.filter(
                shop_id=shop_id,
                delete_flag=False,
                status=True,
                kiosk_display=True,
            ).values('sub_category').distinct()

            # 메인카테고리
            main_categories = list(
                MainCategory.objects.filter(
                    shop_id=shop_id,
                    id__in=SubCategory.objects.filter(
                        id__in=goods_sub_categories
                    ).values('main_category_id')
                )
                .values(
                    'id',
                    'name_kr',
                    'name_en',
                )
                .order_by('rank')
            )

            # 서브카테고리(한 번만 조회)
            sub_categories = list(
                SubCategory.objects.filter(
                    shop_id=shop_id,
                    id__in=goods_sub_categories,
                )
                .values(
                    'id',
                    'name_kr',
                    'name_en',
                    'main_category_id',
                )
                .order_by('rank')
            )

            # 메인카테고리별로 그룹핑
            sub_category_map = defaultdict(list)

            for sub in sub_categories:
                main_category_id = sub.pop('main_category_id')
                sub_category_map[main_category_id].append(sub)

            for main in main_categories:
                main['sub_category'] = sub_category_map.get(main['id'], [])

            return_data = {
                'data': main_categories,
                'resultCd': '0000',
                'msg': '가맹점 카테고리 리스트',
                'totalCnt': len(main_categories),
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
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        main_category_id = request.GET.get('main_category_id', '') 
        sub_category_id = request.GET.get('sub_category_id', '')
        device = request.GET.get('device', 'POS') # POS or KIOSK
        if device == 'POS':
            order_col_name = 'pos_rank'
        elif device == "KIOSK":
            order_col_name =  'kiosk_rank'
        else:
            order_col_name = 'pos_rank'

        filter_dict ={}

        if main_category_id:
            filter_dict['sub_category__main_category_id'] = main_category_id
            if sub_category_id:
                filter_dict['sub_category_id'] = sub_category_id

        filter_dict['shop'] = shop
        filter_dict['delete_flag'] = False
        filter_dict['status'] = True
        filter_dict['kiosk_display'] = True

        try:
            queryset = Goods.objects.filter(**filter_dict).annotate(
                    goodsImageThumbnailUrl=Case(
                        When(image_thumbnail='', then=None),
                        When(image_thumbnail=None, then=None),
                        default=Concat(V(settings.SITE_URL), V(settings.MEDIA_URL), 'image_thumbnail', output_field=CharField())
                    ),
                ).values(
                    'id',
                    'name_kr',
                    'name_en',
                    'sale_price',
                    'price',
                    'status',
                    'option_flag',
                    'soldout',
                    'goodsImageThumbnailUrl'
                ).order_by(order_col_name)

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
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")

        try:
            data = {
                'id': goods.pk,
                'name_kr': goods.name_kr,
                'name_en': goods.name_en,
                'sale_price': goods.sale_price,
                'price': goods.price,
                'goodsImageThumbnailUrl': settings.SITE_URL + goods.image.url if goods.image else None,
                'status': goods.status,
                'soldout': goods.soldout,
                'option_flag': goods.option_flag,
            }
            if goods.option_flag:

                options = list(
                    goods.option.values(
                        'id',
                        'required',
                        'name_kr',
                        'name_en',
                    ).order_by('id')
                )

                if options:
                    option_ids = [o['id'] for o in options]

                    option_details = list(
                        GoodsOptionDetail.objects.filter(
                            goods_option_id__in=option_ids
                        ).values(
                            'id',
                            'goods_option_id',
                            'name_kr',
                            'name_en',
                            'price',
                            'stock',
                            'stock_flag',
                            'soldout',
                        ).order_by('id')
                    )

                    detail_map = defaultdict(list)

                    for detail in option_details:
                        goods_option_id = detail.pop('goods_option_id')
                        detail_map[goods_option_id].append(detail)

                    for option in options:
                        option['option_detail'] = detail_map.get(option['id'], [])

                    data['option'] = options
                else:
                    data['option'] = []
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