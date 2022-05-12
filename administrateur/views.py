import sys

from Tools.scripts import generate_token
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage, send_mail, BadHeaderError
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse, request
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.db.models.query_utils import Q

from pythonProj import settings
from . import forms
from .forms import administrateurForm, connexionForm, forgotPasswordForm
from django.forms import ModelForm
from .forms import administrateurForm, etablissementForm
from .forms import connexionForm

# Create your views here.
from .tokens import generate_token


def inscriptionPage(request):
    # error = False
    # form = administrateurForm()
    if request.method == 'POST':
        print("Bonjour POST")
        form = administrateurForm(request.POST)
        if form.is_valid():
            print("Bonjour valide")
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activez votre compte InterSmart.'
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': generate_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, settings.EMAIL_HOST_USER, [user.email]
            )
            email.fail_silently = True
            email.send()
            print("Bonjour save")
            # return render(request,'inscription/ajout_etablissement.html',{'form': form})
            return HttpResponseRedirect('confirmEmail')
    else:
        print("Bonjour Pas POST")
        form = administrateurForm()
        # print(error)
    return render(request, 'inscription/register.html', {'form': form})


def newEtablissement(request):
    form = etablissementForm()
    if request.method == 'POST':
        form = etablissementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboardAdmin')
    else:
        print("Bonjour etablissement")
    return render(request, 'inscription/ajout_etablissement.html', {'form': form})


def dashboardAdmin(request):
    return render(request, 'dashboard/dashboardAdmin.html')


def confirmEmail(request):
    return render(request, 'confirm_email.html')


def connexionPage(request):
    error = False
    print("Bonjour connexion")
    if request.user.is_authenticated:
        return render(request, 'dashboardAdmin.html')
    if request.method == 'POST':
        print("Bonjour POST")

        username = request.POST["username"]
        print(username)
        password = request.POST["password"]
        print(password)
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('etablissement')

        else:
            form = connexionForm(request.POST)
            return render(request, 'connexion/login.html', {'form': form})
    else:
        form = connexionForm()
        return render(request, 'connexion/login.html', {'form': form})


def home(request):
    return render(request, 'accueil/index.html')


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and generate_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('home')
        return redirect('administrateurLogin')
    else:
        return HttpResponse('Activation link is invalid!')


def password_reset_request(request):
    if request.method == "POST":
        print('bonjour post')
        password_reset_form = forgotPasswordForm(request.POST)
        print(password_reset_form)
        if password_reset_form.is_valid():
            print('valid')
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            current_site = get_current_site(request)
            if associated_users.exists():
                for user in associated_users:
                    subject = "Reinitialisation du mot de passe InterSmart"
                    message = render_to_string('motDePasse/password_reset_email.txt', {
                        'user': user,
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': generate_token.make_token(user),
                        'protocol': 'http',
                    })
                    email = EmailMessage(
                        subject, message, settings.EMAIL_HOST_USER, [user.email]
                    )

                    email.fail_silently = True
                    try:
                        email.send()
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect("/password_reset_done")
    password_reset_form = forgotPasswordForm()
    return render(request, 'motDePasse/forgot-password.html', context={"password_reset_form": password_reset_form})

