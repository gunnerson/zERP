from django.urls import path

from . import views
from mtn.views import OrderListView, OrderDetailView, OrderCreateView, OrderUpdateView, AddPartView

app_name = "mtn"

urlpatterns = [

    path('', views.index, name='index'),

    path('mwo/order-list/', OrderListView.as_view(), name='order-list'),

    path('mwo/order/<int:pk>', OrderDetailView.as_view(), name='order'),

    path('mwo/create_order/', OrderCreateView.as_view(), name='new_order'),
	
    path('mwo/update_order/<int:pk>/', OrderUpdateView.as_view(), 
		    name='edit_order'),

    path('mwo/order/<int:pk>/add_part/', AddPartView.as_view(), 
            name='add_part'),

    # path('mwo/order/add_part/<int:order_id>', views.add_part, name='add_part'),
]
