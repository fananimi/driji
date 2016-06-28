# -*- coding: utf-8 -*-
import calendar

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_http_methods as alowed

from driji.forms import AddTerminalForm, EditTerminalForm, LoginForm, \
    ScanTerminalForm, StudentForm
from driji.models import PhoneBook, User

from layang.models import Message

from zk.exception import ZKError

from zkcluster.models import Terminal


@alowed(['GET'])
@login_required
def index(request):
    return redirect('terminal')
    # return render(request, 'index.html')


@alowed(['GET'])
@login_required
def my_profile(request):
    return render(request, 'my_profile.html')


@alowed(['GET', 'POST'])
def login_view(request):
    user = request.user
    if user.is_authenticated():
        next_url = request.GET.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('index')

    form = LoginForm(request.POST or None)
    if request.POST and form.is_valid():
        authenticate_user = form.get_authenticate_user()
        login(request, authenticate_user)
        messages.add_message(request, messages.SUCCESS, "Welcome {} !".format(request.user.username))
        return redirect(request.META.get('HTTP_REFERER'))

    return render(request, 'login.html', {'form': form})


@alowed(['GET'])
def logout_views(request):
    if not request.user.is_authenticated():
        raise Http404()
    logout(request)
    return redirect('index')


@alowed(['GET'])
@login_required
def terminal(request):
    terminals = Terminal.objects.all()
    paginator = Paginator(terminals, settings.PAGINATION_NUMBER)
    page = request.GET.get('page')
    try:
        terminals = paginator.page(page)
    except PageNotAnInteger:
        terminals = paginator.page(1)
    except EmptyPage:
        terminals = paginator.page(paginator.num_pages)
    data = {
        'terminals': terminals
    }
    return render(request, 'terminal.html', data)


@alowed(['POST'])
@login_required
def terminal_add(request):
    connected = request.GET.get('connected')
    if connected:
        form = AddTerminalForm(request.POST or None, {'validate_name': True})
        if form.is_valid():
            try:
                form.save()
                messages.add_message(request, messages.SUCCESS, _('Successfully registering a new terminal'))
                return redirect('terminal')
            except ZKError, e:
                messages.add_message(request, messages.ERROR, str(e))
    else:
        form = AddTerminalForm(request.POST or None)

    data = {
        'form': form
    }
    return render(request, 'terminal_add.html', data)


@alowed(['GET', 'POST'])
@login_required
def terminal_scan(request):
    form = ScanTerminalForm(request.POST or None)
    if request.POST and form.is_valid():
        ip = form.cleaned_data['ip']
        port = form.cleaned_data['port']

        terminal = Terminal(
            ip=ip,
            port=port
        )
        try:
            terminal.zk_connect()
            sn = terminal.zk_getserialnumber()

            # manipulate the POST information
            mutable = request.POST._mutable
            request.POST._mutable = True
            request.POST['serialnumber'] = sn
            request.POST._mutable = mutable

            terminal.zk_disconnect()
            return terminal_add(request)
        except ZKError, e:
            messages.add_message(request, messages.ERROR, str(e))

    data = {
        'form': form
    }

    return render(request, 'terminal_scan.html', data)


@alowed(['GET'])
@login_required
def terminal_members(request, terminal_id):
    terminal = get_object_or_404(Terminal, pk=terminal_id)
    data = {
        'terminal': terminal
    }
    return render(request, 'terminal_members.html', data)


@alowed(['GET', 'POST'])
@login_required
def terminal_edit(request, terminal_id):
    terminal = get_object_or_404(Terminal, pk=terminal_id)
    form = EditTerminalForm(request.POST or None, instance=terminal)
    if request.POST and form.is_valid():
        try:
            form.save()
            messages.add_message(request, messages.SUCCESS, _('Successfully updating a terminal'))
        except ZKError, e:
            messages.add_message(request, messages.ERROR, str(e))
        return redirect('terminal')
    data = {
        'terminal': terminal,
        'form': form
    }
    return render(request, 'terminal_edit.html', data)


@alowed(['POST'])
@login_required
def terminal_sync_report(request, terminal_id):
    terminal = get_object_or_404(Terminal, pk=terminal_id)
    try:
        terminal.sync_report()
        messages.add_message(request, messages.SUCCESS, _('%(terminal)s has synced') % {'terminal': terminal})
    except ZKError, e:
        messages.add_message(request, messages.ERROR, str(e))

    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)

    return redirect('terminal')


@alowed(['POST'])
@login_required
def terminal_restart(request, terminal_id):
    terminal = get_object_or_404(Terminal, pk=terminal_id)
    try:
        terminal.zk_connect()
        terminal.zk_restart()
        messages.add_message(request, messages.SUCCESS, _('%(terminal)s has restarted') % {'terminal': terminal})
    except ZKError, e:
        messages.add_message(request, messages.ERROR, str(e))

    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)

    return redirect('terminal')


@alowed(['POST'])
@login_required
def terminal_poweroff(request, terminal_id):
    terminal = get_object_or_404(Terminal, pk=terminal_id)
    try:
        terminal.zk_connect()
        terminal.zk_poweroff()
        terminal.zk_disconnect()
        messages.add_message(request, messages.SUCCESS, _('%(terminal)s has shutdown') % {'terminal': terminal})
    except ZKError, e:
        messages.add_message(request, messages.ERROR, str(e))

    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)

    return redirect('terminal')


@alowed(['POST'])
@login_required
def terminal_voice(request, terminal_id):
    terminal = get_object_or_404(Terminal, pk=terminal_id)
    try:
        terminal.zk_connect()
        terminal.zk_voice()
        terminal.zk_disconnect()
    except ZKError, e:
        messages.add_message(request, messages.ERROR, str(e))

    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)

    return redirect('terminal')


@alowed(['POST'])
@login_required
def terminal_format(request, terminal_id):
    terminal = get_object_or_404(Terminal, pk=terminal_id)
    try:
        terminal.format()
        messages.add_message(request, messages.SUCCESS, _('%(terminal)s has formated') % {'terminal': terminal})
    except ZKError, e:
        messages.add_message(request, messages.ERROR, str(e))

    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)

    return redirect('terminal')


@alowed(['POST'])
@login_required
def terminal_delete(request, terminal_id):
    terminal = get_object_or_404(Terminal, pk=terminal_id)
    try:
        terminal.delete()
        messages.add_message(request, messages.SUCCESS, _('%(terminal)s has deleted') % {'terminal': terminal})
    except ZKError, e:
        messages.add_message(request, messages.ERROR, str(e))

    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)

    return redirect('terminal')


@alowed(['GET', 'POST'])
@login_required
def terminal_action(request, action, terminal_id):
    if action == 'members':
        return terminal_members(request, terminal_id)
    elif action == 'edit':
        return terminal_edit(request, terminal_id)
    elif action == 'sync_report':
        return terminal_sync_report(request, terminal_id)
    elif action == 'restart':
        return terminal_restart(request, terminal_id)
    elif action == 'poweroff':
        return terminal_poweroff(request, terminal_id)
    elif action == 'voice':
        return terminal_voice(request, terminal_id)
    elif action == 'format':
        return terminal_format(request, terminal_id)
    elif action == 'delete':
        return terminal_delete(request, terminal_id)
    else:
        raise Http404("Action doest not allowed")


@alowed(['GET'])
@login_required
def terminal_detail(request, terminal_id):
    terminal = get_object_or_404(Terminal, pk=terminal_id)
    users = terminal.user_set.all()

    # generate days number
    days = []
    now = timezone.now()
    cal = calendar.monthrange(now.year, now.month)
    for d in range(cal[0] - 1, cal[1] + 1):
        days.append(d)

    data = {
        'terminal': terminal,
        'users': users,
        'days': days
    }
    return render(request, 'terminal_detail.html', data)


@alowed(['GET'])
@login_required
def student(request):
    students = User.objects.filter(user_type=User.USER_STUDENT)
    paginator = Paginator(students, settings.PAGINATION_NUMBER)
    page = request.GET.get('page')
    try:
        students = paginator.page(page)
    except PageNotAnInteger:
        students = paginator.page(1)
    except EmptyPage:
        students = paginator.page(paginator.num_pages)
    data = {
        'students': students
    }
    return render(request, 'student.html', data)


@alowed(['GET', 'POST'])
@login_required
def student_add(request):
    form = StudentForm(request.POST or None)
    if request.POST and form.is_valid():
        form.save()
        messages.add_message(request, messages.SUCCESS, _('Successfully registering a new student'))
        return redirect('student')
    data = {
        'form': form
    }
    return render(request, 'student_add.html', data)


@alowed(['POST', 'GET'])
@login_required
def student_add_terminal(request):
    if request.POST:
        action = request.POST.get('action')
        if action in ['upload_selected', 'upload_selected_commit']:
            if action == 'upload_selected':
                student_id_list = request.POST.getlist('student_id_list')
                if not student_id_list:
                    messages.add_message(request, messages.WARNING, _('No student selected.'))
                    return redirect('student')
            if action == 'upload_selected_commit':
                student_id_list = request.POST.getlist('student_id_list')
                terminal_id_list = request.POST.getlist('terminal_id_list')
                if not student_id_list:
                    messages.add_message(request, messages.WARNING, _('No student selected.'))
                if not terminal_id_list:
                    messages.add_message(request, messages.WARNING, _('No terminal selected.'))
                else:
                    terminals = Terminal.objects.filter(id__in=terminal_id_list)

                    for terminal in terminals:
                        try:
                            terminal.add_users(student_id_list)
                            return redirect('student')
                        except ZKError, e:
                            err_msg = '[{}] {}'.format(terminal.name, e)
                            messages.add_message(request, messages.ERROR, err_msg)

            students = User.objects.filter(id__in=student_id_list)
            terminals = Terminal.objects.all()
            data = {
                'students': students,
                'terminals': terminals
            }
            return render(request, 'student_add_terminal.html', data)
        else:
            messages.add_message(request, messages.WARNING, _('No action selected.'))

    return redirect('student')


@alowed(['GET'])
@login_required
def attendance(request, terminal_id):
    terminal = get_object_or_404(Terminal, pk=terminal_id)
    users = terminal.user_set.all()

    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    midnight = (today + timezone.timedelta(days=1))
    first_date = timezone.make_aware(timezone.datetime(today.year, today.month, 1))

    attendances = terminal.attendances.filter(
        timestamp__range=(first_date, midnight),
        summary__isnull=False
    ).values(
        'summary__driji_user_id',
        'summary__date',
        'summary__status'
    )
    summary = {}
    for att in attendances:
        key = str(att['summary__driji_user_id'])
        if not summary.get(key):
            summary[key] = {}
        key_day = att['summary__date'].strftime('%Y%m%d')
        summary[key][key_day] = att['summary__status']

    # generate days number
    days = []
    cal = calendar.monthrange(today.year, today.month)
    for d in range(cal[0] - 1, cal[1] + 1):
        date = today.replace(day=d).date()
        days.append(date)
        if date < midnight.date():
            for user in users:
                key = str(user.id)
                day_key = date.strftime('%Y%m%d')
                if date.isoweekday() != 7:
                    if summary.get(key):
                        if not summary.get(key).get(date.strftime('%Y%m%d')):
                            summary[key][day_key] = 'a'
                    else:
                        summary[key] = {}
                        summary[key][day_key] = 'a'
                else:
                    if summary.get(key):
                        if not summary.get(key).get(date.strftime('%Y%m%d')):
                            summary[key][day_key] = 'w'
                    else:
                        summary[key] = {}
                        summary[key][day_key] = 'w'

    data = {
        'terminal': terminal,
        'users': users,
        'days': days,
        'today': today,
        'summary': summary
    }
    return render(request, 'attendance.html', data)


@alowed(['GET'])
@login_required
def sms(request):
    list_sms = Message.objects.all()
    data = {
        'list_sms': list_sms
    }
    return render(request, 'sms.html', data)


@alowed(['GET'])
@login_required
def phonebook(request):
    contacts = PhoneBook.objects.all()
    paginator = Paginator(contacts, settings.PAGINATION_NUMBER)
    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)

    data = {
        'contacts': contacts
    }
    return render(request, 'phonebook.html', data)

# @alowed(['GET'])
# @login_required
# def settings_grade(request):
#     grade_list = Grade.objects.all()
#     data = {
#         'grade_list': grade_list
#     }
#     return render(request, 'settings_grade.html', data)
#
# @alowed(['GET', 'POST'])
# @login_required
# def settings_grade_add(request):
#     form = GradeForm(request.POST or None)
#     if request.POST and form.is_valid():
#         form.save()
#         messages.add_message(request, messages.SUCCESS, _('Successfully adding a new grade'))
#         return redirect('settings_grade')
#     data = {
#         'form': form
#     }
#     return render(request, 'settings_grade_add.html', data)
