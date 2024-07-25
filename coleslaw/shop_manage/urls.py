from django.urls import path, include

from django.contrib.auth.views import LogoutView
from shop_manage.views.shop_manage_views.auth_views import HomeView, LoginView, PermissionDeniedView, NotFoundView, shop_main_sales, shop_main_orders, UserPasswordEditView
from shop_manage.views.entry_manage_views.person_type_manage_views import PersonTypeManageView, PersonTypeCreateView, PersonTypeDetailView, PersonTypeEditView, PersonTypeGoodsManageView
from shop_manage.views.entry_manage_views.entry_option_manage_views import ShopEntryOptionManageView, ShopEntryOptionDetailManageView, ShopEntryOptionDetailImageView
from shop_manage.views.table_manage_views.table_manage_views import ShopTableManageView, ShopTableCreateView
from shop_manage.views.pos_manage_views.pos_manage_views import ShopPosManageView, ShopPosCreateView
from shop_manage.views.goods_manage_views.goods_manage_views import GoodsManageView, GoodsCreateView, GoodsDetailView, GoodsEditView, goods
from shop_manage.views.goods_manage_views.option_manage_views import OptionManageView, OptionDetailManageView
from shop_manage.views.order_manage_views.order_manage_views import OrderManageView, order_complete_sms, order_goods


app_name='shop_manage'
urlpatterns = [
    path('<int:shop_id>/', HomeView.as_view(), name='home'),
    path('<int:shop_id>/main/sales/', shop_main_sales),
    path('<int:shop_id>/main/orders/', shop_main_orders),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='shop_manage:login'), name='logout'),
    path('login/', LoginView.as_view(), name='login'),
    path('denied/', PermissionDeniedView.as_view(), name='denied'),
    path('notfound/', NotFoundView.as_view(), name='notfound'),
    path('user-password-edit/', UserPasswordEditView.as_view(), name='user_password_edit'),

    path('<int:shop_id>/person-type-manage/', PersonTypeManageView.as_view(), name='person_type_manage'),
    path('<int:shop_id>/person-type-create/', PersonTypeCreateView.as_view(), name='person_type_create'),
    path('<int:shop_id>/person-type-detail/<int:pk>/', PersonTypeDetailView.as_view(), name='person_type_detail'),
    path('<int:shop_id>/person-type-edit/<int:pk>/', PersonTypeEditView.as_view(), name='person_type_edit'),
    path('<int:shop_id>/person-type-goods/<int:pk>/', PersonTypeGoodsManageView.as_view(), name='person_type_goods'),
    path('<int:shop_id>/entry-option-manage/', ShopEntryOptionManageView.as_view(), name='entry_option_manage'),
    path('<int:shop_id>/entry-option-detail-manage/', ShopEntryOptionDetailManageView.as_view(), name='entry_option_detail_manage'),
    path('<int:shop_id>/entry-option-detail-image/', ShopEntryOptionDetailImageView.as_view(), name='entry_option_detail_image'),
    

    path('<int:shop_id>/table-manage/', ShopTableManageView.as_view(), name='table_manage'),
    path('<int:shop_id>/table-create/', ShopTableCreateView.as_view(), name='table_create'),

    path('<int:shop_id>/pos-manage/', ShopPosManageView.as_view(), name='pos_manage'),
    path('<int:shop_id>/pos-create/', ShopPosCreateView.as_view(), name='pos_create'),

    path('<int:shop_id>/goods-manage/', GoodsManageView.as_view(), name='goods_manage'),
    path('<int:shop_id>/goods-create/', GoodsCreateView.as_view(), name='goods_create'),
    path('<int:shop_id>/goods-detail/<int:pk>/', GoodsDetailView.as_view(), name='goods_detail'),
    path('<int:shop_id>/goods-edit/<int:pk>/', GoodsEditView.as_view(), name='goods_edit'),
    path('<int:shop_id>/goods/', goods),

    path('<int:shop_id>/option-manage/<int:pk>/', OptionManageView.as_view(), name='option_manage'),
    path('<int:shop_id>/option-detail-manage/', OptionDetailManageView.as_view(), name='option_detail_manage'),

    path('<int:shop_id>/order-manage/', OrderManageView.as_view(), name='order_manage'),
    path('<int:shop_id>/order-complete-sms/', order_complete_sms),
    path('<int:shop_id>/order-goods/<int:order_id>/', order_goods),
]