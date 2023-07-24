from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.sites.models import Site

from django.conf import settings
import stripe_api

from dashboard.models import Profile, LedgerEntry
from stripe_api.models import Stripe as StripeProfile

stripe_api.api_key = settings.STRIPE_SECRET_KEY


@login_required
def index(request):
    taxable_balance = LedgerEntry.objects.filter(user=request.user, is_public=True, ledger_name='SportsPro').aggregate(Sum('debit'))['debit__sum']
    wallet = LedgerEntry.objects.filter(user=request.user, ledger_name='eWallet').aggregate(balance=Sum('debit') - Sum('credit'))['balance']
    context = {
        'balance': taxable_balance,
        'wallet': wallet,
    }
    return render(request, "profile.html", context)


@login_required
def settings():
    pass


@login_required
def security():
    pass


@login_required
def ewallet(request):
    try:
        if request.method == 'POST' and request.POST.get("form_name") == "new_external_card_form":
            card_name = request.POST.get('card_name')
            card_number = request.POST.get('card_number')
            card_expiry_month = request.POST.get('card_expiry_month')
            card_expiry_year = request.POST.get('card_expiry_year')
            card_cvv = request.POST.get('card_cvv')

            get_user = StripeProfile.objects.get(user_id=request.user.id)
            account_id = get_user.connect_id

            token = stripe_api.Token.create(
                card={
                    "number": card_number,
                    "exp_month": card_expiry_month,
                    "exp_year": card_expiry_year,
                    "cvc": card_cvv,
                    "name": card_name,
                    "currency": "usd",
                },
            ).id

            # Create external account
            stripe_api.Account.create_external_account(
                account_id,
                external_account=token,
                stripe_account=account_id,
            )

            # Success message
            message = "Your card was successfully added!"
            response = {'message': message}
            return JsonResponse(response)

        if request.method == 'POST' and request.POST.get("form_name") == "new_external_bank_form":
            account_name = request.POST.get('account_name')
            routing_number = request.POST.get('routing_number')
            account_number = request.POST.get('account_number')

            get_user = StripeProfile.objects.get(user_id=request.user.id)
            account_id = get_user.connect_id

            token = stripe_api.Token.create(
                bank_account={
                    "country": "US",
                    "currency": "usd",
                    "account_holder_name": account_name,
                    "account_holder_type": "individual",
                    "routing_number": routing_number,
                    "account_number": account_number,
                },
            ).id

            # Create external account
            stripe_api.Account.create_external_account(
                account_id,
                external_account=token,
                stripe_account=account_id,
            )

            # Success message
            message = "Your bank account was successfully added!"
            response = {'message': message}
            return JsonResponse(response)

    except stripe_api.error.CardError as e:
        message = str(e.user_message)
        response = {'message': message}
        print('ERROR', message)
        return JsonResponse(response, status=400)

    except stripe_api.error.StripeError as e:
        message = str(e.user_message)
        response = {'message': message}
        print('ERROR', message)
        return JsonResponse(response, status=400)

    except Exception as e:
        message = str(e.user_message) if hasattr(e, 'user_message') else str(e)
        response = {'message': message}
        print('ERROR:', type(e))
        return JsonResponse(response, status=400)

    if request.method == 'GET':
        get_user = StripeProfile.objects.get(user_id=request.user.id)
        account_id = get_user.connect_id

        if account_id is not None and account_id != '':
            account = stripe_api.Account.retrieve(account_id)
            disabled_status = account.requirements.disabled_reason
            kyc_items = account.requirements.currently_due

            if len(kyc_items) > 0:
                get_user.disabled = True
                get_user.save()
                kyc_items = get_user.disabled
            else:
                get_user.disabled = False
                get_user.save()
                kyc_items = get_user.disabled

            external_card_accounts = stripe_api.Account.list_external_accounts(
                account_id,
                limit=100  # The maximum number of external accounts to retrieve (default is 10)
            )

            card_accounts = [account for account in external_card_accounts.auto_paging_iter() if account.object == 'card']
            bank_accounts = [account for account in external_card_accounts.auto_paging_iter() if account.object == 'bank_account']

            context = {
                'card_accounts': card_accounts,
                'bank_accounts': bank_accounts,
                'account_disabled': disabled_status,
                'kyc_items': kyc_items,
            }

            return render(request, "ewallet.html", context)
        else:
            return render(request, "ewallet.html")


@login_required
def statements():
    pass


@login_required
def referrals(request):
    profile = Profile.objects.get(user=request.user)
    referred_user_list = profile.get_recommended_profiles()
    signed_up_count = profile.get_recommended_count()
    paid_signed_up_count = profile.get_recommended_paid_count()
    taxable_balance = LedgerEntry.objects.filter(user=request.user, is_public=True, ledger_name='SportsPro').aggregate(Sum('debit'))['debit__sum']
    if request.is_secure():
        protocol = 'https'
    else:
        protocol = 'http'
    current_site = Site.objects.get_current(request)
    absolute_url = f"{protocol}://{current_site}/"

    wallet = LedgerEntry.objects.filter(user=request.user, ledger_name='eWallet').aggregate(balance=Sum('debit') - Sum('credit'))['balance']

    context = {
        'referred_user': referred_user_list,
        'count': signed_up_count,
        'paid_count': paid_signed_up_count,
        'domain': absolute_url,
        'balance': taxable_balance,
        'wallet': wallet,
    }

    return render(request, "referrals.html", context)


@login_required
def logs(request):
    user_ledger = LedgerEntry.objects.filter(user=request.user).order_by('timestamp')
    user_balance = 0
    for entry in user_ledger:
        user_balance += entry.debit - entry.credit
        entry.user_balance = user_balance
        entry.save()
    user_ledger = LedgerEntry.objects.filter(user=request.user).order_by('-timestamp')

    context = {
        'entries': user_ledger,
    }

    return render(request, "logs.html", context)


@login_required
def sports_ledger(request):
    user_ledger = LedgerEntry.objects.filter(user=request.user).order_by('timestamp')
    user_balance = 0
    for entry in user_ledger:
        user_balance += entry.debit - entry.credit
        entry.user_balance = user_balance
        entry.save()
    user_ledger = LedgerEntry.objects.filter(user=request.user).order_by('-timestamp')

    blue_ledger = LedgerEntry.objects.filter(ledger_name='Blue').order_by('timestamp')
    blue_balance = 0
    for entry in blue_ledger:
        blue_balance += entry.debit - entry.credit
        entry.blue_balance = blue_balance
        entry.save()
    blue_ledger = LedgerEntry.objects.filter(ledger_name='Blue').order_by('-timestamp')

    boosters_ledger = LedgerEntry.objects.filter(ledger_name='Boosters').order_by('timestamp')
    boosters_balance = 0
    for entry in boosters_ledger:
        boosters_balance += entry.debit - entry.credit
        entry.boosters_balance = boosters_balance
        entry.save()
    boosters_ledger = LedgerEntry.objects.filter(ledger_name='Boosters').order_by('-timestamp')

    full_ledger = LedgerEntry.objects.all()
    total_balance = 0
    for entry in full_ledger:
        total_balance += entry.debit - entry.credit
        entry.master_balance = total_balance
        entry.save()
    full_ledger = LedgerEntry.objects.all().order_by('-timestamp')

    return render(request, 'ledger.html', {'entries': user_ledger, 'full': full_ledger, 'blue': blue_ledger, 'boosters': boosters_ledger})


def add_ledger_entry(request, user, des, debit, credit, ledger, is_public):
    user_id = user
    description = des
    debit = debit
    credit = credit
    ledger_name = ledger

    update_ledger = LedgerEntry.objects.create(user=user_id)
    update_ledger.description = description
    update_ledger.debit = debit
    update_ledger.credit = credit
    update_ledger.ledger_name = ledger_name
    update_ledger.is_public = is_public
    update_ledger.save()


def delete_external_account(request, account_id, external_account_id):
    try:
        stripe_api.Account.delete_external_account(
            account_id,
            external_account_id
        )
        return JsonResponse({'success': True})

    except stripe_api.error.InvalidRequestError as e:
        return JsonResponse({'error': str(e)})


def update_external_account(request, account_id, external_account_id):
    try:
        stripe_api.Account.modify_external_account(
            account_id,
            external_account_id,
            default_for_currency=True,
        )
        return JsonResponse({'success': True})

    except stripe_api.error.InvalidRequestError as e:
        return JsonResponse({'error': str(e)})
