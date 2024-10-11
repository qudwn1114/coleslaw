from django.conf import settings
from django.views.generic import View
from django.urls import reverse
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.db.models.functions import Concat
from django.db.models import CharField, F, Value as V, Func, Case, When, Prefetch
from django.core.serializers.json import DjangoJSONEncoder

from system_manage.models import Agency, Order, Shop, OrderPayment

import traceback, json

class AgencyDetailView(View):
    '''
        agency detail api
    '''
    def get(self, request: HttpRequest, *args, **kwargs):
        agency_id = kwargs.get('agency_id')
        try:
            agency = Agency.objects.get(pk=agency_id)
            data = {}
            data['id'] = agency.pk
            data['name'] = agency.name
            data['description'] = agency.description
            if agency.image:
                data['imageUrl'] = settings.SITE_URL + agency.image.url
            else:
                data['imageUrl'] = None
            data['qr_order_note'] = agency.qr_order_note
            return_data = {
                'data': data,
                'resultCd': '0000',
                'msg': 'Agency 정보',
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
