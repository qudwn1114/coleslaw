from django.conf import settings
from django.views.generic import View
from django.urls import reverse
from django.http import HttpRequest, JsonResponse, HttpResponse
from system_manage.models import Agency, AgencyShop
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