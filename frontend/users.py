from django.utils.translation import ugettext as _
from django.utils import timezone
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import pytz
import json
from . models import User, Command, Controller
from . forms import EditProfileForm
import urllib
from django.conf import settings
from django.utils.encoding import smart_str

def _get_lat_lng(request, location):
    try:
        key = settings.GOOGLE_API_KEY
        location = urllib.parse.quote_plus(smart_str(location))
        url = 'https://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=false&key=%s' % (location, key)
        data = urllib.request.urlopen(url).read()
        jdata = json.loads(data.decode('utf-8'))
        #messages.info(request, jdata)
        #messages.info(request, jdata['results'][0]['geometry']['location'])
        if jdata['status'] == 'OK' and jdata['results'] and len(jdata['results']):
            return (jdata['results'][0]['geometry']['location']['lat'], jdata['results'][0]['geometry']['location']['lng'])
    except Exception as e:
        messages.info(request, e)
    return (0, 0)


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
            user.phonenu = form.cleaned_data['phonenu']
            user.timezone = form.cleaned_data['timezone']
            user.address = form.cleaned_data['address']
            user.lat, user.lng = _get_lat_lng(request, user.address)
            user.save()
            request.session['django_timezone'] = user.timezone
            messages.info(request, _('Your Profile has been updated successfully'))

            # Send conf back to Controllers
            controllers = Controller.objects.filter(login=request.user.username)
            for contr in controllers:
                cmd = Command.objects.create(
                    key = contr.key,
                    zid = contr.zid,
                    cmd = 'user_def',
                    parms = json.dumps({ 'user': { 'address': user.address, 'phonenu': user.phonenu, 'email': user.email } })
                )
                cmd.save()
        else:
            messages.error(request, _('Invalid Form Values'))
    else:
        form = EditProfileForm(initial={'email': user.email, 'phonenu': user.phonenu, 'address': user.address, 'timezone': user.timezone})

    context = {
        'form': form,
        'menu_profile': 'active',
        'timezones': pytz.common_timezones,
    }
    return render(request, 'users/profile.html', context)