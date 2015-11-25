from django.utils.translation import ugettext as _
from django import forms
from . models import Sensor

class LoginForm(forms.Form):
    username = forms.CharField(max_length=75, label=_('Your Login'))
    password = forms.CharField(widget=forms.PasswordInput, label=_('Your Password'))


class AddDeviceForm(forms.Form):
    key = forms.CharField(max_length=80, label=_('Controller ID'), help_text=_('This is the value written on you Domopi Box'))


class AddRuleForm(forms.Form):
    description = forms.CharField(max_length=256, label=_('Description'), help_text=_('This is the free description of the Automation Rule'))


# Warning: field names of RuleCondition and RuleAction must differ or we should use the 'prefix' parameter
def create_RuleConditionForm(key):
    class RuleConditionForm(forms.Form):
        THRESHOLD = 'thresholdcond'
        TIME = 'timecond'
        STATUS = 'statuscond'
        TYPE = ( (THRESHOLD, _('Sensor Value Threshold')), (TIME, _('Time Condition')), ((STATUS, _('Sensor Status'))))
        TESTOP = ( ('>', '>'), ('>=', '=>'), ('<', '<'), ('<=', '<='), ('==', '='), ('!=', '<>'))
        conditiontype = forms.ChoiceField(choices=TYPE, label=_('Condition Type'))
        sensors = Sensor.objects.filter(key=key)
        csensor_name = forms.ChoiceField(
            (tuple((x.getInternalName(),x.description))
                for x in sensors
                if x.devtype == Sensor.TYPE_BATTERY or x.devtype == Sensor.TYPE_SENSOR_BINARY or x.devtype == Sensor.TYPE_SENSOR_MULTILEVEL),
            label=_('Sensor Name'))
        testtype = forms.ChoiceField(choices=TESTOP, label=_('Value Comparison'), required=False)
        cvalue = forms.CharField(max_length=32, label=_('Threshold Value'), help_text=_('This is the Value the Sensor must be compared with'), required=False)
        starttime = forms.CharField(label=_('Start Time'), required=False)
        endtime = forms.CharField(label=_('End Time'), required=False)
        alldays = forms.BooleanField(label=_('Everyday'), required=False)
        monday = forms.BooleanField(label=_('Monday'), required=False)
        tuesday = forms.BooleanField(label=_('Tuesday'), required=False)
        wednesday = forms.BooleanField(label=_('Wednesday'), required=False)
        thursday = forms.BooleanField(label=_('Thursday'), required=False)
        friday = forms.BooleanField(label=_('Friday'), required=False)
        saturday = forms.BooleanField(label=_('Saturday'), required=False)
        sunday = forms.BooleanField(label=_('Sunday'), required=False)

    return RuleConditionForm


class RuleConditionFormSet(forms.formsets.BaseFormSet):
    pass


class RuleActionForm1(forms.Form):
    SENSORCMD = 'sensorcmd'
    TYPE = ( (SENSORCMD, _('Sensor Command')), )
    ON = 'ON'
    OFF = 'OFF'
    COMMANDS = ( (ON, _('On')), (OFF, _('Off')))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['actiontype'] = forms.ChoiceField(choices=RuleActionForm1.TYPE)
        self.fields['sensor_name'] = forms.ModelChoiceField(queryset=Sensor.objects.filter(key='1234'))
        self.fields['value'] = forms.ChoiceField(choices=RuleActionForm1.COMMANDS)


def create_RuleActionForm(key):
    class RuleActionForm(forms.Form):
        SENSORCMD = 'sensorcmd'
        TYPE = ( (SENSORCMD, _('Sensor Command')), )
        ON = 'ON'
        OFF = 'OFF'
        COMMANDS = ( (ON, _('On')), (OFF, _('Off')))

        actiontype = forms.ChoiceField(choices=TYPE, label=_('Action Type'))
        sensors = Sensor.objects.filter(key=key, devtype=Sensor.TYPE_SWITCH)
        asensor_name = forms.ChoiceField((tuple((x.getInternalName(),x.description)) for x in sensors), label=_('Sensor Name'))
        avalue = forms.ChoiceField(label=_('Command Value'), choices=COMMANDS)

    return RuleActionForm


class RuleActionFormSet(forms.formsets.BaseFormSet):
    pass