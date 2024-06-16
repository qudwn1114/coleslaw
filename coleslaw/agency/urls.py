from django.urls import path, include
from agency.views import AgencyHomeView, AgencyShopListView, AgencyShopView, AgencyBasketView, AgencyShopCheckoutView, AgencyShopOrderCompleteView

app_name='agency'
urlpatterns = [
    path('<int:agency_id>/', AgencyHomeView.as_view(), name='home'),
    path('<int:agency_id>/shop-list/', AgencyShopListView.as_view(), name='agency_shop_list'),
    path('shop/<int:agency_shop_id>/', AgencyShopView.as_view(), name='agency_shop'),
    path('<int:agency_id>/basket/', AgencyBasketView.as_view(), name='agency_shop_basket'),
    path('checkout/<int:agency_shop_id>/<str:code>/', AgencyShopCheckoutView.as_view(), name='agency_shop_checkout'),
    path('order-complete/<int:agency_shop_id>/<int:order_id>/', AgencyShopOrderCompleteView.as_view(), name='agency_shop_order_complete'),
]