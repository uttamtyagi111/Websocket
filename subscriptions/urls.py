from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = [
    path("", include(router.urls)),
    path("user-profile/", views.get_user_profile, name="get_user_profile"),
    path("available-plans/", views.get_available_plans, name="get_available_plans"),
    path("choose-plan/", views.choose_plan_view, name="choose_plan_view"),
    path("upgrade-plan/", views.upgrade_plan, name="upgrade_plan"),
    path("verify-upgrade-payment/", views.verify_upgrade_payment, name="verify_upgrade_payment"),
    # path('create-order/', views.create_order, name='create_order'),
    # path('payment-callback/', views.handle_payment_callback, name='handle_payment_callback'),
    path("initiate-payment/", views.initiate_payment, name="initiate_payment"),
    path("verify-payment/", views.verify_payment, name="verify_payment"),
    path("payment-success/", views.payment_success, name="payment_success"),
    path("payment-failed/", views.payment_failed, name="payment_failed"),
    # path('send-invoice/', views.example_view, name='send_invoice'),
]
