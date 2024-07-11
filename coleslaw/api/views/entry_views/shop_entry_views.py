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

from system_manage.models import Shop, ShopPersonType, EntryQueue, EntryQueueDetail, ShopEntryOptionDetail, ShopMember
from system_manage.views.system_manage_views.auth_views import validate_phone


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
        입장 정보 입력 관련 api
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


class ShopEntryQueueCreateView(View):
    '''
        shop 대기열 생성
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ShopEntryQueueCreateView, self).dispatch(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        try:
            shop = Shop.objects.get(pk=shop_id)
        except:
            return_data = {'data': {},'msg': 'shop id 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        membername = request.POST['membername'].strip()
        phone = request.POST['phone']
        email = request.POST['email']
        car_plate_no = request.POST['car_plate_no']

        if not validate_phone(phone):
            return_data = {'data': {},'msg': '유효하지 않은 전화번호 형식입니다.','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")


        peopleList = request.POST['peopleList']
        peopleList = json.loads(peopleList)

        optionList = request.POST['optionList']
        optionList = json.loads(optionList)

        try:
            with transaction.atomic():
                shop_member, created = ShopMember.objects.get_or_create(
                    shop=shop, phone=phone,
                    defaults={ 'membername' : membername }
                )
                if not created:
                    shop_member.membername = membername
                    shop_member.save()

                order = EntryQueue.objects.filter(shop=shop, date=timezone.now().date()).count() + 1
                remark = ''
                entry_queue = EntryQueue.objects.create(
                    shop=shop,
                    shop_member=shop_member,
                    order=order,
                    membername=membername,
                    phone=phone,
                    car_plate_no=car_plate_no,
                    email=email,
                    remark=remark
                )
                option = ''
                entry_queue_detail_bulk_list = []
                for i in peopleList: 
                    shopPersonTypeId = i['id']
                    quantity = int(i['quantity'])
                    if quantity > 0:
                        try:
                            shop_person_type = ShopPersonType.objects.get(pk=shopPersonTypeId, shop=shop)
                        except:
                            raise ValueError(f'{shopPersonTypeId} Person Type ID error')
                        if shop_person_type.goods:
                            entry_queue_detail_bulk_list.append(EntryQueueDetail(entry_queue=entry_queue, name=shop_person_type.person_type.name, goods=shop_person_type.goods, quantity=quantity))
                
                if entry_queue_detail_bulk_list:
                    EntryQueueDetail.objects.bulk_create(entry_queue_detail_bulk_list)
                
                for i in optionList: 
                    shopEntryOptionId = i['id']
                    shopEntryOptionDetailId = i['detailId']
                    try:
                        shop_entry_option_detail = ShopEntryOptionDetail.objects.get(pk=shopEntryOptionDetailId, shop_entry_option_id=shopEntryOptionId)
                    except:
                        raise ValueError(f'Option error')
                    option += f'{shop_entry_option_detail.shop_entry_option.name}:{shop_entry_option_detail.name}, '
                
                if option:
                    remark = remark.strip().rstrip(',')
                    remark += f'{option}'

                entry_queue.remark = remark
                entry_queue.save()

                return_data = {
                    'data': {
                        'shop_id':shop.pk,
                        'order':entry_queue.order,
                    },
                    'msg': '대기열 등록완료',
                    'resultCd': '0000',
                }
        
        except ValueError as e:
            return_data = {
                'data': {},
                'msg': str(e),
                'resultCd': '0001',
            }
        except IntegrityError:
            return_data = {
                'data': {},
                'msg': '다시 시도해주세요.',
                'resultCd': '0001',
            }
        except:
            return_data = {'data': {},'msg': traceback.format_exc(),'resultCd': '0001'}
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")
    

class ShopEntryQueueListView(View):
    '''
        shop entry queue list api
    '''
    def get(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        try:
            shop = Shop.objects.get(pk=shop_id)
        except:
            return_data = {'data': {},'msg': 'shop id 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        try:
            page = int(request.GET.get('page', 1))
            startnum = 0 + (page-1)*10
            endnum = startnum+10
            queryset = EntryQueue.objects.filter(shop=shop).annotate(
                    createdAt=Func(
                        F('created_at'),
                        V('%y.%m.%d %H:%i'),
                        function='DATE_FORMAT',
                        output_field=CharField()
                    )
                ).values(
                    'id',
                    'membername',
                    'phone',
                    'status',
                    'order',
                    'date',
                    'createdAt',
                ).order_by('-id', '-order')

            return_data = {
                'data': list(queryset[startnum:endnum]),
                'resultCd': '0000',
                'msg': '가맹점 대기열 리스트',
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


class ShopEntryQueueDetailView(View):
    '''
        shop entry queue detail api
    '''
    def get(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        pk = kwargs.get('pk')
        try:
            entry_queue = EntryQueue.objects.get(pk=pk, shop_id=shop_id)
        except:
            return_data = {'data': {},'msg': '데이터 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        data = {}
        data['id'] = entry_queue.pk
        data['membername'] = entry_queue.membername
        data['phone'] = entry_queue.phone
        data['email'] = entry_queue.email
        data['car_plate_no'] = entry_queue.car_plate_no
        data['order'] = entry_queue.order
        entry_queue_detail = EntryQueueDetail.objects.filter(entry_queue=entry_queue).values(
            'name',
            'quantity'
        ).order_by('id')
        data['entry_queue_detail'] = list(entry_queue_detail)
        data['remark'] = entry_queue.remark
        data['createdAt'] = entry_queue.created_at.strftime('%Y-%m-%d %H:%M')

        return_data = {
            'data': data,
            'resultCd': '0000',
            'msg': '가맹점 대기열 상세',
        }

        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")


class ShopEntryQueueStatusView(View):
    '''
        shop 대기열 상태 변경
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ShopEntryQueueCreateView, self).dispatch(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        pk = kwargs.get('pk')
        try:
            entry_queue = EntryQueue.objects.get(pk=pk, shop_id=shop_id)
        except:
            return_data = {'data': {},'msg': '데이터 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        status = str(request.POST['status'])

        if status not in ['0', '1', '2']:
            return_data = {'data': {},'msg': '옳바르지 않은 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        entry_queue.status = status
        entry_queue.save()

        return_data = {'data': {},'msg': '상태가 변경되었습니다.','resultCd': '0000'}
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")