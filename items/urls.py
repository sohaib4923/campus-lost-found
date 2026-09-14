from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("add-item/", views.add_item, name="add_item"),
    path("item/<int:item_id>/", views.item_detail, name="item_detail"),
    path("item/<int:item_id>/claim/", views.claim_item, name="claim_item"),
    path("dashboard/", views.dashboard, name="dashboard"),
]