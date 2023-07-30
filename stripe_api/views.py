from django.shortcuts import render

# Create your views here.
# Import django base settings
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.conf import settings
from django.http.response import JsonResponse, HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.urls import reverse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

# Import models from dashboard and stripe_api apps and give them a reference name.
from dashboard.models import Profile as UserProfile
from stripe_api.models import Stripe as StripeProfile

from dashboard.views import add_ledger_entry

# Import stripe_api api client to work with the stripe_api API. The stripe_api API key is set via the django settings module, but held in the .env
# file at the top level directory. To update the key update the .env file not the django settings file.
import stripe
import time
import os
import urllib
import json
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = settings.STRIPE_SECRET_KEY


# When a new user signs up this creates the customer account via the stipe API. The function then returns the new customer's account ID
def create_customer(first_name, last_name, email):
    # Use the Stripe API to create a new customer
    name = f'{first_name} {last_name}'
    customer = stripe.Customer.create(
        name=name,
        email=email
    )
    # Return the new customer ID
    return customer.id


# Create a new checkout session. The session is tied to the user class for the authenticated user. When the user hits the checkout screen,
# it will have the email pre-set and cannot be changed. The charge then links it to the product "Life Time Membership".
@csrf_exempt
def create_checkout_session(request):
    if request.method == 'GET':
        # set the domain name to use in call backs.
        domain_url = settings.STRIPE_DOMAIN
        # set the API key in .env files.
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            # Get the current user id from the request method.
            user_id = request.user.id
            # Get the current user model and load it up.
            User = get_user_model()
            # Get the current user using the id from the request object.
            user = User.objects.get(id=user_id)
            # Get the and link the object from the Stipe model in the stripe_api model.py file ane return the stored stripe_api customer ID to pass
            # into the checkout creation.
            get_customer_id = StripeProfile.objects.get(user_id=user_id)
            strip_id = get_customer_id.customer_id

            # Begin the checkout session for stripe_api.
            checkout_session = stripe.checkout.Session.create(
                # pass the current user.id through to stripe_api to connect the two systems together using client_reference_id. If user.id is
                # none then none will be passes.
                client_reference_id=request.user.id if request.user.is_authenticated else None,
                # This is the URL that will be sent upon a checkout success status.
                success_url=domain_url + 'stripe_api/success/{CHECKOUT_SESSION_ID}',
                # This is the URL if the cancel the checkout process, either they leave the page, or they hit the back button. It will
                # return them to the site using this URL.
                cancel_url=domain_url + 'stripe_api/cancelled/',
                # Stripe payment method types.
                payment_method_types=['card'],
                customer=strip_id,
                phone_number_collection={
                    'enabled': True,
                },
                mode='payment',
                line_items=[
                    {
                        'quantity': os.getenv("STRIPE_MEMBERSHIP_QTY"),
                        'price': os.getenv("STRIPE_MEMBERSHIP_PRICE"),
                    }
                ],
                metadata={
                    "product_id": os.getenv('STRIPE_MEMBERSHIP'),  # Add any additional metadata as needed
                    # Add more metadata key-value pairs as required
                },
            )
            session = checkout_session['url']
            return redirect(session)
        except Exception as e:
            return JsonResponse({'error': str(e)})


@csrf_exempt
def create_checkout_session_boosters(request):
    if request.method == 'GET':
        # set the domain name to use in call backs.
        domain_url = settings.STRIPE_DOMAIN
        # set the API key in .env files.
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            # Get the current user id from the request method.
            user_id = request.user.id
            # Get the current user model and load it up.
            User = get_user_model()
            # Get the current user using the id from the request object.
            user = User.objects.get(id=user_id)
            # Get the and link the object from the Stipe model in the store model.py file ane return the stored strip customer ID to pass
            # into the checkout creation.
            get_customer_id = StripeProfile.objects.get(user_id=user_id)
            strip_id = get_customer_id.customer_id

            # Begin the checkout session for stripe_api.
            checkout_session = stripe.checkout.Session.create(
                # pass the current user.id through to stripe_api to connect the two systems together using client_reference_id. If user.id is
                # none then none will be passes.
                client_reference_id=request.user.id if request.user.is_authenticated else None,
                # This is the URL that will be sent upon a checkout success status.
                success_url=domain_url + 'stripe_api/success/{CHECKOUT_SESSION_ID}',
                # This is the URL if the cancel the checkout process, either they leave the page, or they hit the back button. It will
                # return them to the site using this URL.
                cancel_url=domain_url + 'stripe_api/cancelled/',
                # Stripe payment method types.
                payment_method_types=['card'],
                customer=strip_id,
                phone_number_collection={
                    'enabled': True,
                },
                mode='payment',
                line_items=[
                    {
                        'quantity': os.getenv("STRIPE_BOOSTERS_QTY"),
                        "adjustable_quantity": {"enabled": True, "minimum": os.getenv("STRIPE_BOOSTERS_MIN"), "maximum": os.getenv("STRIPE_BOOSTERS_MAX")},
                        'price': os.getenv("STRIPE_BOOSTERS_PRICE"),
                    }
                ],
            )
            session = checkout_session['url']
            return redirect(session)
        except Exception as e:
            return JsonResponse({'error': str(e)})


@csrf_exempt
def success(request, *args, **kwargs):
    messages.success(request, 'Your checkout session is complete.')
    return redirect('dashboard.index')


@csrf_exempt
def cancelled(request, *args, **kwargs):
    return redirect('dashboard.index')


@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        print("Stripe Webhook Value Error")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        print("Stripe Sig Error")
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        print("Checkout Session Completed")
        session_id = event.data.object['id']
        line_items = stripe.checkout.Session.list_line_items(session_id)
        checkout_type = line_items.data[0]['price']['product']

        if checkout_type == os.getenv("STRIPE_MEMBERSHIP"):
            print('Membership Bought')
            client_id = event.data.object['client_reference_id']
            User = get_user_model()
            user = User.objects.get(id=client_id)
            get_profile = UserProfile.objects.get(user_id=user)
            get_profile.membership_level = 'Paid Customer'
            get_profile.phone = event.data.object.customer_details.phone
            get_profile.save()

            if not get_profile.is_booster:
                commission_owner = user.profile.commission_owner
                commission_matrix = commission_owner.profile.matrix_level

                print('User signing up is', user)
                print('Commission Owner:', commission_owner)
                print('Commission Owner Matrix:', commission_matrix)

                if commission_matrix <= 1:
                    print('Logic Hit Main Statement. Matrix <=1.')
                    add_ledger_entry(request, user=user, des=f'Lifetime Membership Signup - {user.first_name} {user.last_name}', debit=39, credit=0, ledger='Blue', is_public=False)
                    time.sleep(1)
                    add_ledger_entry(request, user=user, des="Stripe Processing Fee", debit=0, credit=1.43, ledger='Blue', is_public=False)
                    time.sleep(1)
                    add_ledger_entry(request, user=user, des=f'Coded Transfer to {commission_owner.first_name} {commission_owner.last_name}', debit=0, credit=37, ledger='Blue', is_public=False)
                    time.sleep(1)
                    add_ledger_entry(request, user=commission_owner, des=f'Membership Credited', debit=37, credit=0, ledger='SportsPro', is_public=True)

                    commission_owner.profile.matrix_level = commission_owner.profile.matrix_level + 1
                    commission_owner.profile.save()

                    if commission_matrix == 1:
                        commission_owner.profile.membership_level = 'Level 1 Affiliate'
                        commission_owner.profile.save()
                    else:
                        commission_owner.profile.membership_level = 'Level 2 Affiliate'
                        commission_owner.profile.save()
                else:
                    print('Logic Hit Else Statement. Matrix >=2.')
                    add_ledger_entry(request, user=user, des=f'Lifetime Membership Signup - {user.first_name} {user.last_name}', debit=39, credit=0, ledger='Blue', is_public=False)
                    time.sleep(1)
                    add_ledger_entry(request, user=user, des="Stripe Processing Fee", debit=0, credit=1.43, ledger='Blue', is_public=False)
                    time.sleep(1)
                    add_ledger_entry(request, user=user, des=f'Coded Transfer to {commission_owner.first_name} {commission_owner.last_name}', debit=0, credit=37, ledger='Blue', is_public=False)
                    time.sleep(1)
                    add_ledger_entry(request, user=commission_owner, des=f'Membership Credited', debit=37, credit=0, ledger='SportsPro', is_public=True)

                    commission_owner.profile.matrix_level = commission_owner.profile.matrix_level + 1
                    commission_owner.profile.save()

                    if commission_matrix == 3:
                        commission_owner.profile.membership_level = 'Level 3 Affiliate'
                        commission_owner.profile.boosters = commission_owner.profile.boosters + 2
                        commission_owner.profile.save()
                        print("Added 2 Boosters")

                    if commission_matrix == 6:
                        commission_owner.profile.boosters = commission_owner.profile.boosters + 4
                        commission_owner.profile.save()
                        print("Added 4 Boosters")

                # print("DEBUG1 = HttpResponse(status=200)")
                # return HttpResponse(status=200)
            else:
                print('Hit Pass Statement')
                pass

        else:
            client_id = event.data.object['client_reference_id']
            print('Booster Bought')
            booster_qty = line_items.data[0]['quantity']
            print(booster_qty)

            User = get_user_model()
            user = User.objects.get(id=client_id)
            get_profile = UserProfile.objects.get(user_id=user)
            get_profile.boosters += booster_qty
            get_profile.save()

    print("DEBUG2 = HttpResponse(status=200)")
    response_data = {
        "status": "success",
        "message": "Webhook processed successfully."
    }
    response_json = json.dumps(response_data)
    return HttpResponse(response_json, content_type='application/json', status=200)


class StripeAuthorizeView(View):
    def get(self, request):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('auth.login'))

        # Create a custom account
        try:
            account = stripe.Account.create(
                type='custom',
                country='US',
                email=request.user.email,
                business_type='individual',
                business_profile={"url": "https://bizz35.com"},
                capabilities={
                    'transfers': {'requested': True},
                    'tax_reporting_us_1099_misc': {'requested': True}
                },
                settings={
                    "payouts": {
                        "debit_negative_balances": True,
                        "schedule": {"interval": "manual"}
                    }
                },

            )
            account_id = account.id
            print(f"Account created with ID {account_id}")
            print(account)
            get_customer_id = StripeProfile.objects.get(user_id=request.user.id)
            get_customer_id.connect_id = account_id
            get_customer_id.save()
        except stripe.error.StripeError as e:
            # Handle the error here
            print(f"Error creating account: {e}")
            pass

        # Generate an account link for the user to complete onboarding
        domain_url = settings.STRIPE_DOMAIN
        url = domain_url + 'stripe_api/oauth/callback'
        try:
            account_link = stripe.AccountLink.create(
                account=account_id,
                refresh_url=domain_url + 'stripe_api/oauth/callback',
                return_url=domain_url + 'stripe_api/oauth/callback',
                type='custom_account_verification',
                collect="eventually_due",
            )
            url = account_link.url

        except stripe.error.StripeError as e:
            # Handle the error here
            pass

        return redirect(url)


class StripeAuthorizeCallbackView(View):
    def get(self, request):
        code = request.GET.get('code')
        print('code:', code)
        if code:
            data = stripe.OAuth.token(
                grant_type="authorization_code",
                code=code,
                client_id=settings.STRIPE_CONNECT_CLIENT_ID,
                refresh_token=None,
            )
            url = 'https://connect.stripe.com/express/oauth/token'

            user_id = request.user.id
            print(user_id)
            stripe_connect_id = data['stripe_user_id']
            print(stripe_connect_id)
            access_token = data['access_token']
            refresh_token = data['refresh_token']

            stripe.Account.modify(
                stripe_connect_id,
                settings={"payouts": {"schedule": {"interval": "manual"}}},
            )

            print('Connect ID:', stripe_connect_id)
            print('Token:', access_token)

            account = stripe.Account.retrieve(stripe_connect_id)
            print('Payouts Enabled:', account['payouts_enabled'])

        url = reverse('dashboard.index')
        response = redirect(url)
        return response


class StripeRequirementsView(View):
    def get(self, request):
        url = 'https://bizz35.com/stripe_api/oauth/callback'
        get_customer_id = StripeProfile.objects.get(user_id=request.user.id)
        account_id = get_customer_id.connect_id

        try:
            account_link = stripe.AccountLink.create(
                account=account_id,
                refresh_url='https://bizz35.com/stripe_api/oauth/callback',
                return_url='https://bizz35.cfom/stripe_api/oauth/callback',
                type='custom_account_verification',
                collect="eventually_due",
            )
            url = account_link.url

        except stripe.error.StripeError as e:
            # Handle the error here
            pass

        return redirect(url)


def transfer_funds(amount, currency, destination_account_id):
    try:
        transfer = stripe.Transfer.create(
            amount=amount,
            currency=currency,
            destination=destination_account_id
        )
        return transfer
    except stripe.error.InvalidRequestError as e:
        # Handle any errors that occur during the transfer
        print("Transfer failed:", e)


def payment_history(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    customer_id = 'cus_Nad0LvTTcJB0iC'
    payment_intents = stripe.PaymentIntent.list(customer=customer_id)
    payment_methods = stripe.PaymentMethod.list(customer=customer_id)
    charges = stripe.Charge.list(customer=customer_id)
    # print("Payment Intent:", payment_intents)
    # print("Payment Methods:", payment_intents)
    # print("Payment Charges:", charges)
    # for payment_intent in payment_intents:
    #     status = payment_intent["status"]
    #     amount = payment_intent["amount"] / 100  # Divide by 100 to get the amount in dollars (assuming currency is USD)
    #     print(f"Payment Status: {status}, Amount Charged: ${amount}")
    for charge in charges.data:
        status = charge.status
        amount = charge.amount / 100  # Divide by 100 to get the amount in dollars (assuming currency is USD)
        outcome = charge.outcome.seller_message
        last4 = charge.payment_method_details.card.last4
        print(f"Charge Status: {status}, Amount Charged: ${amount}, Last4: {last4}, Outcome: {outcome}")
    pass
