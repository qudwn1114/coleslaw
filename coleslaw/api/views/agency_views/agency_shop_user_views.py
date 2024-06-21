from django.conf import settings
from django.views.generic import View
from django.urls import reverse
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.db.models.functions import Concat
from django.db.models import CharField, F, Value as V, Func, Case, When, Prefetch
from django.core.serializers.json import DjangoJSONEncoder

from system_manage.models import Agency, Order

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
                shopName = F('shop__name'),
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
                'shopName',
                'shopImageUrl',
                'final_price',
                'order_name',
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
            order = Order.objects.get(pk=order_id, agency=agency, order_membername=membername, order_phone=phone)
            data = {}
            if order.shop.image:
                data['orderShopImageUrl'] = settings.SITE_URL + order.shop.image.url
            else:
                data['orderShopImageUrl'] = None

            data['shopName'] = order.shop.name
            data['final_price'] = order.final_price
            data['order_name'] = order.order_name
            data['order_code'] = order.order_code
            data['order_no'] = order.order_no
            data['status'] = order.status
            data['created_at'] = order.created_at

            order_goods = order.order_goods.all().values( 
                'name',
                'price',
                'option',
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
    