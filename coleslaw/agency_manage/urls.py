from django.urls import path, include
from django.contrib.auth.views import LogoutView
from agency_manage.views.agency_manage_views.auth_views import HomeView, LoginView, PermissionDeniedView, NotFoundView, agency_main_sales, UserPasswordEditView

app_name='agency_manage'
urlpatterns = [
    path('<int:agency_id>/', HomeView.as_view(), name='home'),
    path('<int:agency_id>/main/sales/', agency_main_sales),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='agency_manage:login'), name='logout'),
    path('login/', LoginView.as_view(), name='login'),
    path('denied/', PermissionDeniedView.as_view(), name='denied'),
    path('notfound/', NotFoundView.as_view(), name='notfound'),
    path('user-password-edit/', UserPasswordEditView.as_view(), name='user_password_edit'),
]