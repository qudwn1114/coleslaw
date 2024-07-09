from django.urls import path, include

from django.contrib.auth.views import LogoutView
from system_manage.views.system_manage_views.auth_views import HomeView, LoginView, PermissionDeniedView, NotFoundView, system_main_sales
from system_manage.views.user_manage_views.user_manage_views import UserManageView, UserCreateView, UserDetailView, UserEditView
from system_manage.views.agency_manage_views.agency_manage_views import AgencyManageView, AgencyCreateView, AgencyDetailView, AgencyEditView
from system_manage.views.agency_manage_views.agency_admin_manage_views import AgencyAdminManageView
from system_manage.views.agency_manage_views.agency_shop_manage_views import AgencyShopManageView
from system_manage.views.shop_manage_views.shop_category_manage_views import ShopCategoryManageView, ShopCategoryCreateView, ShopCategoryDetailView, ShopCategoryEditView
from system_manage.views.shop_manage_views.shop_manage_views import ShopManageView, ShopCreateView, ShopDetailView, ShopEditView
from system_manage.views.shop_manage_views.shop_admin_manage_views import ShopAdminManageView
from system_manage.views.category_manage_views.category_manage_views import CategoryManageView, sub_category, category
from system_manage.views.person_type_manage_views.person_type_manage_views import PersonTypeManageView, PersonTypeCreateView, PersonTypeDetailView, PersonTypeEditView

app_name='system_manage'
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('main/sales/', system_main_sales),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='system_manage:login'), name='logout'),
    path('denied/', PermissionDeniedView.as_view(), name='denied'),
    path('notfound/', NotFoundView.as_view(), name='notfound'),

    #회원관리
    path('user-manage/', UserManageView.as_view(), name='user_manage'),
    path('user-create/', UserCreateView.as_view(), name='user_create'),
    path('user-detail/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('user-edit/<int:pk>/', UserEditView.as_view(), name='user_edit'),

    #에이전시관리
    path('agency-manage/', AgencyManageView.as_view(), name='agency_manage'),
    path('agency-create/', AgencyCreateView.as_view(), name='agency_create'),
    path('agency-detail/<int:pk>/', AgencyDetailView.as_view(), name='agency_detail'),
    path('agency-edit/<int:pk>/', AgencyEditView.as_view(), name='agency_edit'),

    path('agency-shop-manage/<int:pk>/', AgencyShopManageView.as_view(), name='agency_shop_manage'),

    path('agency-admin-manage/<int:pk>/', AgencyAdminManageView.as_view(), name='agency_admin_manage'),

    
    #사람타입 관리
    path('person-type-manage/', PersonTypeManageView.as_view(), name='person_type_manage'),
    path('person-type-create/', PersonTypeCreateView.as_view(), name='person_type_create'),
    path('person-type-detail/<int:pk>/', PersonTypeDetailView.as_view(), name='person_type_detail'),
    path('person-type-edit/<int:pk>/', PersonTypeEditView.as_view(), name='person_type_edit'),

    #가맹점카테고리 관리
    path('shop-category-manage/', ShopCategoryManageView.as_view(), name='shop_category_manage'),
    path('shop-category-create/', ShopCategoryCreateView.as_view(), name='shop_category_create'),
    path('shop-category-detail/<int:pk>/', ShopCategoryDetailView.as_view(), name='shop_category_detail'),
    path('shop-category-edit/<int:pk>/', ShopCategoryEditView.as_view(), name='shop_category_edit'),

    #가맹점관리
    path('shop-manage/', ShopManageView.as_view(), name='shop_manage'),
    path('shop-create/', ShopCreateView.as_view(), name='shop_create'),
    path('shop-detail/<int:pk>/', ShopDetailView.as_view(), name='shop_detail'),
    path('shop-edit/<int:pk>/', ShopEditView.as_view(), name='shop_edit'),

    path('shop-admin-manage/<int:pk>/', ShopAdminManageView.as_view(), name='shop_admin_manage'),

    #카테고리관리
    path('category-manage/', CategoryManageView.as_view(), name='category_manage'),
    path('sub-category/', sub_category),
    path('category/', category),
]