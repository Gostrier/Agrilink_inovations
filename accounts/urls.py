from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/<str:username>/", views.public_profile_view, name="public_profile"),
    path("community/", views.community_view, name="community"),
]
