from django.utils.translation import ugettext as _
from django.utils import timezone
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import pytz
from . models import User
from . forms import EditProfileForm


@login_required
def editAction(request):
    user = User.objects.get(login=request.user.username)

    if request.method == 'POST':
        form = EditProfileForm(request.POST)
        if form.is_valid():
            e = form.cleaned_data['email']
            request.user.email = e
            request.user.save()
            user.email = e
            user.timezone = form.cleaned_data['timezone']
            user.save()
            request.session['django_timezone'] = user.timezone
            messages.info(request, _('Your Profile has been updated successfully'))
        else:
            messages.error(request, _('Invalid Form Values'))
    else:
        form = EditProfileForm(initial={'email': user.email, 'timezone': user.timezone})

    context = {
        'form': form,
        'menu_profile': 'active',
        'timezones': pytz.common_timezones,
    }
    return render(request, 'users/profile.html', context)