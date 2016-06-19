from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect

from .forms import LoginForm

@login_required
def index(request):
    return render(request, 'index.html')

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
        return redirect(request.META.get('HTTP_REFERER'))

    return render(request, 'login.html', {'form': form})

def logout_views(request):
    if not request.user.is_authenticated():
        raise Http404()
    logout(request)
    return redirect('index')

@login_required
def user(request):
    return render(request, 'user.html')

@login_required
def terminal(request):
    return render(request, 'terminal.html')
