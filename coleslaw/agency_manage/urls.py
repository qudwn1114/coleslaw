from django.urls import path, include
from django.contrib.auth.views import LogoutView
from agency_manage.views.agency_manage_views.auth_views import HomeView, LoginView, PermissionDeniedView, NotFoundView, agency_main_sales, agency_sales_report, agency_shop_sales_report, UserPasswordEditView
from agency_manage.views.user_manage_views.user_manage_views import UserManageView, UserCreateView, UserDetailView, UserEditView
from agency_manage.views.shop_manage_views.shop_manage_views import ShopManageView, ShopCreateView, ShopDetailView, ShopEditView
from agency_manage.views.shop_manage_views.shop_admin_manage_views import ShopAdminManageView
from agency_manage.views.sales_report_manage_views.sales_report_manage_views import AgencySalesReportManage
from agency_manage.views.sales_report_manage_views.online_report_manage_views import AgencyOnlineReportManage


app_name='agency_manage'
urlpatterns = [
    path('<int:agency_id>/', HomeView.as_view(), name='home'),
    path('<int:agency_id>/main/sales/', agency_main_sales),
    path('<int:agency_id>/main/report/', agency_sales_report),
    path('<int:agency_id>/main/shop/report/', agency_shop_sales_report),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='agency_manage:login'), name='logout'),
    path('login/', LoginView.as_view(), name='login'),
    path('denied/', PermissionDeniedView.as_view(), name='denied'),
    path('notfound/', NotFoundView.as_view(), name='notfound'),
    path('user-password-edit/', UserPasswordEditView.as_view(), name='user_password_edit'),

    #회원관리
    path('<int:agency_id>/user-manage/', UserManageView.as_view(), name='user_manage'),
    path('<int:agency_id>/user-create/', UserCreateView.as_view(), name='user_create'),
    path('<int:agency_id>/user-detail/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('<int:agency_id>/user-edit/<int:pk>/', UserEditView.as_view(), name='user_edit'),

    #가맹점관리
    path('<int:agency_id>/shop-manage/', ShopManageView.as_view(), name='shop_manage'),
    path('<int:agency_id>/shop-create/', ShopCreateView.as_view(), name='shop_create'),
    path('<int:agency_id>/shop-detail/<int:pk>/', ShopDetailView.as_view(), name='shop_detail'),
    path('<int:agency_id>/shop-edit/<int:pk>/', ShopEditView.as_view(), name='shop_edit'),

    path('<int:agency_id>/shop-admin-manage/<int:pk>/', ShopAdminManageView.as_view(), name='shop_admin_manage'),

    path('<int:agency_id>/sales-report-manage/', AgencySalesReportManage.as_view(), name='sales_report_manage'),
    path('<int:agency_id>/online-report-manage/', AgencyOnlineReportManage.as_view(), name='online_report_manage'),
]