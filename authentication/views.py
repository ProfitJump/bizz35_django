from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import transaction

from .api_twilio.account_verification_email import two_step_email, two_step_email_response
from .models import User
from dashboard.models import Profile as UserProfile
from dashboard.api_referrals.generate_referral import new_referral_id
from stripe.models import Stripe as StripeCustomer
from stripe.views import create_customer as newstripecustomer


# Create your views here.
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # print(username)
        # print(password)

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.POST.get('next', None)
            if next_url:
                return redirect(next_url)
            else:
                return redirect(reverse('dashboard.index'))
        else:
            if username is "":
                messages.error(request, "Please enter a valid username.")
                return redirect('auth.login')

            if password is "":
                messages.error(request, "Please enter a valid password.")
                return redirect('auth.login')

            user = get_user_model()
            if user.objects.filter(is_active=False):
                messages.error(request, "User is not active. Please confirm your email or contact support.")
                return redirect('auth.login')

        messages.error(request, "Your username or password is incorrect. Please try again.")
        return redirect('auth.login')

    return render(request, "auth/login.html")


def register(request):
    if request.method == 'POST':
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        User = get_user_model()

        if User.objects.filter(username=username):
            messages.error(request, "Username already exists in our system! Please try again.")
            return redirect('auth.register')

        if User.objects.filter(email=email):
            messages.error(request, "Email is already in use. Please login or contact support.")
            return redirect('auth.register')

        if len(username) > 25:
            messages.error(request, "Username must be under 25 characters.")
            return redirect('auth.register')

        if not username.isalnum():
            messages.error(request, "Username cannot contain any special characters! Please try again.")
            return redirect('auth.register')

        if password1 != password2:
            messages.error(request, "Passwords do not match! Please try again.")
            return redirect('auth.register')

        with transaction.atomic():
            new_user = User.objects.create_user(username, email, password1)
            new_user.first_name = fname
            new_user.last_name = lname
            new_user.is_active = False

            new_profile = UserProfile.objects.create(user_id=new_user.id)
            new_profile.referral_id = new_referral_id()
            new_profile.membership_level = 'Free User'

            stripe_customer = StripeCustomer.objects.create(user_id=new_user.id)
            stripe_customer.customer_id = newstripecustomer(first_name=fname, last_name=lname, email=email)

            profile_id = request.session.get('ref_profile')
            if profile_id is not None:
                recommended_by_profile = User.objects.get(id=profile_id)
                new_profile.referred_by = recommended_by_profile
            else:
                new_profile.is_booster = True

            new_user.save()
            new_profile.save()
            stripe_customer.save()

        messages.success(request, "Your account had been created. Please verify your email to login.")
        session_email = email
        two_step_email(email=email, name=fname, session_email=session_email)

        return redirect('auth.login')

    return render(request, "auth/register.html")


def register_verify(request, session_email, code):
    s_email = session_email

    two_step_email_response(email=s_email, code=code)
    messages.success(request, "Your email has been activated! You may now login.")

    user = User.objects.get(email=s_email)
    user.is_active = True
    user.save()

    return redirect('auth.login')


def user_logout(request):
    logout(request)
    next_url = request.GET.get('next', None)
    if next_url:
        # remove the 'next' parameter from the URL
        next_url = '/'
    return redirect(next_url or '/')


