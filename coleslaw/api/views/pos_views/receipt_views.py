from django.views.generic import View
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.db.models import CharField, F, Value as V, Func, Case, When, Prefetch, Sum
from django.db.models.functions import Coalesce
from django.core.serializers.json import DjangoJSONEncoder
from system_manage.views.system_manage_views.auth_views import validate_phone
from django.utils import timezone, dateformat
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from system_manage.models import OrderPayment, Shop, OrderGoods

import json, datetime


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
        data['shopReceiptFlag'] = shop.shop_receipt_flag
        data['shopName'] = shop.name_kr
        data['shopDescription'] = shop.description
        data['shopRepresentative'] = shop.representative
        data['shopRegistrationNo'] = shop.registration_no
        data['shopPhone'] = shop.phone
        data['shopAddress'] = shop.address
        data['shopAddressDetail'] = shop.address_detail
        data['shopZipcode'] = shop.zipcode
        data['shopReceipt'] = shop.receipt
        data['printerPort1'] = shop.printer_port1
        data['printerPort2'] = shop.printer_port2
        
        data['table_no'] = order_payment.order.table_no
        data['order_no'] = order_payment.order.order_no
        data['tid'] = order_payment.tid
        data['installment'] = order_payment.installment
        data['tranDate'] = order_payment.tranDate
        if order_payment.tranTime:
            tranTime = order_payment.tranTime[:2] + ":" + order_payment.tranTime[2:]
        else:
            tranTime = ''
        data['tranTime'] = tranTime
        data['amount'] = order_payment.amount # 결제금액
        data['taxAmount'] = order_payment.taxAmount # 결제금액 부가세
        data['cardNo'] = order_payment.cardNo
        data['issueCompanyName'] = order_payment.issueCompanyName
        data['cardNo'] = order_payment.cardNo
        data['approvalNumber'] = order_payment.approvalNumber
        if order_payment.cancelled_at:
            data['cancelledAt'] = order_payment.cancelled_at.strftime('%Y-%m-%d %H:%M')
        else:
            data['cancelledAt'] = None

        data['orderFinalDiscount'] = order_payment.order.final_discount # 총할인
        data['orderFinalAdditional'] = order_payment.order.final_additional # 총추가금액
        data['orderFinalPrice'] = order_payment.order.final_price # 합계
        data['orderFianlTaxPrice'] = round(order_payment.order.final_price/1.1*0.1) # 합계부가세

        order_detail = order_payment.order.order_goods.all().values(
            'id',
            'name_kr',
            'price',
            'option_kr',
            'option_price',
            'quantity',
            'total_price'
        )        
        data['order_detail'] = list(order_detail)
        
        return_data = {
            'data': data,
            'resultCd': '0000',
            'msg': 'receipt 정보',
        }
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")
    

class ShopCloseReceiptView(View):
    '''
        shop pos 마감 영수증 api
    '''
    def get(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        try:
            shop = Shop.objects.get(pk=shop_id)
        except:
            return_data = {'data': {},'msg': 'shop id 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")

        start_date = request.GET.get('start_date', '')
        end_date = request.GET.get('end_date', '')

        filter_dict = {}
        if start_date and end_date:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
            end_date = datetime.datetime.combine(end_date, datetime.time.max)
        else:
            start_date = timezone.now().date()
            end_date = datetime.datetime.combine(start_date, datetime.time.max)

        if start_date.strftime('%Y-%m-%d') == end_date.strftime('%Y-%m-%d'):
            date = f"{start_date.strftime('%Y-%m-%d')}"
        else:
            date = f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}"
        filter_dict['order__created_at__gte'] = start_date
        filter_dict['order__created_at__lte'] = end_date

        status_list = ['1', '3', '4', '5']
        filter_dict['order__status__in'] = status_list
        filter_dict['order__shop'] = shop

        order_goods = OrderGoods.objects.filter(**filter_dict).annotate(
            sale_total_price=F('sale_price') + F('sale_option_price')
            ).values(
                "name_kr", 
                "option_kr", 
                "sale_price", 
                "sale_option_price", 
                "sale_total_price"
            ).annotate(total_quantity=Sum("quantity")).order_by('name_kr', '-total_quantity')

        data = {}
        data['agencyName'] = shop.agency.name
        data['shopName'] = shop.name_kr
        data['shopDescription'] = shop.description
        data['shopRepresentative'] = shop.representative
        data['shopRegistrationNo'] = shop.registration_no
        data['shopPhone'] = shop.phone
        data['shopAddress'] = shop.address
        data['shopAddressDetail'] = shop.address_detail
        data['shopZipcode'] = shop.zipcode
        data['shopReceipt'] = shop.receipt
        data['printerPort1'] = shop.printer_port1
        data['printerPort2'] = shop.printer_port2
        data['date'] = date
        
        data['order_goods_list'] = list(order_goods)

        payment_filter_dict = {}
        payment_filter_dict['order__created_at__gte'] = start_date
        payment_filter_dict['order__created_at__lte'] = end_date
        payment_filter_dict['order__shop'] = shop
        payment_filter_dict['status'] = True
    

        order_payment = OrderPayment.objects.filter(**payment_filter_dict)
        
        card_total_amount = order_payment.filter(payment_method='0').aggregate(sum=Coalesce(Sum('amount'), 0)).get('sum')
        card_total_tax_amount = round(card_total_amount/1.1*0.1)
        
        cash_total_amount = order_payment.filter(payment_method='1').aggregate(sum=Coalesce(Sum('amount'), 0)).get('sum')
        cash_total_tax_amount = order_payment.filter(payment_method='1').aggregate(sum=Coalesce(Sum('taxAmount'), 0)).get('sum')

        data['card_total_amount'] = card_total_amount
        data['card_total_tax_amount'] = card_total_tax_amount
        data['cash_total_amount'] = cash_total_amount
        data['cash_total_tax_amount'] = cash_total_tax_amount
        
        return_data = {
            'data': data,
            'resultCd': '0000',
            'msg': f'{shop.name_kr} {date} 마감 영수증 정보',
        }
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")