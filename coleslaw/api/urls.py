from django.urls import path, include
from api.views.agency_views.agency_shop_views import AgencyShopListView

app_name='api'
urlpatterns = [
    path('agency/<int:agency_id>/shop-list/', AgencyShopListView.as_view()),
]