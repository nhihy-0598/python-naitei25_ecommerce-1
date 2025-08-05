from django.shortcuts import redirect, render
from userauths.forms import UserRegisterForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.conf import settings
from userauths.models import User
from django.utils.translation import gettext as _


def register_view(request):  
    if request.method == "POST":
        form = UserRegisterForm(request.POST or None)
        if form.is_valid():
            new_user = form.save()
            username = form.cleaned_data.get("username")
            messages.success(
                request,
                _("Hello %(username)s, your account was created successfully.") % {"username": username}
            )

            new_user = authenticate(username=form.cleaned_data['email'],
                                    password=form.cleaned_data['password1']
            )
            login(request, new_user)
            return redirect("core:index")
    else:
        print("User cannot be registered")
        form = UserRegisterForm()
    context = {
        'form': form,
    }
    return render(request, "userauths/sign-up.html", context)

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
                _("User with %(email)s does not exist.") % {"email": email}
            )

    
    return render(request, "userauths/sign-in.html")


def logout_view(request):
    logout(request)
    messages.success(request, _("You logged out."))
    return redirect("userauths:sign-in")
        
        
