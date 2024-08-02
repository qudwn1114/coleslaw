from django.views.generic import View
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.db.models import CharField, F, Value as V, Func, Case, When, Prefetch, Sum
from django.db import transaction, IntegrityError
from django.core.serializers.json import DjangoJSONEncoder
from system_manage.views.system_manage_views.auth_views import validate_phone
from django.utils import timezone, dateformat
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from system_manage.models import OrderPayment, Shop

import json


class ShopOrderReceiptView(View):
    '''
        shop pos 영수증 api
    '''
    def get(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        order_payment_id = int(kwargs.get('order_payment_id'))
        try:
            shop = Shop.objects.get(pk=shop_id)
        except:
            return_data = {'data': {},'msg': 'shop id 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")

        try:
            order_payment = OrderPayment.objects.get(pk=order_payment_id, order__shop=shop)
        except:
            return_data = {'data': {},'msg': '결제정보 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        data = {}
        data['agencyName'] = shop.agency.name
        data['shopName'] = shop.name_kr
        data['shopDescription'] = shop.description
        data['shopRepresentative'] = shop.representative
        data['shopPhone'] = shop.phone
        data['shopAddress'] = shop.address
        data['shopAddressDetail'] = shop.address_detail
        data['shopZipcode'] = shop.zipcode

        data['tid'] = order_payment.tid
        data['installment'] = order_payment.installment
        data['tranDate'] = order_payment.tranDate
        data['tranTime'] = order_payment.tranTime
        data['amount'] = order_payment.amount
        data['taxAmount'] = order_payment.taxAmount
        data['cardNo'] = order_payment.cardNo
        data['issueCompanyName'] = order_payment.issueCompanyName
        data['cardNo'] = order_payment.cardNo

        
        return_data = {
            'data': data,
            'resultCd': '0000',
            'msg': 'tid 정보',
        }
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")