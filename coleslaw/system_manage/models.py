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
    name = models.CharField(max_length=100, verbose_name='가맹점카테고리이름', unique=True)
    description = models.CharField(default='', max_length=255, verbose_name='설명')
    image = models.ImageField(max_length=300, null=True, upload_to="image/shop_category/", verbose_name='가맹점카테고리이미지')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta : 
        db_table = 'shop_category'


# 가맹점
class Shop(models.Model):
    agency = models.ForeignKey(Agency, on_delete=models.PROTECT, related_name='shop', verbose_name='메인 agency')
    shop_category = models.ForeignKey(ShopCategory, on_delete=models.PROTECT, related_name='shop')
    name = models.CharField(max_length=100, verbose_name='가맹점이름', unique=True)
    description = models.CharField(default='', max_length=255, verbose_name='설명')
    
    phone = models.CharField(null=True, max_length=20, verbose_name='가맹점연락처')
    representative = models.CharField(null=True, max_length=20, verbose_name='대표자이름')

    zipcode = models.CharField(default='', max_length=10, verbose_name='우편번호')
    address = models.CharField(default='', max_length=255, verbose_name='주소')
    address_detail = models.CharField(default='', max_length=255, verbose_name='상세주소')

    registration_no = models.CharField(null=True, max_length=20, verbose_name='가맹점사업자등록번호')
    image = models.ImageField(max_length=300, null=True, upload_to="image/shop/", verbose_name='가맹점이미지')

    waiting_time = models.PositiveIntegerField(default=10, verbose_name='팀 당 예상 대기시간')

    logo_image1 = models.ImageField(max_length=300, null=True, upload_to="image/shop_logo/", verbose_name='가맹점 로고이미지')
    entry_image1 = models.ImageField(max_length=300, null=True, upload_to="image/shop_entry/", verbose_name='가맹점 입장이미지')
    logo_image2 = models.ImageField(max_length=300, null=True, upload_to="image/shop_logo/", verbose_name='가맹점 로고이미지2')
    entry_image2 = models.ImageField(max_length=300, null=True, upload_to="image/shop_entry/", verbose_name='가맹점 입장이미지2')

    entry_membername = models.BooleanField(default=True)
    entry_phone = models.BooleanField(default=True)
    entry_email = models.BooleanField(default=False)
    entry_car_plate_no = models.BooleanField(default=False)

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

# shop table
class ShopTable(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    table_no = models.PositiveIntegerField()
    name = models.CharField(max_length=100, verbose_name='테이블명')
    cart = models.TextField(verbose_name='장바구니', null=True)
    total_price = models.PositiveIntegerField(default=0, verbose_name='총 결제 금액')
    shop_member = models.ForeignKey(ShopMember, on_delete=models.SET_NULL, null=True)
    entry_time = models.DateTimeField(null=True, verbose_name='입장시간')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['shop', 'table_no'], name='shop_table_no_unique')
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
    name = models.CharField(max_length=100, verbose_name='대분류이름', unique=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        db_table='main_category'

# 소분류
class SubCategory(models.Model):
    main_category = models.ForeignKey(MainCategory, on_delete=models.PROTECT, related_name='sub_category')
    name = models.CharField(max_length=100, verbose_name='소분류이름')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['main_category', 'name'], name='main_category_name_unique')
        ]
        db_table='sub_category'

# 상품
class Goods(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.PROTECT)
    name = models.CharField(max_length=100, verbose_name='상품명')
    sale_price = models.PositiveIntegerField(verbose_name='판매가격', default=0)
    price = models.PositiveIntegerField(verbose_name='제품가격', default=0)
    image = models.ImageField(max_length=300, upload_to="image/goods/%Y/%m/%d/", verbose_name='상품이미지')
    image_thumbnail = models.ImageField(max_length=300, upload_to="image/goods/%Y/%m/%d/", verbose_name='상품이미지 썸네일 정사각형')
    status = models.BooleanField(default=True, verbose_name='판매상태') #True:판매중 False:판매중단
    stock = models.IntegerField(verbose_name='재고수량', default=0)
    stock_flag = models.BooleanField(default=False, verbose_name='재고관리사용여부') #재고 관리 사용 여부
    option_flag = models.BooleanField(default=False, verbose_name='옵션사용여부') #옵션 사용 여부에 따라 옵션재고 수량을수 있음.
    soldout = models.BooleanField(default=False, verbose_name='품절') #True:품절
    delete_flag = models.BooleanField(default=False, verbose_name='삭제처리')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    
    class Meta : 
        db_table = 'goods'

#상품옵션
class GoodsOption(models.Model):
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, related_name='option')
    required = models.BooleanField(default=True, verbose_name='필수여부')
    name = models.CharField(max_length=100, verbose_name='옵션명')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['goods', 'name'], name='goods_name_unique')
        ]
        db_table='goods_option'

#상품옵션상세
class GoodsOptionDetail(models.Model):
    goods_option = models.ForeignKey(GoodsOption, on_delete=models.CASCADE, related_name='option_detail')
    name = models.CharField(max_length=100, verbose_name='옵션명')
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
    goods = models.ForeignKey(Goods, on_delete=models.SET_NULL, null=True)
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
    shop_member = models.ForeignKey(ShopMember, on_delete=models.SET_NULL, null=True)
    order = models.PositiveIntegerField()
    membername = models.CharField(max_length=20, verbose_name='예약자명')
    phone = models.CharField(max_length=20, verbose_name='전화번호')
    car_plate_no = models.CharField(max_length=20, verbose_name='차량번호', default='')
    email = models.CharField(max_length=50, verbose_name='이메일', default='')
    status = models.CharField(max_length=10, verbose_name='상태', default='0') #0:대기 1:입장 2:취소
    date = models.DateField(auto_now_add=True, verbose_name='날짜')
    remark = models.TextField(null=True, verbose_name='비고')
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
    table_no = models.PositiveIntegerField(default=None, null=True)
    shop_member = models.ForeignKey(ShopMember, on_delete=models.SET_NULL, null=True)
    final_price = models.PositiveIntegerField(default=0, verbose_name='최종결제금액')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')

    class Meta:
        db_table='checkout'

#상품주문상세
class CheckoutDetail(models.Model):
    checkout = models.ForeignKey(Checkout, on_delete=models.CASCADE, related_name="checkout_detail")
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, verbose_name='수량')
    price = models.PositiveIntegerField(verbose_name='가격')
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
    
    table_no = models.PositiveIntegerField(default=None, null=True)
    shop_member = models.ForeignKey(ShopMember, on_delete=models.SET_NULL, null=True)

    order_type = models.CharField(max_length=10, verbose_name='주문방식', default='0') # 0: pos, 1: QR, 2: 키오스크
    order_name = models.CharField(max_length=255, verbose_name='주문명', null=True)
    order_code = models.CharField(max_length=50, verbose_name='주문코드')
    order_no = models.PositiveIntegerField(default=0, verbose_name='주문번호')
    order_membername = models.CharField(max_length=20, default='', verbose_name='주문자명')
    order_phone = models.CharField(max_length=20, default='', verbose_name='주문자번호')

    status = models.CharField(max_length=10, verbose_name='결제상태', default='0') #'0':주문요청 '1':결제완료 '2':취소, '3': 준비중, '4': 주문완료, 5: '수령완료'

    final_price = models.PositiveIntegerField(default=0, verbose_name='최종결제요청금액')

    payment_price = models.PositiveIntegerField(default=0, verbose_name='실제결제금액')
    payment_method = models.CharField(max_length=10, verbose_name='결제수단', default='')  #CARD, #CASH
    cancelled_at = models.DateTimeField(null=True, verbose_name='취소일')

    order_complete_sms = models.BooleanField(default=False, verbose_name='주문완료문자')

    date = models.DateField(auto_now_add=True, verbose_name='날짜')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    delete_flag = models.BooleanField(default=False, verbose_name='삭제여부')

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
    custormerName = models.CharField(max_length=50, default='')
    customerTelNo = models.CharField(max_length=20, default='')
    applNo = models.CharField(max_length=20, default='')
    cardNo = models.CharField(max_length=100, default='')
    issueCompanyNo = models.CharField(max_length=10, default='')
    issueCompanyName = models.CharField(max_length=20, default='')
    issueCardName = models.CharField(max_length=20, default='')
    acqCompanyNo = models.CharField(max_length=20, default='')
    acqCompanyName = models.CharField(max_length=20, default='')
    payType = models.CharField(max_length=10, default='')
    cardAmount = models.IntegerField(default=0)
    pointAmount = models.IntegerField(default=0)
    couponAmount = models.IntegerField(default=0)
    custormmerName = models.CharField(max_length=50, default='')
    custormmerTelNo = models.CharField(max_length=50, default='')
    cardPointAmount = models.IntegerField(default=0)
    cardPointApplNo = models.CharField(max_length=20, default='')
    bankCode = models.CharField(max_length=20, null=True)
    accountNo = models.CharField(max_length=20, null=True)
    accountCloseDate = models.CharField(max_length=20, null=True)
    billkey = models.CharField(max_length=20, null=True)

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
    name = models.CharField(null=True, max_length=255, verbose_name='제품명')
    price = models.PositiveIntegerField(default=0, verbose_name='가격')
    option = models.CharField(max_length=255, verbose_name='옵션', null=True)
    option_price = models.PositiveIntegerField(default=0, verbose_name='옵션추가비용')
    quantity = models.PositiveIntegerField(default=1, verbose_name='주문수량')
    total_price = models.PositiveIntegerField(default=0, verbose_name='총가격')
    

    class Meta:
        db_table='order_goods'

class OrderGoodsOption(models.Model):
    order_goods = models.ForeignKey(OrderGoods, on_delete=models.CASCADE, related_name="order_goods_option")
    goods_option_detail = models.ForeignKey(GoodsOptionDetail, on_delete=models.CASCADE)
    
    class Meta:
        db_table='order_goods_option'