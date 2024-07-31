from django.conf import settings
from django.views.generic import View
from django.urls import reverse
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.db.models.functions import Concat
from django.db.models import CharField, F, Value as V, Func, Case, When, Prefetch
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction, IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from system_manage.models import Shop, Checkout, CheckoutDetailOption

import traceback, json, datetime

class PosCheckoutDetailView(View):
    '''
        pos checkout detail api
    '''
    def get(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        checkout_id = kwargs.get('checkout_id')
        code = kwargs.get('code')

        try:
            shop = Shop.objects.get(pk=shop_id)
        except:
            return_data = {'data': {},'msg': 'shop id 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")

        try:
            checkout = Checkout.objects.get(pk=checkout_id, shop=shop, code=code)
        except:
            return_data = {'data': {},'msg': 'checkout data 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        data = {}
        if checkout.shop_member:
            data['membername'] = checkout.shop_member.membername
        else:
            data['membername'] = None
            
        data['final_price'] = checkout.final_price
        data['final_discount'] = checkout.final_discount
        checkout_detail = checkout.checkout_detail.all().annotate(
            name_kr = F('goods__name_kr'),
        ).values(
            'id',
            'name_kr',
            'quantity',
            'total_price'
        )
        for i in checkout_detail:
            i['option_detail'] = list(CheckoutDetailOption.objects.filter(pk=i['id']).annotate(
                name_kr = F('goods_option_detail__name_kr'),
            ).values('name_kr'))

        data['checkout_detail'] = list(checkout_detail)

        return_data = {
            'data': data,
            'resultCd': '0000',
            'msg': f'checkout 상세정보',
        }

        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")