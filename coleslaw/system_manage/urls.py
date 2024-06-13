from django.urls import path, include

from django.contrib.auth.views import LogoutView
from system_manage.views.system_manage_views.auth_views import HomeView, LoginView, PermissionDeniedView, NotFoundView
from system_manage.views.user_manage_views.user_manage_views import UserManageView, UserCreateView, UserDetailView, UserEditView
from system_manage.views.shop_manage_views.shop_manage_views import ShopManageView, ShopCreateView, ShopDetailView, ShopEditView
from system_manage.views.shop_manage_views.shop_admin_manage_views import ShopAdminManageView
from system_manage.views.category_manage_views.category_manage_views import CategoryManageView, sub_category, category

app_name='system_manage'
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='system_manage:login'), name='logout'),
    path('denied/', PermissionDeniedView.as_view(), name='denied'),
    path('notfound/', NotFoundView.as_view(), name='notfound'),

    #회원관리
    path('user-manage/', UserManageView.as_view(), name='user_manage'),
    path('user-create/', UserCreateView.as_view(), name='user_create'),
    path('user-detail/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('user-edit/<int:pk>/', UserEditView.as_view(), name='user_edit'),

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