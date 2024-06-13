from django.urls import path, include

from django.contrib.auth.views import LogoutView
from shop_manage.views.shop_manage_views.auth_views import HomeView, LoginView, PermissionDeniedView, NotFoundView
from shop_manage.views.goods_manage.goods_manage_views import GoodsManageView, GoodsCreateView, GoodsDetailView, GoodsEditView, goods


app_name='shop_manage'
urlpatterns = [
    path('<int:shop_id>/', HomeView.as_view(), name='home'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='shop_manage:login'), name='logout'),
    path('denied/', PermissionDeniedView.as_view(), name='denied'),
    path('notfound/', NotFoundView.as_view(), name='notfound'),

    path('<int:shop_id>/goods-manage/', GoodsManageView.as_view(), name='goods_manage'),
    path('<int:shop_id>/goods-create/', GoodsCreateView.as_view(), name='goods_create'),
    path('<int:shop_id>/goods-detail/<int:pk>/', GoodsDetailView.as_view(), name='goods_detail'),
    path('<int:shop_id>/goods-edit/<int:pk>/', GoodsEditView.as_view(), name='goods_edit'),
    path('<int:shop_id>/goods/', goods),

]