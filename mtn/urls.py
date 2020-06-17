from django.urls import path

from .views import (
    index,
    OrderListView,
    OrderDetailView,
    OrderCreateView,
    OrderUpdateView,
    ImageCreateView,
    load_locales,
    repair_toggle,
    create_pms,
    PmListView,
    PmUpdateView,

)
from invent.views import PartListView, OrderPartsListView, import_parts

app_name = "mtn"

urlpatterns = [
    path('', index, name='index'),
    path('mwo/order-list/', OrderListView.as_view(), name='order-list'),
    path('mwo/order/<int:pk>/', OrderDetailView.as_view(), name='order'),
    path('mwo/order/create/<int:pk>/', OrderCreateView.as_view(),
         name='new_order'),
    path('mwo/order/create/', OrderCreateView.as_view(), name='new_order'),
    path('ajax/mwo/order/create/', load_locales, name='ajax_new_order'),
    path('mwo/order/<int:pk>/edit/', OrderUpdateView.as_view(),
         name='edit_order'),
    path('mwo/order/<int:pk>/add_part/',
         PartListView.as_view(template_name='invent/use_part.html'),
         name='add_part'),
    path('mwo/order/<int:pk>/update-parts/', OrderPartsListView.as_view(),
         name='update_parts'),
    path('mwo/order/<int:pk>/add_image/',
         ImageCreateView.as_view(), name='image'),
    path('mwo/order-list/toggle/<int:pk>/<slug:func>/', repair_toggle,
         name='repair_toggle'),
    path('mwo/pm/bulk-create/', create_pms, name='create-pms'),
    path('mwo/pm-list/', PmListView.as_view(), name='pm-list'),
    path('mwo/pm/<int:pk>/', PmUpdateView.as_view(), name='edit_pm'),
    path('mwo/pm/<int:pk>/add_part/',
         PartListView.as_view(template_name='invent/use_part.html'),
         name='add_pm_part'),
    path('mwo/pm/<int:pk>/import-parts/', import_parts, name='import_parts'),
    path('mwo/pm/<int:pk>/update-parts/', OrderPartsListView.as_view(),
         name='update_pm_parts'),
]
