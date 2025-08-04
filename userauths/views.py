from django.shortcuts import redirect, render
from userauths.forms import UserRegisterForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.utils.translation import gettext as _
from userauths.models import User


def register_view(request):  
    if request.method == "POST":
        form = UserRegisterForm(request.POST or None)
        if form.is_valid():
            new_user = form.save()
            username = form.cleaned_data.get("username")
            messages.success(
                request,
                _(f"Hello {username}, your account was created successfully.")
            )
            new_user = authenticate(username=form.cleaned_data['email'],
                                    password=form.cleaned_data['password1']
            )
            if new_user:
                login(request, new_user)
                return redirect("core:index")
    else:
        form = UserRegisterForm()
    return render(request, "userauths/sign-up.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        messages.warning(request, _("You are already logged in."))
        return redirect("core:index")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, email=user_obj.email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, _("Login successfully!"))
                next_url = request.GET.get("next", 'core:index')
                return redirect(next_url)
            else:
                messages.warning(request, _("User does not exist. Create an account."))
        except:
            messages.warning(
                request,
                _(f"User with {email} does not exist.")
            )
    return render(request, "userauths/sign-in.html")


def logout_view(request):
    logout(request)
    messages.success(request, _("You logged out."))
    return redirect("userauths:sign-in")
