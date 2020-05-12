from django.urls import path

from .views import (
    index,
    OrderListView,
    OrderDetailView,
    OrderCreateView,
    OrderUpdateView,
    ImageCreateView,
)
from invent.views import PartListView, OrderPartsListView

app_name = "mtn"

urlpatterns = [

    path('', index, name='index'),

    path('mwo/order-list/', OrderListView.as_view(), name='order-list'),

    path('mwo/order/<int:pk>', OrderDetailView.as_view(), name='order'),

    path('mwo/order/create/', OrderCreateView.as_view(), name='new_order'),

    path('mwo/order/<int:pk>/edit', OrderUpdateView.as_view(),
         name='edit_order'),

    path('mwo/order/<int:pk>/add_part/',
         PartListView.as_view(template_name='invent/use_part.html'),
         name='add_part'),

    path('mwo/order/<int:pk>/delete_part/', OrderPartsListView.as_view(),
         name='delete_part'),

    path('mwo/order/<int:pk>/add_image/',
         ImageCreateView.as_view(), name='image'),

]
