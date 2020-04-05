"""mtn URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path

from . import views

app_name = "mtn"

urlpatterns = [
	# Home page
    path('', views.index, name='index'),
    
    # Maintenance page
    path('maint/', views.maint, name='maint'),
    
    # Show all open work orders
    path('maint/orders/', views.orders, name='orders'),

    # Show all open work orders
    path('maint/closed_orders/', views.closed_orders, 
			name='closed_orders'),
    
    # Detail page for a single work order
    path('maint/orders/<int:order_id>/', views.order, 
			name='order'),
    
    # Page for adding new work orders
    path('maint/new_order/', views.new_order, name='new_order'),
	
    # Page for editing a repair
    path('maint/edit_order/<int:order_id>/', views.edit_order, 
		    name='edit_order'),
]
