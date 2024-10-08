from django.conf import settings
from django.views.generic import View
from django.urls import reverse
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.db.models.functions import Concat
from django.db.models import CharField, F, Value as V, Func, Case, When, Prefetch
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from system_manage.models import Agency, Order, Shop, OrderPayment

import traceback, json, datetime

class AgencyShopUserOrderListView(View):
    '''
        agency shop user order list api
    '''
    def get(self, request: HttpRequest, *args, **kwargs):
        agency_id = kwargs.get('agency_id')
        membername = request.GET['membername']
        phone = request.GET['phone']
        try:
            agency = Agency.objects.get(pk=agency_id)
            queryset = Order.objects.filter(agency=agency, order_membername=membername, order_phone=phone).exclude(status='0').annotate(
                shopNameKr = F('shop__name_kr'),
                shopNameEn = F('shop__name_en'),
                shopImageUrl=Case(
                    When(shop__image='', then=None),
                    When(shop__image=None, then=None),
                    default=Concat(V(settings.SITE_URL), V(settings.MEDIA_URL), 'shop__image', output_field=CharField())
                ),
                createdAt=Func(
                    F('created_at'),
                    V('%y.%m.%d %H:%i'),
                    function='DATE_FORMAT',
                    output_field=CharField()
                )
            ).values(
                'id',
                'shopNameKr',
                'shopNameEn',
                'shopImageUrl',
                'final_price',
                'order_name_kr',
                'order_name_en',
                'status',
                'createdAt'
            ).order_by('-id')
            return_data = {
                'data': list(queryset),
                'resultCd': '0000',
                'msg': '사용자 주문내역',
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
    

class AgencyShopUserOrderDetailView(View):
    '''
        agency shop user order detail api
    '''
    def get(self, request: HttpRequest, *args, **kwargs):
        agency_id = kwargs.get('agency_id')
        order_id = kwargs.get('order_id')
        membername = request.GET['membername']
        phone = request.GET['phone']
        try:
            agency = Agency.objects.get(pk=agency_id)
            order = Order.objects.get(pk=order_id, agency=agency, order_type='1', order_membername=membername, order_phone=phone)
            order_payment = OrderPayment.objects.get(order=order)
            data = {}
            if order.shop.image:
                data['orderShopImageUrl'] = settings.SITE_URL + order.shop.image.url
            else:
                data['orderShopImageUrl'] = None

            data['shop_id'] = order.shop.pk
            data['shopNameKr'] = order.shop.name_kr
            data['shopNameEn'] = order.shop.name_en
            data['final_price'] = order.final_price
            data['order_name_kr'] = order.order_name_kr
            data['order_name_en'] = order.order_name_en
            data['order_code'] = order.order_code
            data['order_no'] = order.order_no
            data['status'] = order.status

            if order_payment.payType in ['I', 'V', 'K']:
                data['order_payment_type'] = '신용카드'
            elif order_payment.payType == 'A':
                data['order_payment_type'] = '카카오페이'
            elif order_payment.payType == 'P':
                data['order_payment_type'] = '페이코'
            elif order_payment.payType == 'N1':
                data['order_payment_type'] = '네이버페이'
            elif order_payment.payType == 'N2':
                data['order_payment_type'] = '네이버페이포인트'
            elif order_payment.payType == 'U':
                data['order_payment_type'] = '유니온페이'
            else:
                data['order_payment_type'] = '신용카드'
            data['createdAt'] = order.created_at.strftime('%Y년 %m월 %d일 %H:%M')

            data['mbrNo'] = order_payment.mbrNo
            data['mbrRefNo'] = order_payment.mbrRefNo
            data['refNo'] = order_payment.refNo
            data['tranDate'] = order_payment.tranDate
            data['payType'] = order_payment.payType
            data['paymethod'] = order.payment_method
            data['amount'] = order_payment.amount

            order_goods = order.order_goods.all().values( 
                'name_kr',
                'name_en',
                'price',
                'option_kr',
                'option_en',
                'option_price',
                'quantity',
                'total_price'
            ).order_by('id')
            data['order_goods'] = list(order_goods)

            return_data = {
                'data': data,
                'resultCd': '0000',
                'msg': '사용자 주문상세',
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

class ShopOrderCancelView(View):
    '''
        사용자 주문 취소
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ShopOrderCancelView, self).dispatch(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        order_id = kwargs.get('order_id')
        try:
            shop = Shop.objects.get(pk=shop_id)
        except:
            return_data = {
                'data': {},
                'msg': 'shop id 오류',
                'resultCd': '0001',
            }
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")

        try:
            order = Order.objects.get(pk=order_id, shop=shop)
            order_payment = OrderPayment.objects.get(order=order)
        except:
            return_data = {
                'data': {},
                'msg': 'order 오류',
                'resultCd': '0001',
            }
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        order.status = '2'
        order.save()
        
        order_payment.status = False
        order_payment.cancelled_at = timezone.now()
        order_payment.save()

        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'shop_order_{shop_id}',
                {
                    'type': 'chat_message',
                    'message_type' : 'CANCEL',
                    'title': '! 주문취소 ! ',
                    'message': f'[{order.order_no}] {order.order_name_kr}'
                }
            )
        except:
            pass
        
        # 재고 롤백
        try:
            for i in order.order_goods.all():
                if i.goods.stock_flag:
                    g = i.goods
                    g.stock += i.quantity
                    g.save()
                for j in i.order_goods_option.all():
                    if j.goods_option_detail.stock_flag:
                        god = j.goods_option_detail
                        god.stock += i.quantity
                        god.save()
        except:
            pass


        return_data = {
            'data': {},
            'msg': '취소 상태변경 완료',
            'resultCd': '0000',
        }
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")