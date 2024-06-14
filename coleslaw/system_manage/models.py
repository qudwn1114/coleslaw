from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

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

    class Meta:
        db_table='auth_profile'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

# 가맹점
class Shop(models.Model):
    name = models.CharField(max_length=100, verbose_name='가맹점이름', unique=True)
    description = models.CharField(default='', max_length=255, verbose_name='설명')
    
    phone = models.CharField(null=True, max_length=20, verbose_name='가맹점연락처')
    representative = models.CharField(null=True, max_length=20, verbose_name='대표자이름')

    zipcode = models.CharField(default='', max_length=10, verbose_name='우편번호')
    address = models.CharField(default='', max_length=255, verbose_name='주소')
    address_detail = models.CharField(default='', max_length=255, verbose_name='상세주소')

    registration_no = models.CharField(null=True, max_length=20, verbose_name='가맹점사업자등록번호')
    image = models.ImageField(max_length=300, null=True, upload_to="image/shop/", verbose_name='가맹점이미지')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta : 
        db_table = 'shop'

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
    price = models.PositiveIntegerField(verbose_name='제품가격', default=0)
    image = models.ImageField(max_length=300, upload_to="image/goods/%Y/%m/%d/", verbose_name='상품이미지')
    image_thumbnail = models.ImageField(max_length=300, upload_to="image/goods/%Y/%m/%d/", verbose_name='상품이미지 썸네일 정사각형')
    status = models.BooleanField(default=True, verbose_name='판매상태') #True:판매중 False:판매중단
    delete_flag = models.BooleanField(default=False, verbose_name='삭제처리')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    
    class Meta : 
        db_table = 'goods'

class ShopEntryGoods(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    goods = models.OneToOneField(Goods, on_delete=models.CASCADE, related_name='entry_goods')
    sequence = models.IntegerField(verbose_name='순서')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta : 
        constraints = [
            models.UniqueConstraint(fields=['shop', 'sequence'], name='shop_sequence_unique')
        ]
        db_table = 'shop_entry_goods'
        
class EntryQueue(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    date = models.DateField(auto_now_add=True, verbose_name='날짜')
    membername = models.CharField(max_length=20, verbose_name='예약자명')
    phone = models.CharField(max_length=20, verbose_name='전화번호')
    car_plate_no = models.CharField(max_length=20, verbose_name='차량번호', default='')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta :
        constraints = [
            models.UniqueConstraint(fields=['shop', 'order', 'date'], name='shop_order_date_unique')
        ]
        db_table = 'entry_queue'

class EntryQueueDetail(models.Model):
    entry_queue = models.ForeignKey(EntryQueue, on_delete=models.CASCADE)
    goods = models.ForeignKey(Goods, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1, verbose_name='수량')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta : 
        db_table = 'entry_queue_detail'