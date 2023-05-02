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
]
