from django.utils.translation import ugettext as _
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.forms import formsets
from django.contrib.auth.decorators import login_required
import json
import mongoengine as mo
from . models import Command, Sensor, Rule, RuleCondition, RuleAction, checkControllerOwner
from . forms import AddRuleForm, create_RuleConditionForm, RuleConditionFormSet, create_RuleActionForm, RuleActionFormSet


# Must display the devices owned by the user
@login_required
def indexAction(request, key):

    controller = checkControllerOwner(request.user.username, key)
    if not controller:
        messages.error(request, _('Invalid Parameters'))
        return redirect('controllers_index')

    rules = Rule.objects.filter(key=key)
    context = {
        'contr': controller,
        'rules': rules,
    }
    # Rules are read from the last known configuration
    return render(request, 'automation/index.html', context)


@login_required
def addAction(request, key):

    controller = checkControllerOwner(request.user.username, key)
    if not controller:
        messages.error(request, _('Invalid Parameters'))
        return redirect('controllers_index')

    if request.method == 'POST':
        form = AddRuleForm(request.POST)
        condition_formset = formsets.formset_factory(create_RuleConditionForm(key), formset=RuleConditionFormSet)
        cformset = condition_formset(request.POST)
        action_formset = formsets.formset_factory(create_RuleActionForm(key), formset=RuleActionFormSet)
        aformset = action_formset(request.POST)
        if form.is_valid() and cformset.is_valid() and aformset.is_valid():
            # Check rule description uniqueness
            try:
                Rule.objects.get(key=key, description=form.cleaned_data['description'])
                messages.error(request, _('This Rule Description already exists, please choose another one'))
            except:
                rule = Rule()
                rule.key = key
                rule.zid = controller.zid
                rule.description = form.cleaned_data['description']
                rule.conditions = []
                rule.actions = []
                for f in cformset:
                    condrule = RuleCondition()
                    condrule.condtype = f.cleaned_data['conditiontype']
                    condrule.devid, condrule.instid, condrule.sid = Sensor.splitInternalName(f.cleaned_data['csensor_name'])
                    condrule.value = f.cleaned_data['cvalue']
                    condrule.testtype = f.cleaned_data['testtype']
                    condrule.starttime = f.cleaned_data['starttime']
                    condrule.endtime = f.cleaned_data['endtime']
                    condrule.days = ''
                    if not f.cleaned_data['alldays']:
                        if f.cleaned_data['sunday']: condrule.days += '0'
                        if f.cleaned_data['monday']: condrule.days += '1'
                        if f.cleaned_data['tuesday']: condrule.days += '2'
                        if f.cleaned_data['wednesday']: condrule.days += '3'
                        if f.cleaned_data['thursday']: condrule.days += '4'
                        if f.cleaned_data['friday']: condrule.days += '5'
                        if f.cleaned_data['saturday']: condrule.days += '6'
                    rule.conditions.append(condrule)
                for f in aformset:
                    actrule = RuleAction()
                    actrule.actiontype = f.cleaned_data['actiontype']
                    actrule.value = f.cleaned_data['avalue']
                    actrule.devid, actrule.instid, actrule.sid = Sensor.splitInternalName(f.cleaned_data['asensor_name'])
                    rule.actions.append(actrule)

                rule.save()
                _sendRulesBack(key, controller.zid)
                messages.info(request, _('The Rule has been correctly created'))
                return redirect('automation', key=key)
        else:
            messages.error(request, _('Invalid Form Values'))
    else:
        form = AddRuleForm()
        condition_formset = formsets.formset_factory(create_RuleConditionForm(key), formset=RuleConditionFormSet)
        action_formset = formsets.formset_factory(create_RuleActionForm(key), formset=RuleActionFormSet)

    context = {
        'form': form,
        'condition_formset': condition_formset,
        'action_formset': action_formset,
        'contr': controller,
    }
    return render(request, 'automation/add.html', context)


@login_required
def deleteAction(request, key, rid):
    controller = checkControllerOwner(request.user.username, key)
    if not controller:
        messages.error(request, _('Invalid Parameters'))
        return redirect('controllers_index')

    try:
        rule = Rule.objects.filter(key=key, description=rid).delete()
        _sendRulesBack(key, rule.zid)
        messages.info(request, _('The Rule has been removed'))
    except:
        messages.error(request, _('Sorry, an internal software error occurred'))

    return redirect('automation', key=key)


# TODO
@login_required
def editAction(request, key, rid):
    pass


@login_required
def setDescrAction(request, key, rid):
    if request.method == 'POST':
        controller = checkControllerOwner(request.user.username, key)
        if not controller:
            messages.error(request, _('Invalid Parameters'))
            return redirect('controllers_index')

        newdescr = request.POST['newdescr']  # TODO: check injection
        if newdescr:
            try:
                rule = Rule.objects.get(key=key, description=rid)
                rule.description = newdescr
                rule.save()
                _sendRulesBack(key, rule.zid)
                messages.info(request, _('The Rule has been modified'))
            except Exception as e:
                messages.error(request, _('Sorry, an internal software error occurred'))
                messages.error(request, e)

    return redirect('automation', key=key)


# Send the command back to the Controller
def _sendRulesBack(key, zid):
    rules = Rule.objects.filter(key=key).exclude('id')  # _id resolves to id in MongoEngine
    cmd = Command.objects.create(
        key = key,
        zid = zid,
        cmd = 'rules_def',
        parms = json.dumps({ 'rules': rules.to_json() })
    )
    cmd.save()

