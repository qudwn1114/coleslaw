from django.urls import path, include
from api.views.agency_views.agency_views import AgencyDetailView
from api.views.agency_views.agency_shop_views import AgencyShopCategoryListView, AgencyShopListView, ShopMainCategoryListView, ShopGoodsListView, ShopGoodsDetailView
from api.views.agency_views.agency_shop_user_views import AgencyShopUserOrderListView, AgencyShopUserOrderDetailView, ShopOrderCancelView
from api.views.checkout_views.checkout_views import ShopCheckoutView
from api.views.order_views.order_views import ShopOrderCreateView, ShopOrderCompleteView, ShopOrderStatusView, ShopOrderCompleteSmsView, ShopOrderAlertTestView
from api.views.entry_views.shop_entry_views import ShopDetailView, ShopEntryDetailView, ShopEntryQueueCreateView, ShopEntryQueueListView, ShopEntryQueueDetailView, ShopEntryQueueStatusView, ShopEntryCallView, ShopEntryPaymentView, ShopEntryNowView
from api.views.pos_views.table_views import ShopTableListView, ShopTableAssignView, ShopTableExitView, ShopTableManageDetailView, ShopTableDetailView, ShopTableLogoutView, ShopMainPosTidView, ShopTableExitColorView
from api.views.pos_views.pos_views import ShopPosListView, ShopTableAddView, ShopTableUpdateView, ShopTableDeleteView, ShopTableClearView, ShopTableGoodsDiscountView, ShopTableDiscountView, ShopTableDiscountCancelView, ShopTableAdditionalView, ShopTableAdditionalCancelView, ShopTableCheckoutView, ShopPosDetailView
from api.views.pos_views.order_views import ShopPosOrderCreateView, ShopPosCheckoutOrderDetailView, ShopPosOrderCompleteView, ShopPosOrderListView, ShopPosOrderDetailView, ShopPosOrderPaymentCancelView, ShopPosOrderPaymentCashReceiptCompleteView, ShopPosOrderPaymentCashReceiptCancelView
from api.views.pos_views.receipt_views import ShopOrderReceiptView, ShopCloseReceiptView
from api.views.pos_views.member_views import ShopMemberListView, ShopMemberCreateView, ShopMemberDeleteView, ShopMemberCouponListView, ShopMemberCouponCreateView, ShopMemberCouponDeleteView, ShopMemberCouponStatusView, ShopCouponListView, ShopMemberCouponExtensionView
from api.views.pos_views.category_views import ShopPosMainCategoryListView, ShopPosCatgoryFixView
from api.views.pos_views.online_views import ShopOnlineEnterView
from api.views.kiosk_views.order_views import ShopKioskOrderCreateView
from api.views.online_views.online_views import GoodsShopView

app_name='api'
urlpatterns = [
    path('agency/<int:agency_id>/', AgencyDetailView.as_view()),
    path('agency/<int:agency_id>/shop-category-list/', AgencyShopCategoryListView.as_view()),
    path('agency/<int:agency_id>/shop-list/<int:shop_category_id>/', AgencyShopListView.as_view()),
    path('shop/<int:shop_id>/category-list/', ShopMainCategoryListView.as_view()),
    path('shop/<int:shop_id>/goods-list/', ShopGoodsListView.as_view()),
    path('shop/<int:shop_id>/goods/<int:goods_id>/', ShopGoodsDetailView.as_view()),
    path('shop/<int:shop_id>/checkout/', ShopCheckoutView.as_view()),
    path('shop/<int:shop_id>/order/<int:checkout_id>/<str:code>/', ShopOrderCreateView.as_view()),
    path('shop/<int:shop_id>/order-complete/<int:order_id>/<str:code>/', ShopOrderCompleteView.as_view()),
    path('shop/<int:shop_id>/order-status/<int:order_id>/', ShopOrderStatusView.as_view()),
    path('shop/<int:shop_id>/order-complete-sms/<int:order_id>/', ShopOrderCompleteSmsView.as_view()),
    path('shop/<int:shop_id>/alert-test/', ShopOrderAlertTestView.as_view()),
    

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
    path('shop/<int:shop_id>/entry-now/<int:queue_id>/<str:phone>/', ShopEntryNowView.as_view()),

    # 테이블
    path('shop/<int:shop_id>/table-list/', ShopTableListView.as_view()),
    path('shop/<int:shop_id>/table-manage-detail/<str:table_no>/', ShopTableManageDetailView.as_view()),
    path('shop/<int:shop_id>/table-detail/<str:table_no>/', ShopTableDetailView.as_view()),
    path('shop/<int:shop_id>/table-assign/<str:table_no>/', ShopTableAssignView.as_view()),
    path('shop/<int:shop_id>/table-exit/<str:table_no>/', ShopTableExitView.as_view()),
    path('shop/<int:shop_id>/table-exit-color/<str:table_no>/', ShopTableExitColorView.as_view()),
    path('shop/<int:shop_id>/table-logout/<str:table_no>/', ShopTableLogoutView.as_view()),
    path('shop/<int:shop_id>/mainpos-tid/<str:mainpos_id>/', ShopMainPosTidView.as_view()),
    
    # pos
    path('shop/<int:shop_id>/pos-list/', ShopPosListView.as_view()),
    path('shop/<int:shop_id>/pos-detail/', ShopPosDetailView.as_view()),
    path('shop/<int:shop_id>/member-list/', ShopMemberListView.as_view()),
    path('shop/<int:shop_id>/member-create/', ShopMemberCreateView.as_view()),
    path('shop/<int:shop_id>/member-delete/',ShopMemberDeleteView.as_view()),
    path('shop/<int:shop_id>/member/<int:shop_member_id>/coupon-list/', ShopMemberCouponListView.as_view()),
    path('shop/<int:shop_id>/member/<int:shop_member_id>/coupon-create/', ShopMemberCouponCreateView.as_view()),
    path('shop/<int:shop_id>/member/<int:shop_member_id>/coupon-delete/', ShopMemberCouponDeleteView.as_view()),
    path('shop/<int:shop_id>/member/<int:shop_member_id>/coupon-status/', ShopMemberCouponStatusView.as_view()),
    path('shop/<int:shop_id>/member/<int:shop_member_id>/coupon-extension/', ShopMemberCouponExtensionView.as_view()),
    path('shop/<int:shop_id>/coupon-list/', ShopCouponListView.as_view()),

    path('shop/<int:shop_id>/category-list/<str:mainpos_id>/', ShopPosMainCategoryListView.as_view()),
    path('shop/<int:shop_id>/category-fix/<str:mainpos_id>/', ShopPosCatgoryFixView.as_view()),

    path('shop/<int:shop_id>/table/<str:table_no>/add/<str:mainpos_id>/', ShopTableAddView.as_view()),
    path('shop/<int:shop_id>/table/<str:table_no>/update/<str:mainpos_id>/', ShopTableUpdateView.as_view()),
    path('shop/<int:shop_id>/table/<str:table_no>/delete/<str:mainpos_id>/', ShopTableDeleteView.as_view()),
    path('shop/<int:shop_id>/table/<str:table_no>/clear/<str:mainpos_id>/', ShopTableClearView.as_view()),
    path('shop/<int:shop_id>/table/<str:table_no>/goods-discount/<str:mainpos_id>/', ShopTableGoodsDiscountView.as_view()),
    path('shop/<int:shop_id>/table/<str:table_no>/discount/<str:mainpos_id>/', ShopTableDiscountView.as_view()),
    path('shop/<int:shop_id>/table/<str:table_no>/discount-cancel/<str:mainpos_id>/', ShopTableDiscountCancelView.as_view()),
    path('shop/<int:shop_id>/table/<str:table_no>/additional/<str:mainpos_id>/', ShopTableAdditionalView.as_view()),
    path('shop/<int:shop_id>/table/<str:table_no>/additional-cancel/<str:mainpos_id>/', ShopTableAdditionalCancelView.as_view()),

    path('shop/<int:shop_id>/table/<str:table_no>/checkout/<str:mainpos_id>/', ShopTableCheckoutView.as_view()),
    
    path('shop/<int:shop_id>/pos/checkout/order-detail/<int:order_id>/<str:code>/', ShopPosCheckoutOrderDetailView.as_view()),
    path('shop/<int:shop_id>/pos/order-list/', ShopPosOrderListView.as_view()),
    path('shop/<int:shop_id>/pos/order-detail/<int:order_id>/', ShopPosOrderDetailView.as_view()),
    path('shop/<int:shop_id>/pos/order/payment-cancel/<int:order_payment_id>/', ShopPosOrderPaymentCancelView.as_view()),
    path('shop/<int:shop_id>/pos/order/payment-cash-receipt-complete/<int:order_payment_id>/', ShopPosOrderPaymentCashReceiptCompleteView.as_view()),
    path('shop/<int:shop_id>/pos/order/payment-cash-receipt-cancel/<int:order_payment_id>/', ShopPosOrderPaymentCashReceiptCancelView.as_view()),

    path('shop/<int:shop_id>/pos/order/<int:checkout_id>/<str:code>/', ShopPosOrderCreateView.as_view()),
    path('shop/<int:shop_id>/pos/order-complete/<int:order_id>/<str:code>/', ShopPosOrderCompleteView.as_view()),
    path('shop/<int:shop_id>/pos/receipt/<int:order_payment_id>/', ShopOrderReceiptView.as_view()),
    path('shop/<int:shop_id>/pos/close-receipt/', ShopCloseReceiptView.as_view()),
    
    path('shop/<int:shop_id>/pos/online-enter/', ShopOnlineEnterView.as_view()),

    # kiosk
    path('shop/<int:shop_id>/kiosk/order/<int:checkout_id>/<str:code>/', ShopKioskOrderCreateView.as_view()),

    # online
    path('goods/<str:code>/', GoodsShopView.as_view()),
]