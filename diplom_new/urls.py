"""diplom_new URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include

from backend.views import PartnerUpdate, ApiRoot, ProductInfoList, ProductInfoDetail
from users.views import RegisterUserView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth', include('rest_framework.urls')),
    path('signup/', RegisterUserView.as_view(), name='signup'),
    path('partner-update/', PartnerUpdate.as_view(), name=PartnerUpdate.name),
    path('products/', ProductInfoList.as_view(), name=ProductInfoList.name),
    path('products/<pk>/', ProductInfoDetail.as_view(), name=ProductInfoDetail.name),
    path('', ApiRoot.as_view(), name=ApiRoot.name),
]
