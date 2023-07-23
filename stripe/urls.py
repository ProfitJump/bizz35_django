from django.urls import path
from . import views as stripe_views
from dashboard import views as dashboard_views

urlpatterns = [
    path('create-checkout-session/', stripe_views.create_checkout_session, name='stripe.membership'),
    path('create-checkout-session-boosters/', stripe_views.create_checkout_session_boosters, name='stripe.boosters'),
    path('success/<str:session_id>/', stripe_views.success, name='stripe.success'),
    path('cancelled/', stripe_views.cancelled, name='stripe.cancelled'),
    path('webhook/', stripe_views.stripe_webhook, name='stripe.webhook'),
    path('authorize/', stripe_views.StripeAuthorizeView.as_view(), name='stripe.authorize'),
    path('initial-requirements/', stripe_views.StripeRequirementsView.as_view(), name='stripe.initial_requirements'),
    path('oauth/callback/', stripe_views.StripeAuthorizeCallbackView.as_view(), name='stripe.authorize_callback'),
    path('delete_external_account/<str:account_id>/<str:external_account_id>/', dashboard_views.delete_external_account, name='stripe.delete_external_account'),
    path('update_external_account/<str:account_id>/<str:external_account_id>/', dashboard_views.update_external_account, name='stripe.update_external_account'),
]
