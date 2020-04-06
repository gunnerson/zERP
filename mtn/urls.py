from django.urls import path

from . import views
from mtn.views import OrderListView

app_name = "mtn"

urlpatterns = [

    path('', views.index, name='index'),
    
    path('mwo/', views.maint, name='maint'),

    path('mwo/order-list/', OrderListView.as_view(), name='order-list'),

    path('mwo/order/<int:order_id>/', views.order, 
			name='order'),
    
    path('mwo/new_order/', views.new_order, name='new_order'),
	
    path('mwo/edit_order/<int:order_id>/', views.edit_order, 
		    name='edit_order'),
]
