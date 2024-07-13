from django.urls import path, include
from api.views.agency_views.agency_shop_views import AgencyShopCategoryListView, AgencyShopListView, ShopMainCategoryListView, ShopGoodsListView, ShopGoodsDetailView
from api.views.agency_views.agency_shop_user_views import AgencyShopUserOrderListView, AgencyShopUserOrderDetailView, ShopOrderCancelView
from api.views.checkout_views.checkout_views import ShopCheckoutView
from api.views.order_views.order_views import ShopOrderCreateView, ShopOrderCompleteView

from api.views.entry_views.shop_entry_views import ShopDetailView, ShopEntryDetailView, ShopEntryQueueCreateView, ShopEntryQueueListView, ShopEntryQueueDetailView, ShopEntryQueueStatusView, ShopEntryCallView, ShopEntryPaymentView
from api.views.pos_views.table_views import ShopTableListView, ShopTableAssignView, ShopTableExitView, ShopTableDetailView
from api.views.pos_views.pos_views import ShopTableAddView, ShopTableUpdateView, ShopTableDeleteView, ShopTableClearView
from api.views.pos_views.member_views import ShopMemberListView, ShopMemberCreateView

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
    path('shop/<int:shop_id>/entry-queue-list/', ShopEntryQueueListView.as_view()),
    path('shop/<int:shop_id>/entry-queue/<int:pk>/', ShopEntryQueueDetailView.as_view()),
    path('shop/<int:shop_id>/entry-queue-status/<int:pk>/', ShopEntryQueueStatusView.as_view()),
    path('shop/<int:shop_id>/entry-call/<int:pk>/', ShopEntryCallView.as_view()),
    path('shop/<int:shop_id>/entry-payment/<int:pk>/', ShopEntryPaymentView.as_view()),

    # 테이블
    path('shop/<int:shop_id>/table-list/', ShopTableListView.as_view()),
    path('shop/<int:shop_id>/table-detail/<int:table_no>/', ShopTableDetailView.as_view()),
    path('shop/<int:shop_id>/table-assign/<int:table_no>/', ShopTableAssignView.as_view()),
    path('shop/<int:shop_id>/table-exit/<int:table_no>/', ShopTableExitView.as_view()),
    
    # pos
    path('shop/<int:shop_id>/member-list/', ShopMemberListView.as_view()),
    path('shop/<int:shop_id>/member-create/', ShopMemberCreateView.as_view()),
    path('shop/<int:shop_id>/table/<int:table_no>/add/', ShopTableAddView.as_view()),
    path('shop/<int:shop_id>/table/<int:table_no>/update/', ShopTableUpdateView.as_view()),
    path('shop/<int:shop_id>/table/<int:table_no>/delete/', ShopTableDeleteView.as_view()),
    path('shop/<int:shop_id>/table/<int:table_no>/clear/', ShopTableClearView.as_view()),
]