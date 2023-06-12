from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_test),
    path('user/create', views.create_user),
    path('user/authenticate', views.authenticate_user),
    path('account/getall', views.get_account_ids),
    path('account/balance', views.get_account_balance),
    path('account/info', views.get_account_info),
    path('account/info/edit', views.edit_account_info),
    path('account/payment/preview', views.get_account_payment_preview),
    path('account/bankcard', views.get_account_bank_card),
    path('account/bankcard/delete', views.delete_account_bank_card),
    path('account/bankcard/add', views.add_account_bank_card),
    path('account/payment/temp/create', views.create_temp_payment),
    path('account/payment/temp/renewal', views.renewal_temp_payment),
    path('account/payment/temp/getpayee', views.get_temp_payment_peyee),
    path('account/payment/temp/lock', views.lock_temp_payment),
    path('account/payment/create', views.create_payment),
]
