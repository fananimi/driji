from django.contrib import messages
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_http_methods as alowed

from zk.exception import ZKError
from zkcluster.models import Terminal

from .models import Grade, Student
from .forms import LoginForm, ScanTerminalForm, AddTerminalForm, EditTerminalForm, StudentForm, GradeForm

@alowed(['GET'])
@login_required
def index(request):
    return render(request, 'index.html')

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
def terminal_restart(request, terminal_id):
    terminal = get_object_or_404(Terminal, pk=terminal_id)
    try:
        terminal.zk_connect()
        terminal.zk_restart()
        messages.add_message(request, messages.SUCCESS, _('%(terminal)s has restarted') % {'terminal': terminal})
    except ZKError, e:
        messages.add_message(request, messages.ERROR, str(e))

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

    return redirect('terminal')

@alowed(['GET', 'POST'])
@login_required
def terminal_action(request, action, terminal_id):
    if action == 'edit':
        return terminal_edit(request, terminal_id)
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
def student(request):
    students = Student.objects.all()
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

@alowed(['GET'])
@login_required
def settings_grade(request):
    grade_list = Grade.objects.all()
    data = {
        'grade_list': grade_list
    }
    return render(request, 'settings_grade.html', data)

@alowed(['GET', 'POST'])
@login_required
def settings_grade_add(request):
    form = GradeForm(request.POST or None)
    if request.POST and form.is_valid():
        form.save()
        messages.add_message(request, messages.SUCCESS, _('Successfully adding a new grade'))
        return redirect('settings_grade')
    data = {
        'form': form
    }
    return render(request, 'settings_grade_add.html', data)
