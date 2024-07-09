from django.conf import settings
from django.views.generic import View
from django.urls import reverse
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.db.models.functions import Concat
from django.db.models import CharField, F, Value as V, Func, Case, When, Prefetch
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from system_manage.models import Shop, ShopPersonType, ShopEntryOption, ShopEntryOptionDetail

import traceback, json, datetime

class ShopDetailView(View):
    '''
        entry shop detail api
    '''
    def get(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        try:
            shop = Shop.objects.get(pk=shop_id)
            data = {}            
            data['agencyName'] = shop.agency.name
            data['shopCategoryName'] = shop.shop_category.name
            data['shopName'] = shop.name
            data['shopDescription'] = shop.description
            data['shopRepresentative'] = shop.representative
            data['shopAddress'] = shop.address
            data['shopAddressDetail'] = shop.address_detail
            data['shopZipcode'] = shop.zipcode

            data['shopEntryOrder'] = 10
            data['shopEntryTime'] = 30

            if shop.image:
                data['shopImageUrl'] = settings.SITE_URL + shop.image.url
            else:
                data['shopImageUrl'] = None 
            if shop.logo_image:
                data['shopLogoImageUrl'] = settings.SITE_URL + shop.logo_image.url
            else:
                data['shopLogoImageUrl'] = None
            if shop.entry_image:
                data['shopEntryImageUrl'] = settings.SITE_URL + shop.entry_image.url
            else:
                data['shopEntryImageUrl'] = None

            return_data = {
                'data': data,
                'resultCd': '0000',
                'msg': '가맹점 정보',
            }
        except:
            print(traceback.format_exc())
            return_data = {
                'data': {},
                'msg': '오류!',
                'resultCd': '0001',
            }
    
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")

class ShopEntryDetailView(View):
    '''
        entry shop detail api
    '''
    def get(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        try:
            shop = Shop.objects.get(pk=shop_id)
            data = {}
            data['shopName'] = shop.name
            data['entryMembername'] = shop.entry_membername
            data['entryPhone'] = shop.entry_phone
            data['entryEmail'] = shop.entry_email
            data['entryCarPlateNo'] = shop.entry_car_plate_no
            entry_person_type = ShopPersonType.objects.filter(shop=shop).annotate(
                personTypeName=F('person_type__name'),
                personTypeImageUrl=Case(
                    When(person_type__image='', then=Concat(V(settings.SITE_URL), V(settings.MEDIA_URL), V('image/goods/default.jpg'))),
                    When(person_type__image=None, then=Concat(V(settings.SITE_URL), V(settings.MEDIA_URL), V('image/goods/default.jpg'))),
                    default=Concat(V(settings.SITE_URL), V(settings.MEDIA_URL), 'person_type__image', output_field=CharField())
                ),
            ).values(
                'id',
                'personTypeName',
                'personTypeImageUrl',
                'description'
            ).order_by('id')
            data['enrtyPersonType'] = list(entry_person_type)

            option_queryset = shop.entry_option.all().values('id', 'required', 'name').order_by('id')
            for i in option_queryset:
                i['entryOptionDetail'] = list(
                    ShopEntryOptionDetail.objects.filter(shop_entry_option_id=i['id']).annotate(
                        optionDetailImageUrl=Case(
                            When(image='', then=Concat(V(settings.SITE_URL), V(settings.MEDIA_URL), V('image/goods/default.jpg'))),
                            When(image=None, then=Concat(V(settings.SITE_URL), V(settings.MEDIA_URL), V('image/goods/default.jpg'))),
                            default=Concat(V(settings.SITE_URL), V(settings.MEDIA_URL), 'image', output_field=CharField())
                        ),
                    ).values('id', 'name', 'optionDetailImageUrl').order_by('id')
                )
            data['entryOption'] = list(option_queryset)

            return_data = {
                'data': data,
                'resultCd': '0000',
                'msg': '가맹점 입장 입력/옵션 정보',
            }
        except:
            print(traceback.format_exc())
            return_data = {
                'data': {},
                'msg': '오류!',
                'resultCd': '0001',
            }
    
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")
