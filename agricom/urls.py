"""
URL configuration for learnproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from agricom import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('notes_list/', views.notes_list, name='notes_list'),
    path('notes_upload/', views.notes_upload, name='notes_upload'),
    path("preview_note/<int:pk>/preview_note/", views.preview_note, name="preview_note"),
    path("notes/<int:pk>/download/", views.download_ai_report, name="download_ai_report"),
    path("initiate_payment/", views.initiate_payment, name="initiate_payment"),
    path("mpesa_callback/", views.mpesa_callback, name="mpesa_callback"),
    path("api/mpesa/callback/", views.mpesa_callback, name="mpesa_callback"),
    path('notes/delete/<int:pk>/', views.delete_note, name='delete_note'), 
    path("listings_page/", views.listing_page, name="listing_page"),
    path('listing/<int:listing_id>/order/', views.order_page, name='order_page'),
    path("buyer/<int:listing_id>/available/", views.buyer_available, name="buyer_available"),
    path("buyer/<int:listing_id>/not_available/", views.buyer_not_available, name="buyer_not_available"),
    path('listing/<int:listing_id>/payment/', views.payment_page, name='payment_page'),

    
   

]
