from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_test),
    path('user/create', views.create_user),
    path('user/authenticate', views.authenticate_user),
    path('account/getall', views.get_account_ids),
    path('account/balance', views.get_account_balance),
    path('account/payment/preview', views.get_account_payment_preview),
]
