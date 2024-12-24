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

from system_manage.models import Shop, ShopPersonType, EntryQueue, EntryQueueDetail, ShopEntryOptionDetail, ShopMember, ShopTable, SmsLog
from system_manage.views.system_manage_views.auth_views import validate_phone


import traceback, json, datetime, logging, requests

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
            data['shopCategoryNameKr'] = shop.shop_category.name_kr
            data['shopCategoryNameEn'] = shop.shop_category.name_en
            data['shopNameKr'] = shop.name_kr
            data['shopNameEn'] = shop.name_en
            data['shopDescription'] = shop.description
            data['shopRepresentative'] = shop.representative
            data['shopAddress'] = shop.address
            data['shopAddressDetail'] = shop.address_detail
            data['shopZipcode'] = shop.zipcode
            
            waiting_team = EntryQueue.objects.filter(shop=shop, status='0', date=timezone.now()).count()

            data['shopEntryWaitingTeam'] = waiting_team
            data['shopEntryWaitingTime'] = waiting_team * shop.waiting_time

            if shop.image:
                data['shopImageUrl'] = settings.SITE_URL + shop.image.url
            else:
                data['shopImageUrl'] = None 
            if shop.location_image:
                data['shopLocationImageUrl'] = settings.SITE_URL + shop.location_image.url
            else:
                data['shopLocationImageUrl'] = None 
            if shop.logo_image1:
                data['shopLogoImageUrl1'] = settings.SITE_URL + shop.logo_image1.url
            else:
                data['shopLogoImageUrl1'] = None
            if shop.entry_image1:
                data['shopEntryImageUrl1'] = settings.SITE_URL + shop.entry_image1.url
            else:
                data['shopEntryImageUrl1'] = None
            
            if shop.logo_image2:
                data['shopLogoImageUrl2'] = settings.SITE_URL + shop.logo_image2.url
            else:
                data['shopLogoImageUrl2'] = None
            if shop.entry_image2:
                data['shopEntryImageUrl2'] = settings.SITE_URL + shop.entry_image2.url
            else:
                data['shopEntryImageUrl2'] = None

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
            data['shopNameKr'] = shop.name_kr
            data['shopNameEn'] = shop.name_en
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
        logger = logging.getLogger('my')
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
        
        if not peopleList:
            return_data = {'data': {},'msg': '인원수를 선택해주세요.','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        if timezone.now().weekday() < 5:
            weekday = True
        else:
            weekday = False

        if not shop.aligo_sender_key or not shop.aligo_entry_template_code1:
            return_data = {'data': {},'msg': '알림톡 설정이 안되어있습니다.','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")

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
                    status='0',
                    remark=remark
                )
                option = ''
                person_type_id_list = []
                entry_queue_detail_bulk_list = []
                for i in peopleList: 
                    shopPersonTypeId = i['id']
                    if shopPersonTypeId in person_type_id_list:
                        raise ValueError(f'{shopPersonTypeId} Person Type Id Duplicated')
                    
                    person_type_id_list.append(shopPersonTypeId)
                    quantity = int(i['quantity'])
                    if quantity > 0:
                        try:
                            shop_person_type = ShopPersonType.objects.get(pk=shopPersonTypeId, shop=shop)
                        except:
                            raise ValueError(f'{shopPersonTypeId} Person Type ID error')
                        #평일일때
                        if weekday:
                            entry_queue_detail_bulk_list.append(EntryQueueDetail(entry_queue=entry_queue, name=shop_person_type.person_type.name, goods=shop_person_type.weekday_goods, quantity=quantity))
                        else:
                            entry_queue_detail_bulk_list.append(EntryQueueDetail(entry_queue=entry_queue, name=shop_person_type.person_type.name, goods=shop_person_type.weekend_goods, quantity=quantity))
                
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
                    remark = option.strip().rstrip(',')

                entry_queue.remark = remark
                entry_queue.save()

                message = f"[{shop.name_kr}]\n\n{membername}님 웨이팅 등록되었습니다.\n\n대기번호: {order}\n등록일시: {timezone.now().strftime('%Y-%m-%d %H:%M')}\n\n입장순서는 실시간으로 확인 가능합니다."

                SmsLog.objects.create(
                    shop=shop,
                    shop_name=shop.name_kr,
                    phone=entry_queue.phone,
                    message=message,
                    message_type='2'
                )

                basic_send_url = 'https://kakaoapi.aligo.in/akv10/alimtalk/send/' # 요청을 던지는 URL, 알림톡 전송
                button_info = {'button': [
                                    {'name': '채널추가',
                                     'linkType': "AC",
                                    'linkTypeName': "채널추가"
                                    },
                                    {'name':'대기현황 확인', # 버튼명
                                        'linkType':'WL', # DS, WL, AL, BK, MD
                                        'linkTypeName' : '웹링크', # 배송조회, 웹링크, 앱링크, 봇키워드, 메시지전달 중에서 1개
                                        'linkM': f'https://root-1.net/webpos/entercheck/index.html?id={shop.pk}', # WL일 때 필수
                                    },
                                ]}
                
                button_info = json.dumps(button_info) # button의 타입은 JSON 이어야 합니다.

                sms_data={'apikey': settings.ALIGO_API_KEY, #api key
                        'userid': 'rootme', # 알리고 사이트 아이디
                        'senderkey': shop.aligo_sender_key, # 발신프로파일 키
                        'tpl_code': shop.aligo_entry_template_code1, # 템플릿 코드
                        'sender' : '07080804603', # 발신자 연락처,
                        'receiver_1': phone, # 수신자 연락처
                        'recvname_1': membername, # 수신자 이름
                        'subject_1': '대기열 등록', # 알림톡 제목 - 수신자에게는 표기X
                        'message_1': message, # 알림톡 내용 - 등록한 템플릿이랑 개행문자 포함 동일하게 입력.
                        'button_1': button_info, # 버튼 정보
                        }
                alimtalk_send_response = requests.post(basic_send_url, data=sms_data)
                alimtalk_send_response_json = alimtalk_send_response.json()
                if alimtalk_send_response_json['code'] != 0:
                    raise ValueError(f"{alimtalk_send_response_json['message']}")
                
                try:
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        f'shop_entry_{shop_id}',
                        {
                            'type': 'chat_message',
                            'message_type' : 'REGISTER',
                            'title': '대기열 등록',
                            'message': order
                        }
                    )
                except:
                    pass

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
            logger.error(traceback.format_exc())
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
        
        status = str(request.GET.get('status', '0'))
        if status not in ['0', '1', '2']:
            return_data = {'data': {},'msg': '옳바르지 않은 status','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")

        try:
            data = EntryQueue.objects.filter(shop=shop, status='0', date=timezone.now().date()).annotate(
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
                ).order_by('order')
            
            data2 = EntryQueue.objects.filter(shop=shop, date=timezone.now().date()).exclude(status='0').annotate(
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
                ).order_by('-id')

            return_data = {
                'data': list(data),
                'data2': list(data2),
                'resultCd': '0000',
                'msg': f'가맹점 대기열 리스트',
                'totalCnt' : data.count() + data2.count()
            }
        except:
            print(traceback.format_exc())
            return_data = {
                'data': [],
                'data2': [],
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
        if entry_queue.called_at:
            data['calledAt'] = entry_queue.called_at.strftime('%Y-%m-%d %H:%M')
        else:
            data['calledAt'] = None
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
        return super(ShopEntryQueueStatusView, self).dispatch(request, *args, **kwargs)
    
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
            return_data = {'data': {},'msg': '옳바르지 않은 status','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        if status == entry_queue.status:
            return_data = {'data': {},'msg': '이전 status와 일치합니다.','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        entry_queue.status = status
        entry_queue.save()

        waiting_team = EntryQueue.objects.filter(shop=entry_queue.shop, status='0', date=timezone.now()).count()
        waiting_time = waiting_team * entry_queue.shop.waiting_time
        
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'shop_entry_{shop_id}',
                {
                    'type': 'chat_message',
                    'message_type' : 'STATUS',
                    'title': '대기 현황',
                    'message': {'waiting_team':waiting_team, 'waiting_time':waiting_time}
                }
            )
        except:
            pass

        return_data = {'data': {},'msg': '상태가 변경되었습니다.','resultCd': '0000'}
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")
    

class ShopEntryCallView(View):
    '''
        shop 대기 호출
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ShopEntryCallView, self).dispatch(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        logger = logging.getLogger('my')
        shop_id = kwargs.get('shop_id')
        pk = kwargs.get('pk')
        try:
            entry_queue = EntryQueue.objects.get(pk=pk, shop_id=shop_id)
        except:
            return_data = {'data': {},'msg': '데이터 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        

        if not entry_queue.shop.aligo_sender_key or not entry_queue.shop.aligo_entry_template_code2:
            return_data = {'data': {},'msg': '알림톡 설정이 안되어있습니다.','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        try:
            with transaction.atomic():
                message = f"[{entry_queue.shop.name_kr}]\n\n기다려 주셔서 감사합니다.{entry_queue.membername}님 차례가 되었습니다.\n\n직원에게 해당 알림톡을 보여주시면 웨이팅 번호 순서대로 안내해 드리겠습니다."        
                SmsLog.objects.create(
                    shop=entry_queue.shop,
                    shop_name=entry_queue.shop.name_kr,
                    phone=entry_queue.phone,
                    message=message,
                    message_type='2'
                )
                
                entry_queue.called_at = timezone.now()
                entry_queue.save()

                basic_send_url = 'https://kakaoapi.aligo.in/akv10/alimtalk/send/' # 요청을 던지는 URL, 알림톡 전송
                button_info = {'button': [
                                    {
                                        'name': '채널추가',
                                        'linkType': "AC",
                                        'linkTypeName': "채널추가"
                                    }
                                ]}
                
                button_info = json.dumps(button_info) # button의 타입은 JSON 이어야 합니다.
                sms_data={'apikey': settings.ALIGO_API_KEY, #api key
                        'userid': 'rootme', # 알리고 사이트 아이디
                        'senderkey': entry_queue.shop.aligo_sender_key, # 발신프로파일 키
                        'tpl_code': entry_queue.shop.aligo_entry_template_code2, # 템플릿 코드
                        'sender' : '07080804603', # 발신자 연락처,
                        'receiver_1': entry_queue.phone, # 수신자 연락처
                        'recvname_1': entry_queue.membername, # 수신자 이름
                        'subject_1': '입장 안내', # 알림톡 제목 - 수신자에게는 표기X
                        'message_1': message, # 알림톡 내용 - 등록한 템플릿이랑 개행문자 포함 동일하게 입력.
                        'button_1': button_info, # 버튼 정보
                        }
                alimtalk_send_response = requests.post(basic_send_url, data=sms_data)
                alimtalk_send_response_json = alimtalk_send_response.json()
                logger.error(alimtalk_send_response_json)
                if alimtalk_send_response_json['code'] != 0:
                    raise ValueError(f"{alimtalk_send_response_json['message']}")
        
        except ValueError as e:
            return_data = {'data': {},'msg': str(e),'resultCd': '0001',}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        except:
            return_data = {'data': {},'msg': traceback.format_exc(),'resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")

        # try:
        #     channel_layer = get_channel_layer()
        #     async_to_sync(channel_layer.group_send)(
        #         f'shop_entry_{shop_id}',
        #         {
        #             'type': 'chat_message',
        #             'message_type' : 'CALL',
        #             'title': '입장 안내',
        #             'message': entry_queue.order
        #         }
        #     )
        # except:
        #     return_data = {'data': {},'msg': '호출 오류','resultCd': '0001'}
        #     return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        #     return HttpResponse(return_data, content_type = "application/json")
        

        return_data = {'data': {},'msg': '호출완료','resultCd': '0000'}
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")
    
    
class ShopEntryPaymentView(View):
    '''
        shop
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ShopEntryPaymentView, self).dispatch(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        pk = kwargs.get('pk')
        try:
            entry_queue = EntryQueue.objects.get(pk=pk, shop_id=shop_id)
        except:
            return_data = {'data': {},'msg': '데이터 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        mainpos_id = int(request.POST['mainpos_id'])
        cart_list = []
        total_price = 0
        entry_queue_detail = entry_queue.entry_queue_detail.all()
        for i in entry_queue_detail:
            data = {}
            if i.goods:
                data['goodsId'] = i.goods.pk
                data['name_kr'] = i.goods.name_kr
                data['price'] = i.goods.price
                data['discount'] = 0
                data['quantity'] = i.quantity
                data['optionName'] = ''
                data['optionPrice'] = 0
                data['optionList'] = []
                total_price += i.quantity * i.goods.price
                cart_list.append(data)

        if not cart_list:
            return_data = {'data': {},'msg': '입장결제 상품이 연결되어있지 않습니다.','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        try:
            shop_table = ShopTable.objects.get(table_no=mainpos_id, shop_id=shop_id)
        except:
            return_data = {'data': {},'msg': '테이블 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        cart_list = json.dumps(cart_list, ensure_ascii=False)
        shop_table.cart = cart_list
        shop_table.total_price = total_price
        shop_table.total_additional = 0
        shop_table.total_discount = 0
        shop_table.shop_member = entry_queue.shop_member
        shop_table.save()
        
        return_data = {'data': {},'msg': '메인 포스 테이블에 상품이 담겼습니다.','resultCd': '0000'}
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")