from django.urls import path, include
from api.views.agency_views.agency_shop_views import AgencyShopCategoryListView, AgencyShopListView, ShopMainCategoryListView, ShopGoodsListView, ShopGoodsDetailView
from api.views.agency_views.agency_shop_user_views import AgencyShopUserOrderListView, AgencyShopUserOrderDetailView, ShopOrderCancelView
from api.views.checkout_views.checkout_views import ShopCheckoutView
from api.views.order_views.order_views import ShopOrderCreateView, ShopOrderCompleteView

from api.views.entry_views.shop_entry_views import ShopDetailView, ShopEntryDetailView, ShopEntryQueueCreateView

app_name='api'
urlpatterns = [
    path('agency/<int:agency_id>/shop-category-list/', AgencyShopCategoryListView.as_view()),
    path('agency/<int:agency_id>/shop-list/<int:shop_category_id>/', AgencyShopListView.as_view()),
    path('shop/<int:shop_id>/category-list/', ShopMainCategoryListView.as_view()),
    path('shop/<int:shop_id>/goods-list/', ShopGoodsListView.as_view()),
    path('shop/<int:shop_id>/goods/<int:goods_id>/', ShopGoodsDetailView.as_view()),
    path('shop/<int:shop_id>/checkout/', ShopCheckoutView.as_view()),
    path('shop/<int:shop_id>/order/<int:checkout_id>/<str:code>/', ShopOrderCreateView.as_view()),
    path('shop/<int:shop_id>/order-complete/<int:order_id>/<str:code>/', ShopOrderCompleteView.as_view()),

    path('agency/<int:agency_id>/user-order-list/', AgencyShopUserOrderListView.as_view()),
    path('agency/<int:agency_id>/user-order/<int:order_id>/', AgencyShopUserOrderDetailView.as_view()),
    path('shop/<int:shop_id>/order-cancel/<int:order_id>/', ShopOrderCancelView.as_view()),

    # 입장처리
    path('shop/<int:shop_id>/', ShopDetailView.as_view()),
    path('shop/<int:shop_id>/entry/', ShopEntryDetailView.as_view()),
    path('shop/<int:shop_id>/entry-queue-create/', ShopEntryQueueCreateView.as_view()),
]