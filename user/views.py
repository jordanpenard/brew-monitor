from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django import forms


class Loginform(forms.Form):
    username=forms.CharField()
    password=forms.CharField(widget=forms.PasswordInput)
    remember_me=forms.BooleanField(required=False)

def login_user(request):
    if request.method == "POST":
        form=Loginform(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data['remember_me']
            user = authenticate(request, username=username, password=password)
    
            if user is not None:
                login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)  # <-- Here if the remember me is False, that is why expiry is set to 0 seconds. So it will automatically close the session after the browser is closed.

                return redirect("index")
            else:
                messages.error(request, "Invalid credentials")
                return redirect("login")
        else:
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')
