from django.urls import path, include

from django.contrib.auth.views import LogoutView
from shop_manage.views.shop_manage_views.auth_views import HomeView, LoginView, PermissionDeniedView, NotFoundView, shop_main_sales, shop_main_orders, shop_sales_report, UserPasswordEditView
from shop_manage.views.entry_manage_views.person_type_manage_views import PersonTypeManageView, PersonTypeCreateView, PersonTypeDetailView, PersonTypeEditView, PersonTypeGoodsManageView
from shop_manage.views.entry_manage_views.entry_option_manage_views import ShopEntryOptionManageView, ShopEntryOptionDetailManageView, ShopEntryOptionDetailImageView
from shop_manage.views.table_manage_views.table_manage_views import ShopTableManageView, ShopTableCreateView
from shop_manage.views.pos_manage_views.pos_manage_views import ShopPosManageView, ShopPosCreateView, ShopPosDetailView, ShopPosEditView
from shop_manage.views.goods_manage_views.goods_manage_views import GoodsManageView, GoodsCreateView, GoodsDetailView, GoodsEditView, goods
from shop_manage.views.goods_manage_views.option_manage_views import OptionManageView, OptionDetailManageView
from shop_manage.views.goods_manage_views.rank_manage_views import GoodsRankManageView, rank_goods, update_rank_goods
from shop_manage.views.order_manage_views.order_manage_views import OrderManageView, order_complete_sms, order_goods
from shop_manage.views.sms_manage_views.sms_manage_view import SMSManageManageView
from shop_manage.views.coupon_manage_views.coupon_manage_views import ShopCouponManageView, ShopCouponCreateView, ShopCouponDetailView, ShopCouponEditView
from shop_manage.views.category_manage_views.category_manage_views import CategoryManageView, sub_category, category, update_category_rank


app_name='shop_manage'
urlpatterns = [
    path('<int:shop_id>/', HomeView.as_view(), name='home'),
    path('<int:shop_id>/main/sales/', shop_main_sales),
    path('<int:shop_id>/main/orders/', shop_main_orders),
    path('<int:shop_id>/main/report/', shop_sales_report),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='shop_manage:login'), name='logout'),
    path('denied/', PermissionDeniedView.as_view(), name='denied'),
    path('notfound/', NotFoundView.as_view(), name='notfound'),
    path('user-password-edit/', UserPasswordEditView.as_view(), name='user_password_edit'),

    path('<int:shop_id>/person-type-manage/', PersonTypeManageView.as_view(), name='person_type_manage'),
    path('<int:shop_id>/person-type-create/', PersonTypeCreateView.as_view(), name='person_type_create'),
    path('<int:shop_id>/person-type-detail/<int:pk>/', PersonTypeDetailView.as_view(), name='person_type_detail'),
    path('<int:shop_id>/person-type-edit/<int:pk>/', PersonTypeEditView.as_view(), name='person_type_edit'),
    path('<int:shop_id>/person-type-goods/<int:pk>/<str:week_type>/', PersonTypeGoodsManageView.as_view(), name='person_type_goods'),
    path('<int:shop_id>/entry-option-manage/', ShopEntryOptionManageView.as_view(), name='entry_option_manage'),
    path('<int:shop_id>/entry-option-detail-manage/', ShopEntryOptionDetailManageView.as_view(), name='entry_option_detail_manage'),
    path('<int:shop_id>/entry-option-detail-image/', ShopEntryOptionDetailImageView.as_view(), name='entry_option_detail_image'),
    

    path('<int:shop_id>/table-manage/', ShopTableManageView.as_view(), name='table_manage'),
    path('<int:shop_id>/table-create/', ShopTableCreateView.as_view(), name='table_create'),

    path('<int:shop_id>/pos-manage/', ShopPosManageView.as_view(), name='pos_manage'),
    path('<int:shop_id>/pos-create/', ShopPosCreateView.as_view(), name='pos_create'),

    path('<int:shop_id>/shop-pos-detail/', ShopPosDetailView.as_view(), name='shop_pos_detail'),
    path('<int:shop_id>/shop-pos-edit/', ShopPosEditView.as_view(), name='shop_pos_edit'),

    path('<int:shop_id>/goods-manage/', GoodsManageView.as_view(), name='goods_manage'),
    path('<int:shop_id>/goods-create/', GoodsCreateView.as_view(), name='goods_create'),
    path('<int:shop_id>/goods-detail/<int:pk>/', GoodsDetailView.as_view(), name='goods_detail'),
    path('<int:shop_id>/goods-edit/<int:pk>/', GoodsEditView.as_view(), name='goods_edit'),
    path('<int:shop_id>/goods/', goods),
    path('<int:shop_id>/goods-rank-manage/', GoodsRankManageView.as_view(), name='goods_rank_manage'),
    path('<int:shop_id>/rank-goods/<int:sub_category_id>/', rank_goods),
    path('<int:shop_id>/rank-goods/<int:sub_category_id>/update/', update_rank_goods),

    path('<int:shop_id>/option-manage/<int:pk>/', OptionManageView.as_view(), name='option_manage'),
    path('<int:shop_id>/option-detail-manage/', OptionDetailManageView.as_view(), name='option_detail_manage'),

    path('<int:shop_id>/order-manage/', OrderManageView.as_view(), name='order_manage'),
    path('<int:shop_id>/order-complete-sms/', order_complete_sms),
    path('<int:shop_id>/order-goods/<int:order_id>/', order_goods),

    path('<int:shop_id>/sms-manage/', SMSManageManageView.as_view(), name='sms_manage'),

    path('<int:shop_id>/coupon-manage/', ShopCouponManageView.as_view(), name='coupon_manage'),
    path('<int:shop_id>/coupon-create/', ShopCouponCreateView.as_view(), name='coupon_create'),
    path('<int:shop_id>/coupon-detail/<int:pk>/', ShopCouponDetailView.as_view(), name='coupon_detail'),
    path('<int:shop_id>/coupon-edit/<int:pk>/', ShopCouponEditView.as_view(), name='coupon_edit'),


    #카테고리관리
    path('<int:shop_id>/category-manage/', CategoryManageView.as_view(), name='category_manage'),
    path('<int:shop_id>/sub-category/', sub_category),
    path('<int:shop_id>/category/', category),
    path('<int:shop_id>/category-rank/update/', update_category_rank),
]