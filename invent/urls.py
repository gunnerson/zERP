"""staff URL Configuration

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

from django.urls import path, re_path

from . import views

app_name = "invent"

urlpatterns = [
	# Inventory page
    path('inventory/', views.invent, name='invent'),
    
    # Page for adding new work part
    re_path(r'^inventory/new_part/$', views.new_part, name='new_part'),
	
    # Page for adding new work part
    re_path(r'^inventory/new_vendor/$', views.new_vendor, name='new_vendor'),
	
]