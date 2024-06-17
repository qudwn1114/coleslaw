from django.urls import path, include
from api.views.agency_views.agency_shop_views import AgencyShopListView, ShopMainCategoryListView, ShopGoodsListView, ShopGoodsDetailView

app_name='api'
urlpatterns = [
    path('agency/<int:agency_id>/shop-list/', AgencyShopListView.as_view()),
    path('shop/<int:shop_id>/category-list/', ShopMainCategoryListView.as_view()),
    path('shop/<int:shop_id>/goods-list/', ShopGoodsListView.as_view()),
    path('shop/<int:shop_id>/goods/<int:goods_id>/', ShopGoodsDetailView.as_view()),
]