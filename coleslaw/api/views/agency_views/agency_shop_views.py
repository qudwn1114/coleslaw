from django.conf import settings
from django.views.generic import View
from django.urls import reverse
from django.http import HttpRequest, JsonResponse, HttpResponse
from system_manage.models import Agency, AgencyShop, Shop, Goods, SubCategory, MainCategory
from django.db.models.functions import Concat
from django.db.models import CharField, F, Value as V, Func, Case, When
from django.core.serializers.json import DjangoJSONEncoder

import traceback, json, datetime

class AgencyShopListView(View):
    '''
        agency shop list api
    '''
    def post(self, request: HttpRequest, *args, **kwargs):
        agency_id = kwargs.get('agency_id')
        try:
            agency = Agency.objects.get(pk=agency_id)
            page = int(request.POST.get('page', 1))
            startnum = 0 + (page-1)*10
            endnum = startnum+10
            queryset = AgencyShop.objects.filter(agency=agency, status=True).annotate(
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
                    'shopName',
                    'shopDescription',
                    'shopImageUrl',
                    'shopDetailUrl'
                ).order_by('-id')

            return_data = {
                'data': list(queryset[startnum:endnum]),
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
            print(shop_main_category_id_list)
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