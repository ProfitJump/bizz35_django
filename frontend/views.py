from django.shortcuts import render
from dashboard.models import Profile


def index_view(request, *args, **kwargs):
    # track_visitor(request)
    code = str(kwargs.get('ref_code'))
    try:
        profile = Profile.objects.get(referral_id=code)
        request.session['ref_profile'] = profile.user_id
    except:
        pass
    return render(request, 'index.html', {})
