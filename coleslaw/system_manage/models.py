from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class PersonType(models.Model):
    name = models.CharField(max_length=100, verbose_name='사람타입', unique=True)
    image = models.ImageField(max_length=300, null=True, upload_to="image/person_type/", verbose_name='사람이미지')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta :
        db_table = 'person_type'

# 에이전시
class Agency(models.Model):
    name = models.CharField(max_length=100, verbose_name='agency이름', unique=True)
    description = models.CharField(default='', max_length=255, verbose_name='설명')
    image = models.ImageField(max_length=300, null=True, upload_to="image/agency/", verbose_name='에이전시이미지')
    status = models.BooleanField(default=True, verbose_name='상태')
    qr_link = models.CharField(max_length=300, null=True, verbose_name='qr주문 링크')
    qr_order_note = models.TextField(default='', null=True)
    qr_order_message = models.CharField(max_length=200, default='', verbose_name='qr주문 문자안내')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta : 
        db_table = 'agency'

# 에이전시관리자
class AgencyAdmin(models.Model):
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='agency_admin')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')

    class Meta : 
        constraints = [
            models.UniqueConstraint(fields=['agency', 'user'], name='agency_user_unique')
        ]
        db_table = 'agency_admin'

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    membername = models.CharField(default='', max_length=50, verbose_name='회원명')
    phone = models.CharField(default='', max_length=30, verbose_name='전화번호')
    gender = models.CharField(default='M', max_length=10, verbose_name='성별') # M / F
    birth = models.DateField(default='1990-01-01', verbose_name='생년월일')

    zipcode = models.CharField(default='', max_length=10, verbose_name='우편번호')
    address = models.CharField(default='', max_length=255, verbose_name='주소')
    address_detail = models.CharField(default='', max_length=255, verbose_name='상세주소')

    withdrawal_at = models.DateTimeField(null=True, verbose_name='탈퇴일')

    agency = models.ForeignKey(Agency, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table='auth_profile'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

# 가맹점 카테고리
class ShopCategory(models.Model):
    name_kr = models.CharField(max_length=100, verbose_name='가맹점카테고리한글이름', unique=True)
    name_en = models.CharField(max_length=100, verbose_name='가맹점카테고리영문이름', unique=True)
    description = models.CharField(default='', max_length=255, verbose_name='설명')
    image = models.ImageField(max_length=300, null=True, upload_to="image/shop_category/", verbose_name='가맹점카테고리이미지')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta : 
        db_table = 'shop_category'

class Pos(models.Model):
    name = models.CharField(max_length=50, verbose_name='포스업체명')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    class Meta :
        db_table = 'pos'


# 가맹점
class Shop(models.Model):
    agency = models.ForeignKey(Agency, on_delete=models.PROTECT, related_name='shop', verbose_name='메인 agency')
    shop_category = models.ForeignKey(ShopCategory, on_delete=models.PROTECT, related_name='shop')
    name_kr = models.CharField(max_length=100, verbose_name='가맹점한글명', unique=True)
    name_en = models.CharField(max_length=100, verbose_name='가맹점영문명', unique=True)
    description = models.CharField(default='', max_length=255, verbose_name='설명')
    
    phone = models.CharField(null=True, max_length=20, verbose_name='가맹점연락처')
    representative = models.CharField(null=True, max_length=20, verbose_name='대표자이름')

    zipcode = models.CharField(default='', max_length=10, verbose_name='우편번호')
    address = models.CharField(default='', max_length=255, verbose_name='주소')
    address_detail = models.CharField(default='', max_length=255, verbose_name='상세주소')

    registration_no = models.CharField(null=True, max_length=20, verbose_name='가맹점사업자등록번호')
    image = models.ImageField(max_length=300, null=True, upload_to="image/shop/", verbose_name='가맹점이미지')
    location_image = models.ImageField(max_length=300, null=True, upload_to="image/shop_location/", verbose_name='가맹점위치 이미지')

    waiting_time = models.PositiveIntegerField(default=10, verbose_name='팀 당 예상 대기시간')

    logo_image1 = models.ImageField(max_length=300, null=True, upload_to="image/shop_logo/", verbose_name='가맹점 로고이미지')
    entry_image1 = models.ImageField(max_length=300, null=True, upload_to="image/shop_entry/", verbose_name='가맹점 입장이미지')
    logo_image2 = models.ImageField(max_length=300, null=True, upload_to="image/shop_logo/", verbose_name='가맹점 로고이미지2')
    entry_image2 = models.ImageField(max_length=300, null=True, upload_to="image/shop_entry/", verbose_name='가맹점 입장이미지2')

    entry_membername = models.BooleanField(default=True)
    entry_phone = models.BooleanField(default=True)
    entry_email = models.BooleanField(default=False)
    entry_car_plate_no = models.BooleanField(default=False)

    main_tid = models.CharField(default='', max_length=20, verbose_name='메인 tid')
    receipt = models.CharField(default='',  max_length=255, verbose_name='영수증내용')

    shop_receipt_flag = models.BooleanField(default=True, verbose_name='매장용 영수증')

    table_paginate_by = models.PositiveIntegerField(default=50)
    table_time = models.PositiveIntegerField(default=0, verbose_name='테이블이용시간') #0: 무제한
    additional_fee_time = models.PositiveIntegerField(default=10, verbose_name='추가요금 시간') #10: 10분

    pos_ad_video = models.FileField(max_length=300, null=True, upload_to='video/pos_ad/', verbose_name='포스광고')

    tbridge = models.BooleanField(default=False, verbose_name='티브릿지 연동')

    aligo_sender_key = models.CharField(max_length=50, null=True, verbose_name='알리고 샌더키')
    aligo_entry_template_code1 = models.CharField(max_length=10, null=True, verbose_name='알리고 입장등록템플릿')
    aligo_entry_template_code2 = models.CharField(max_length=10, null=True, verbose_name='알리고 호출템플릿')

    coupon_flag = models.BooleanField(default=False)

    pos = models.ForeignKey(Pos, on_delete=models.SET_NULL, null=True)

    printer_port1 = models.CharField(max_length=5, default='COM1', null=True, verbose_name='프린터 port1')
    printer_port2 = models.CharField(max_length=5, default='', null=True, verbose_name='프린터 port2')
    printer_baud_rate = models.PositiveIntegerField(default=9600, verbose_name='프린터 baud rate')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    
    class Meta : 
        db_table = 'shop'


# 에이전시 소속 가맹점
class AgencyShop(models.Model):
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='agency_shop')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    status = models.BooleanField(default=True, verbose_name='상태')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')

    class Meta : 
        constraints = [
            models.UniqueConstraint(fields=['agency', 'shop'], name='agency_shop_unique')
        ]
        db_table = 'agency_shop'



# 가맹점관리자
class ShopAdmin(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shop_admin')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')

    class Meta : 
        constraints = [
            models.UniqueConstraint(fields=['shop', 'user'], name='shop_user_unique')
        ]
        db_table = 'shop_admin'


# 가맹점회원
class ShopMember(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    membername = models.CharField(default='', max_length=50, verbose_name='회원명')
    phone = models.CharField(max_length=30, verbose_name='전화번호')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta :
        constraints = [
            models.UniqueConstraint(fields=['shop', 'phone'], name='shop_phone_unique')
        ]
        db_table = 'shop_member'

# 가맹점쿠폰
class ShopCoupon(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, verbose_name='쿠폰명')
    expiration_period = models.PositiveIntegerField(verbose_name='유효기간', default=365) #365일
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta :
        db_table = 'shop_coupon'


# 가맹점회원쿠폰
class ShopMemberCoupon(models.Model):
    shop_member = models.ForeignKey(ShopMember, on_delete=models.CASCADE, related_name='shop_member_coupon')
    shop_coupon = models.ForeignKey(ShopCoupon, on_delete=models.SET_NULL, related_name='shop_member_coupon', null=True)
    name = models.CharField(max_length=50, verbose_name='쿠폰명')
    status = models.CharField(max_length=10, default='0') # 0=미사용, 1=사용완료, 2=만료
    expiration_date = models.DateTimeField(verbose_name='만료일', null=True)
    used_at = models.DateTimeField(null=True, verbose_name='사용일')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta :
        db_table = 'shop_member_coupon'

# shop table
class ShopTable(models.Model):
    pos = models.ForeignKey(Pos, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    table_no = models.IntegerField()
    name = models.CharField(max_length=100, verbose_name='테이블명')
    exit_color = models.CharField(default='2c70f5', max_length=20, verbose_name='퇴장하기 버튼 색')
    
    shop_member = models.ForeignKey(ShopMember, on_delete=models.SET_NULL, null=True)
    entry_time = models.DateTimeField(null=True, verbose_name='입장시간')
    tid = models.CharField(default='', max_length=20, verbose_name='tid')

    cart = models.TextField(verbose_name='장바구니', null=True)
    total_discount = models.PositiveIntegerField(default=0, verbose_name='총 할인 금액')
    total_price = models.PositiveIntegerField(default=0, verbose_name='총 결제 금액')
    total_additional = models.PositiveIntegerField(default=0, verbose_name='총 추가 금액')

    fixed_category_id = models.PositiveIntegerField(default=0, verbose_name='고정 서브 카테고리')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['pos', 'shop', 'table_no'], name='pos_shop_table_no_unique')
        ]
        db_table='shop_table'

class ShopTableLog(models.Model):
    shop_table = models.ForeignKey(ShopTable, on_delete=models.CASCADE)
    shop_member = models.ForeignKey(ShopMember, on_delete=models.SET_NULL, null=True)
    status = models.BooleanField(default=False) #False:입장 True:퇴장
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')

    class Meta:
        db_table='shop_table_log'

# 대분류
class MainCategory(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, null=True)
    name_kr = models.CharField(max_length=100, verbose_name='대분류 한글이름')
    name_en = models.CharField(max_length=100, verbose_name='대분류 영문이름')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['shop', 'name_kr'], name='shop_name_kr_unique'),
            models.UniqueConstraint(fields=['shop', 'name_en'], name='shop_name_en_unique')
        ]
        db_table='main_category'

# 소분류
class SubCategory(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='sub_category', null=True)
    main_category = models.ForeignKey(MainCategory, on_delete=models.PROTECT, related_name='sub_category')
    name_kr = models.CharField(max_length=100, verbose_name='소분류 한글이름', null=True)
    name_en = models.CharField(max_length=100, verbose_name='소분류 영문이름', null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['shop', 'main_category', 'name_kr'], name='shop_main_category_name_kr_unique'),
            models.UniqueConstraint(fields=['shop', 'main_category', 'name_en'], name='shop_main_category_name_en_unique')
        ]

        db_table='sub_category'

# 상품
class Goods(models.Model):
    code = models.CharField(max_length=20, verbose_name='상품코드', unique=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.PROTECT)
    name_kr = models.CharField(max_length=100, verbose_name='상품한글명')
    name_en = models.CharField(max_length=100, verbose_name='상품영문명')
    sale_price = models.PositiveIntegerField(verbose_name='판매가격', default=0)
    price = models.PositiveIntegerField(verbose_name='제품가격', default=0)
    image = models.ImageField(max_length=300, upload_to="image/goods/%Y/%m/%d/", verbose_name='상품이미지')
    image_thumbnail = models.ImageField(max_length=300, upload_to="image/goods/%Y/%m/%d/", verbose_name='상품이미지 썸네일 정사각형')
    status = models.BooleanField(default=True, verbose_name='판매상태') #True:판매 False:판매중단
    kiosk_display = models.BooleanField(default=True, verbose_name='키오스크 표시') #True:표시 False:표시안함

    stock = models.IntegerField(verbose_name='재고수량', default=0)
    stock_flag = models.BooleanField(default=False, verbose_name='재고관리사용여부') #재고 관리 사용 여부
    option_flag = models.BooleanField(default=False, verbose_name='옵션사용여부') #옵션 사용 여부에 따라 옵션재고 수량을수 있음.
    soldout = models.BooleanField(default=False, verbose_name='품절') #True:품절

    after_payment_goods = models.CharField(null=True, verbose_name='결제후들어갈상품 ID list', max_length=100)
    additional_fee_goods = models.PositiveBigIntegerField(null=True, verbose_name='추가요금 상품 ID')
    
    pos_rank = models.PositiveIntegerField(default=0, verbose_name='포스 정렬 순위')
    kiosk_rank = models.PositiveIntegerField(default=0, verbose_name='키오스크 정렬 순위')

    delete_flag = models.BooleanField(default=False, verbose_name='삭제처리')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    
    class Meta : 
        db_table = 'goods'

#상품옵션
class GoodsOption(models.Model):
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, related_name='option')
    required = models.BooleanField(default=True, verbose_name='필수여부')
    name_kr = models.CharField(max_length=100, verbose_name='옵션한글명', null=True)
    name_en = models.CharField(max_length=100, verbose_name='옵션영문명', null=True)

    class Meta:
        db_table='goods_option'

#상품옵션상세
class GoodsOptionDetail(models.Model):
    goods_option = models.ForeignKey(GoodsOption, on_delete=models.CASCADE, related_name='option_detail')
    name_kr = models.CharField(max_length=100, verbose_name='옵션한글명', null=True)
    name_en = models.CharField(max_length=100, verbose_name='옵션영문명', null=True)
    price = models.PositiveIntegerField(default=0, verbose_name='옵션가격')
    stock = models.IntegerField(default=0, verbose_name='재고수량')
    stock_flag = models.BooleanField(default=False, verbose_name='재고관리사용여부') #재고 관리 사용 여부
    soldout = models.BooleanField(default=False, verbose_name='품절 여부') #품절 여부
    
    class Meta:
        db_table='goods_option_detail'


class ShopPersonType(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    person_type = models.ForeignKey(PersonType, on_delete=models.CASCADE)
    description = models.CharField(default='', max_length=255, verbose_name='설명')
    weekday_goods = models.ForeignKey(Goods, on_delete=models.SET_NULL, null=True, related_name='shop_person_type_weekday')
    weekend_goods = models.ForeignKey(Goods, on_delete=models.SET_NULL, null=True, related_name='shop_person_type_weekend')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta :
        constraints = [
            models.UniqueConstraint(fields=['shop', 'person_type'], name='shop_person_type_unique')
        ]
        db_table = 'shop_person_type'

# 가맹점 입장 옵션
class ShopEntryOption(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='entry_option')
    required = models.BooleanField(default=True, verbose_name='필수여부')
    name = models.CharField(max_length=100, verbose_name='옵션명')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['shop', 'name'], name='shop_name_unique')
        ]
        db_table='shop_entry_option'


# 가맹점 입장 옵션 상세
class ShopEntryOptionDetail(models.Model):
    shop_entry_option = models.ForeignKey(ShopEntryOption, on_delete=models.CASCADE, related_name='entry_option_detail')
    name = models.CharField(max_length=100, verbose_name='옵션명')
    image = models.ImageField(max_length=300, upload_to="image/shop_entry_option/%Y/%m/%d/", verbose_name='옵션이미지', default='image/goods/default.jpg')
    
    class Meta:
        db_table='shop_entry_option_detail'
        
class EntryQueue(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    membername = models.CharField(max_length=20, verbose_name='예약자명')
    phone = models.CharField(max_length=20, verbose_name='전화번호')
    car_plate_no = models.CharField(max_length=20, verbose_name='차량번호', default='')
    email = models.CharField(max_length=50, verbose_name='이메일', default='')
    status = models.CharField(max_length=10, verbose_name='상태', default='0') #0:대기 1:입장 2:취소
    date = models.DateField(auto_now_add=True, verbose_name='날짜')
    remark = models.TextField(null=True, verbose_name='비고')
    called_at = models.DateTimeField(null=True, verbose_name='마지막 호출일') 
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta :
        constraints = [
            models.UniqueConstraint(fields=['shop', 'order', 'date'], name='shop_order_date_unique')
        ]
        db_table = 'entry_queue'

class EntryQueueDetail(models.Model):
    entry_queue = models.ForeignKey(EntryQueue, on_delete=models.CASCADE, related_name='entry_queue_detail')
    name = models.CharField(max_length=100)
    goods = models.ForeignKey(Goods, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1, verbose_name='수량')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta : 
        db_table = 'entry_queue_detail'

#상품주문
class Checkout(models.Model):
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, null=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    code = models.CharField(max_length=100, unique=True)
    table_no = models.IntegerField(default=None, null=True)
    mainpos_id = models.IntegerField(default=0)
    shop_member = models.ForeignKey(ShopMember, on_delete=models.SET_NULL, null=True)
    final_price = models.PositiveIntegerField(default=0, verbose_name='최종결제금액')
    final_discount = models.PositiveIntegerField(default=0, verbose_name='전체 할인 금액')
    final_additional = models.PositiveIntegerField(default=0, verbose_name='총 추가 금액')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')

    class Meta:
        db_table='checkout'

#상품주문상세
class CheckoutDetail(models.Model):
    checkout = models.ForeignKey(Checkout, on_delete=models.CASCADE, related_name="checkout_detail")
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, verbose_name='수량')
    price = models.PositiveIntegerField(verbose_name='가격')
    sale_option_price = models.PositiveIntegerField(verbose_name='당시옵션판매가격')
    sale_price = models.PositiveIntegerField(verbose_name='당시상품판매가격')
    total_price = models.PositiveIntegerField(verbose_name='총가격')
    
    class Meta:
        db_table='checkout_detail'

#상품주문옵션상세
class CheckoutDetailOption(models.Model):
    checkout_detail = models.ForeignKey(CheckoutDetail, on_delete=models.CASCADE, related_name="checkout_detail_option")
    goods_option_detail = models.ForeignKey(GoodsOptionDetail, on_delete=models.CASCADE)
    
    class Meta:
        db_table='checkout_detail_option'

#주문
class Order(models.Model):
    agency = models.ForeignKey(Agency, on_delete=models.PROTECT, null=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    
    table_no = models.IntegerField(default=None, null=True)
    mainpos_id = models.IntegerField(default=0)
    shop_member = models.ForeignKey(ShopMember, on_delete=models.SET_NULL, null=True)

    order_type = models.CharField(max_length=10, verbose_name='주문방식', default='0') # 0: pos, 1: QR, 2: 키오스크
    order_name_kr = models.CharField(max_length=255, verbose_name='주문한글명', null=True)
    order_name_en = models.CharField(max_length=255, verbose_name='주문영문명', null=True)
    order_code = models.CharField(max_length=50, verbose_name='주문코드')
    order_no = models.PositiveIntegerField(default=0, verbose_name='주문번호')
    order_membername = models.CharField(max_length=20, default='', verbose_name='주문자명')
    order_phone = models.CharField(max_length=20, default='', verbose_name='주문자번호')

    status = models.CharField(max_length=10, verbose_name='결제상태', default='0') #'0':주문요청 '1':결제완료 '2':취소, '3': 준비중, '4': 주문완료, 5: '수령완료', 6: '부분취소'

    final_price = models.PositiveIntegerField(default=0, verbose_name='최종결제요청금액')
    final_discount = models.PositiveIntegerField(default=0, verbose_name='최종 할인 금액') #전체할인 (개별할인 포함 x)
    final_additional = models.PositiveIntegerField(default=0, verbose_name='총 추가 금액') #전체추가요금

    payment_price = models.PositiveIntegerField(default=0, verbose_name='실제결제금액')
    payment_method = models.CharField(max_length=10, verbose_name='결제수단', default='')  #CARD 0, #CASH 1, #MIXED 2

    order_complete_sms = models.BooleanField(default=False, verbose_name='주문완료문자')

    after_payment_cart = models.TextField(verbose_name='결제이후 장바구니 상품', null=True) # json

    date = models.DateField(auto_now_add=True, verbose_name='날짜')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    delete_flag = models.BooleanField(default=False, verbose_name='삭제여부')
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['shop', 'order_code'], name='shop_order_code_unique'),
            models.UniqueConstraint(fields=['shop', 'order_no', 'date'], name='shop_order_no_date_unique'),
        ]
        db_table='order'

#주문상품
class OrderGoods(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_goods')    
    goods = models.ForeignKey(Goods, on_delete=models.PROTECT, related_name='order_goods')
    name_kr = models.CharField(null=True, max_length=255, verbose_name='제품영어명')
    name_en = models.CharField(null=True, max_length=255, verbose_name='제품한글명')
    price = models.PositiveIntegerField(default=0, verbose_name='가격')
    option_kr = models.CharField(max_length=255, verbose_name='옵션한글명', null=True)
    option_en = models.CharField(max_length=255, verbose_name='옵션영문명', null=True)
    option_price = models.PositiveIntegerField(default=0, verbose_name='옵션추가비용')
    sale_option_price = models.PositiveIntegerField(verbose_name='당시옵션판매가격')
    sale_price = models.PositiveIntegerField(verbose_name='당시상품판매가격')
    quantity = models.PositiveIntegerField(default=1, verbose_name='주문수량')
    total_price = models.PositiveIntegerField(default=0, verbose_name='총가격')
    
    class Meta:
        db_table='order_goods'

class OrderGoodsOption(models.Model):
    order_goods = models.ForeignKey(OrderGoods, on_delete=models.CASCADE, related_name="order_goods_option")
    goods_option_detail = models.ForeignKey(GoodsOptionDetail, on_delete=models.CASCADE)
    
    class Meta:
        db_table='order_goods_option'

class OrderPayment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_payment')

    status = models.BooleanField(default=True, verbose_name='결제여부')
    payment_method = models.CharField(max_length=10, verbose_name='결제수단', default='0') #CARD : 0, #CASH: 1

    refNo = models.CharField(max_length=20, default='')
    mbrNo = models.CharField(max_length=20, default='')
    mbrRefNo = models.CharField(max_length=100, default='')
    tranDate = models.CharField(max_length=20, default='')
    tranTime = models.CharField(max_length=20, default='')
    goodsName = models.CharField(max_length=100, default='')
    amount = models.IntegerField(default=0)
    taxAmount = models.IntegerField(default=0)
    feeAmount = models.IntegerField(default=0)
    taxFreeAmount = models.IntegerField(default=0)
    greenDepositAmount = models.IntegerField(default=0)
    installment = models.CharField(max_length=20, default='')
    customerName = models.CharField(max_length=50, default='')
    customerTelNo = models.CharField(max_length=20, default='')
    applNo = models.CharField(max_length=20, default='')
    cardNo = models.CharField(max_length=50, default='')
    issueCompanyNo = models.CharField(max_length=10, default='')
    issueCompanyName = models.CharField(max_length=20, default='')
    issueCardName = models.CharField(max_length=20, default='')
    acqCompanyNo = models.CharField(max_length=20, default='')
    acqCompanyName = models.CharField(max_length=20, default='')
    payType = models.CharField(max_length=10, default='')
    cardAmount = models.IntegerField(default=0)
    pointAmount = models.IntegerField(default=0)
    couponAmount = models.IntegerField(default=0)
    cardPointAmount = models.IntegerField(default=0)
    cardPointApplNo = models.CharField(max_length=20, default='')
    bankCode = models.CharField(max_length=20, null=True)
    accountNo = models.CharField(max_length=20, null=True)
    accountCloseDate = models.CharField(max_length=20, null=True)
    billkey = models.CharField(max_length=20, null=True)

    #pos
    tid = models.CharField(max_length=20, default='')
    approvalNumber = models.CharField(max_length=20, null=True)
    additionalInfo = models.CharField(max_length=300, null=True)
    posEntryMode = models.CharField(max_length=10, default='')

    cashReceiptStatus = models.BooleanField(default=False, verbose_name='추가현금영수증여부')
    cashReceiptCardNo = models.CharField(max_length=50, default='')
    cashReceiptApprovalNumber = models.CharField(max_length=20, null=True)
    cashReceiptApprovalDate = models.CharField(max_length=20, default='')
    
    cancelled_at = models.DateTimeField(null=True, verbose_name='취소일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')

    class Meta:
        db_table='order_payment'


class SmsLog(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.SET_NULL, null=True)
    shop_name = models.CharField(max_length=100, verbose_name='가맹점한글명', null=True)
    phone = models.CharField(max_length=30, verbose_name='전화번호', null=True)
    message = models.TextField(null=True)
    message_type = models.CharField(default='0', verbose_name='0:문자, 1:알림톡', max_length=10)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')

    class Meta:
        db_table='sms_log'