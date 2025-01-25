from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import View
from django.http import HttpRequest, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
from django.utils.decorators import method_decorator
from django.db.models import CharField, F, Value as V, Func, Case, When, Q
from django.utils import timezone

from system_manage.decorators import permission_required
from system_manage.models import Order, OrderPayment, Agency, Shop
from system_manage.utils import ResponseToXlsx

import datetime

class OrderManageView(View):
    '''
        주문 조회
    '''
    @method_decorator(permission_required(redirect_url='system_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}

        context['agency'] = Agency.objects.all().order_by('name').values('id', 'name')
        context['shop'] = Shop.objects.all().order_by('name_kr').values('id', 'name_kr')

        paginate_by = '20'
        page = request.GET.get('page', '1')
        search_type = request.GET.get('search_type', '')
        search_keyword = request.GET.get('search_keyword', '')

        agency_id = request.GET.get('agency_id', '')
        shop_id = request.GET.get('shop_id', '')

        order_date_no = request.GET.get('order_date_no', None) 

        filter_dict = {}        
        if order_date_no:
            dates = request.GET.get('dates', '')
            context['dates'] = dates
            if dates != '':
                startDate = dates.split(' - ')[0].strip()
                endDate = dates.split(' - ')[1].strip()
                format = '%m/%d/%Y'

                startDate = datetime.datetime.strptime(startDate, format)
                endDate = datetime.datetime.strptime(endDate, format)
                endDate = datetime.datetime.combine(endDate, datetime.time.max)
                filter_dict['created_at__lte'] = endDate
                filter_dict['created_at__gte'] = startDate
        else:
            order_date_no = '1'
            today = timezone.now().strftime("%m/%d/%Y")
            context['dates'] = f"{today} - {today}"
            filter_dict['date'] = timezone.now().date()

        context['order_date_no'] = order_date_no
        
        order_type_list = request.GET.getlist('order_type', None)
        if order_type_list:
            order_type_list = list(map(int, order_type_list))
            filter_dict['order_type__in'] = order_type_list
            context['order_type_list'] = order_type_list
        else:
            context['order_type_list'] = [0, 1, 2]

        if agency_id:
            agency_id = int(agency_id)
            filter_dict['agency_id'] = agency_id
            context['agency_id'] = agency_id
        if shop_id:
            shop_id = int(shop_id)
            filter_dict['shop_id'] = shop_id
            context['shop_id'] = shop_id

        if search_keyword:
            context['search_type'] = search_type
            context['search_keyword'] = search_keyword
            filter_dict[search_type] = search_keyword

        obj_list = Order.objects.annotate(
            orderType = Case(
                When(order_type='0', then=V('POS')),
                When(Q(order_type='1'), then=V('QR')),
                When(Q(order_type='2'), then=V('KIOSK'))
            ),
            orderStatus=Case(
                    When(status='0', then=V('결제대기')),
                    When(status='1', then=V('결제완료')),
                    When(status='2', then=V('취소')),
                    When(status='3', then=V('준비중')),
                    When(status='4', then=V('주문완료')),
                    When(status='5', then=V('수령완료')),
                    When(status='6', then=V('부분취소'))
            ),
            paymentMethod = Case(
                When(payment_method='0', then=V('카드결제')),
                When(payment_method='1', then=V('현금결제')),
                When(payment_method='2', then=V('분할결제'))
            ),
        ).filter(**filter_dict).values(
            'id',
            'shop__name_kr',
            'order_name_kr',
            'order_no',
            'final_price',
            'payment_price',
            'created_at',
            'paymentMethod',
            'status',
            'orderStatus',
            'orderType'
        ).order_by('-id')

        paginator = Paginator(obj_list, paginate_by)
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page = 1
            page_obj = paginator.page(page)
        except EmptyPage:
            page = 1
            page_obj = paginator.page(page)
        except InvalidPage:
            page = 1
            page_obj = paginator.page(page)

        pagelist = paginator.get_elided_page_range(page, on_each_side=3, on_ends=1)
        context['pagelist'] = pagelist
        context['page_obj'] = page_obj

        return render(request, 'admin_order_manage/order_manage.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def post(self, request: HttpRequest, *args, **kwargs):
        if not request.META.get('REMOTE_ADDR') in ['127.0.0.1', 'localhost']:
            return JsonResponse({'message': '해당 요청은 로컬에서만 작업가능합니다.'}, status=400)
        id = request.POST['id']
        try:
            order = Order.objects.get(pk=id)
        except:
            return JsonResponse({'message': '주문정보가 존재하지 않습니다.'}, status=400)
        if order.status != '0':
            return JsonResponse({'message': '대기 상태일때만 가능합니다.'}, status=400)
        OrderPayment.objects.create(
            order=order
        )
        return JsonResponse({'message' : '빈 결제정보 등록 되었습니다.'},  status = 202)

class OrderPaymentManageView(View):
    '''
        주문 결제 조회
    '''
    @method_decorator(permission_required(redirect_url='system_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}

        context['agency'] = Agency.objects.all().order_by('name').values('id', 'name')
        context['shop'] = Shop.objects.all().order_by('name_kr').values('id', 'name_kr')

        paginate_by = '20'
        page = request.GET.get('page', '1')
        search_type = request.GET.get('search_type', '')
        search_keyword = request.GET.get('search_keyword', '')

        agency_id = request.GET.get('agency_id', '')
        shop_id = request.GET.get('shop_id', '')

        order_type_list = request.GET.getlist('order_type', None)
        payment_method_list = request.GET.getlist('payment_method', None)

        order_date_no = request.GET.get('order_date_no', None) 

        q = Q()
        if order_date_no:
            dates = request.GET.get('dates', '')
            context['dates'] = dates
            if dates != '':
                startDate = dates.split(' - ')[0].strip()
                endDate = dates.split(' - ')[1].strip()
                format = '%m/%d/%Y'

                startDate = datetime.datetime.strptime(startDate, format)
                endDate = datetime.datetime.strptime(endDate, format)
                endDate = datetime.datetime.combine(endDate, datetime.time.max)
                q.add(Q(created_at__lte=endDate), q.AND)
                q.add(Q(created_at__gte=startDate), q.AND)
        else:
            order_date_no = '1'
            today = timezone.now().strftime("%m/%d/%Y")
            dates = f"{today} - {today}"
            context['dates'] = dates
            q.add(Q(order__date=timezone.now().date()), q.AND)
        context['order_date_no'] = order_date_no
        
        if order_type_list:
            order_type_list = list(map(int, order_type_list))
            q.add(Q(order__order_type__in=order_type_list), q.AND)
            context['order_type_list'] = order_type_list
        else:
            context['order_type_list'] = [0, 1, 2]
        
        if payment_method_list:
            q.add(Q(payment_method__in=payment_method_list), q.AND)
            context['payment_method_list'] = payment_method_list
        else:
            context['payment_method_list'] = ['0', '1']

        if agency_id:
            agency_id = int(agency_id)
            q.add(Q(order__agency_id=agency_id), q.AND)
            context['agency_id'] = agency_id
        if shop_id:
            shop_id = int(shop_id)
            q.add(Q(order__shop_id=shop_id), q.AND)
            context['shop_id'] = shop_id

        if search_keyword:
            filter_dict = {}
            context['search_type'] = search_type
            context['search_keyword'] = search_keyword
            if search_type == 'approval_no':
                q.add(Q(applNo=search_keyword)|Q(approvalNumber=search_keyword), q.AND)
            else:
                filter_dict[search_type] = search_keyword
                q.add(Q(**filter_dict), q.AND)

        obj_list = OrderPayment.objects.annotate(
            orderType = Case(
                When(order__order_type='0', then=V('POS')),
                When(Q(order__order_type='1'), then=V('QR')),
                When(Q(order__order_type='2'), then=V('KIOSK'))
            ),
            paymentStatus = Case(
                When(status=True, then=V('승인')),
                When(status=False, then=V('취소')),
            ),
            paymentMethod = Case(
                When(payment_method='0', then=V('카드')),
                When(Q(payment_method='1'), then=V('현금'))
            ),
            final = Case(
                When(cancelled_at=None, then=F('amount')),
                default=V(0)
            )
        ).filter(q).values(
            'id',
            'order__shop__name_kr',
            'order__order_no',
            'amount',
            'cardNo',
            'applNo',
            'approvalNumber',
            'issueCompanyName',
            'issueCardName',
            'tranDate',
            'tranTime',
            'cancelled_at',
            'orderType',
            'paymentStatus',
            'paymentMethod',
            'final'
        ).order_by('-id')

        excel = request.GET.get('excel', None)
        if excel:
            filename = f"결제내역_{timezone.now().strftime('%Y%m%d%H%M%S')}"
            columns = ['ID', '가맹점', '주문번호', '결제금액', '카드번호', '승인번호(QR)', '승인번호(POS)', '발급사명', '발급사카드명', '승인날짜', '승인시간', '취소날짜', '주문방식', '상태', '결제수단', '최종']
            xlsx_download = ResponseToXlsx(columns=columns, queryset=obj_list)
            return xlsx_download.download(filename=filename)

        paginator = Paginator(obj_list, paginate_by)
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page = 1
            page_obj = paginator.page(page)
        except EmptyPage:
            page = 1
            page_obj = paginator.page(page)
        except InvalidPage:
            page = 1
            page_obj = paginator.page(page)

        pagelist = paginator.get_elided_page_range(page, on_each_side=3, on_ends=1)
        context['pagelist'] = pagelist
        context['page_obj'] = page_obj

        return render(request, 'admin_order_manage/order_payment_manage.html', context)