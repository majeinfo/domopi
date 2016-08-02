import logging
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

logger = logging.getLogger('domopi')

# Must display the devices owned by the user
@login_required
def indexAction(request, key):

    controller = checkControllerOwner(request.user.username, key)
    if not controller:
        messages.error(request, _('Invalid Parameters'))
        return redirect('controllers_index')

    rules = Rule.objects.filter(key=key)
    context = {
        'menu_rules': 'active',
        'contr': controller,
        'rules': rules,
    }
    # Rules are read from the last known configuration
    return render(request, 'automation/index.html', context)


def _updateRuleFromForm(rule, controller, key, form, cformset, aformset):

    rule.key = key
    rule.zid = controller.zid
    rule.description = form.cleaned_data['description']
    rule.conditions = []
    rule.actions = []

    for f in cformset:
        condrule = RuleCondition()
        condrule.condtype = f.cleaned_data['conditiontype']
        if condrule.condtype == RuleCondition.THRESHOLD:
            condrule.devid, condrule.instid, condrule.sid = Sensor.splitInternalName(f.cleaned_data['csensor_name'])
            condrule.value = f.cleaned_data['cvalue']
            condrule.testtype = f.cleaned_data['testtype']
        elif condrule.condtype == RuleCondition.STATUS:
            condrule.devid, condrule.instid, condrule.sid = Sensor.splitInternalName(f.cleaned_data['csensor_name2'])
            condrule.value = f.cleaned_data['cvalue2']
            condrule.testtype = f.cleaned_data['testtype2']
        elif condrule.condtype == RuleCondition.TIME:
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
        elif condrule.condtype == RuleCondition.SUNTIME:
            condrule.sunevt = f.cleaned_data['sunevt']
            condrule.sunoffset = f.cleaned_data['sunoffset']
            condrule.sundelay = f.cleaned_data['sundelay']
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
        if actrule.actiontype == RuleAction.SENSORCMD:
            actrule.value = f.cleaned_data['avalue']
            actrule.devid, actrule.instid, actrule.sid = Sensor.splitInternalName(f.cleaned_data['asensor_name'])
        elif actrule.actiontype == RuleAction.EMAILCMD:
            actrule.email = f.cleaned_data['email']
            actrule.subject = f.cleaned_data['subject']
            actrule.content = f.cleaned_data['content']
        rule.actions.append(actrule)


@login_required
def addAction(request, key):

    controller = checkControllerOwner(request.user.username, key)
    if not controller:
        messages.error(request, _('Invalid Parameters'))
        return redirect('controllers_index')

    if request.method == 'POST':
        form = AddRuleForm(request.POST)
        condition_formset = formsets.formset_factory(create_RuleConditionForm(key), formset=RuleConditionFormSet)
        cformset = condition_formset(request.POST, prefix='condition')
        action_formset = formsets.formset_factory(create_RuleActionForm(key), formset=RuleActionFormSet)
        aformset = action_formset(request.POST, prefix='action')
        if form.is_valid() and cformset.is_valid() and aformset.is_valid():
            # Check rule description uniqueness
            try:
                Rule.objects.get(key=key, description=form.cleaned_data['description'])
                messages.error(request, _('This Rule Description already exists, please choose another one'))
            except:
                rule = Rule()
                _updateRuleFromForm(rule, controller, key, form, cformset, aformset)
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
        'condition_formset': condition_formset(prefix='condition'),
        'action_formset': action_formset(prefix='action'),
        'contr': controller,
    }
    return render(request, 'automation/add.html', context)


@login_required
def editAction(request, key, rid):

    conds = []
    actions = []

    controller = checkControllerOwner(request.user.username, key)
    if not controller:
        messages.error(request, _('Invalid Parameters'))
        return redirect('controllers_index')

    try:
        rule = Rule.objects.get(key=key, description=rid)
    except:
        messages.error(request, _('Invalid Parameters'))
        return redirect('automation', key=key)

    if request.method == 'POST':
        form = AddRuleForm(request.POST)
        condition_formset = formsets.formset_factory(create_RuleConditionForm(key), formset=RuleConditionFormSet)
        cformset = condition_formset(request.POST, prefix='condition')
        action_formset = formsets.formset_factory(create_RuleActionForm(key), formset=RuleActionFormSet)
        aformset = action_formset(request.POST, prefix='action')
        if form.is_valid() and cformset.is_valid() and aformset.is_valid():
            # Check rule description uniqueness
            count = Rule.objects.filter(key=key, description=form.cleaned_data['description']).count()
            if rule.description != form.cleaned_data['description'] and count > 0:
                messages.error(request, _('This Rule Description already exists, please choose another one'))
                form.fields['description'].initial = rule.description
            else:
                _updateRuleFromForm(rule, controller, key, form, cformset, aformset)
                rule.save()
                _sendRulesBack(key, controller.zid)
                messages.info(request, _('The Rule has been correctly updated'))
                return redirect('automation', key=key)
        else:
            messages.error(request, _('Invalid Form Values'))
    else: # not a POST
        form = AddRuleForm(initial={'description': rule.description})
        condition_formset = formsets.formset_factory(create_RuleConditionForm(key), formset=RuleConditionFormSet, extra=0)

        for cond in rule.conditions:
            d = {
                'conditiontype': cond.condtype,
            }
            if cond.condtype == RuleCondition.THRESHOLD:
                d['csensor_name'] = Sensor.buildInternalName(cond.devid, cond.instid, cond.sid)
                d['cvalue'] = cond.value
                d['testtype'] = cond.testtype
            elif cond.condtype == RuleCondition.STATUS:
                d['csensor_name2'] = Sensor.buildInternalName(cond.devid, cond.instid, cond.sid)
                d['cvalue2'] = cond.value
                d['testtype2'] = cond.testtype
            elif cond.condtype == RuleCondition.TIME:
                d['starttime'] = cond.starttime
                d['endtime'] = cond.endtime
                d['alldays'] = True if not cond.days else False
                d['sunday'] = True if '0' in cond.days else False
                d['monday'] = True if '1' in cond.days else False
                d['tuesday'] = True if '2' in cond.days else False
                d['wednesday'] = True if '3' in cond.days else False
                d['thursday'] = True if '4' in cond.days else False
                d['friday'] = True if '5' in cond.days else False
                d['saturday'] = True if '6' in cond.days else False
            elif cond.condtype == RuleCondition.SUNTIME:
                d['sunevt'] = cond.sunevt
                d['sunoffset'] = cond.sunoffset
                d['sundelay'] = cond.sundelay
                d['alldays'] = True if not cond.days else False
                d['sunday'] = True if '0' in cond.days else False
                d['monday'] = True if '1' in cond.days else False
                d['tuesday'] = True if '2' in cond.days else False
                d['wednesday'] = True if '3' in cond.days else False
                d['thursday'] = True if '4' in cond.days else False
                d['friday'] = True if '5' in cond.days else False
                d['saturday'] = True if '6' in cond.days else False
            conds.append(d)

        action_formset = formsets.formset_factory(create_RuleActionForm(key), formset=RuleActionFormSet, extra=0)

        for action in rule.actions:
            d = {
                'actiontype': action.actiontype,
            }
            if action.actiontype == RuleAction.SENSORCMD:
                d['asensor_name'] = Sensor.buildInternalName(action.devid, action.instid, action.sid)
                d['avalue'] = action.value
            elif action.actiontype == RuleAction.EMAILCMD:
                d['email'] = action.email
                d['subject'] = action.subject
                d['content'] = action.content
            actions.append(d)

    logger.debug(conds)
    logger.debug(actions)
    context = {
        'form': form,
        'condition_formset': condition_formset(prefix='condition', initial=conds),
        'action_formset': action_formset(prefix='action', initial=actions),
        'contr': controller,
        'rule': rule,
    }
    return render(request, 'automation/edit.html', context)


@login_required
def deleteAction(request, key, rid):
    controller = checkControllerOwner(request.user.username, key)
    if not controller:
        messages.error(request, _('Invalid Parameters'))
        return redirect('controllers_index')

    try:
        rule = Rule.objects.get(key=key, description=rid)
        zid = rule.zid
        Rule.objects.filter(key=key, description=rid).delete()
        _sendRulesBack(key, zid)
        messages.info(request, _('The Rule has been removed'))
    except Exception as e:
        messages.error(request, _('Sorry, an internal software error occurred'))
        logger.error(e)

    return redirect('automation', key=key)


@login_required
def setDescrAction(request, key, rid):
    if request.method == 'POST':
        controller = checkControllerOwner(request.user.username, key)
        if not controller:
            messages.error(request, _('Invalid Parameters'))
            return redirect('controllers_index')

        try:
            rule = Rule.objects.get(key=key, description=rid)
        except:
            messages.error(request, _('Invalid Parameters'))
            return redirect('controllers_index')

        newdescr = request.POST['newdescr']
        if newdescr and newdescr != rule.description:
            try:
                if Rule.objects.filter(key=key, description=newdescr).count() > 0:
                    messages.error(request, _('This Rule Description does not exist, please choose another one'))
                else:
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


