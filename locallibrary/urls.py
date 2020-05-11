"""locallibrary URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('catalog/', include('catalog.urls')),
                  path('', RedirectView.as_view(url='catalog/')),

                  # Django site authentication urls (for login, logout, password management)
                  path('accounts/', include('django.contrib.auth.urls')),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


"""AUTHENTICATION AND PERMISSIONS(MUST READ)"""
# Note: Using the above method {path('accounts/', include('django.contrib.auth.urls'))} adds the
# following URLs with names in square brackets, which can be used to reverse the URL mappings.
# You don't have to implement anything else — the above URL mapping automatically maps the below
# mentioned URLs.

# accounts/ login/ [name='login']
# accounts/ logout/ [name='logout']
# accounts/ password_change/ [name='password_change']
# accounts/ password_change/done/ [name='password_change_done']
# accounts/ password_reset/ [name='password_reset']
# accounts/ password_reset/done/ [name='password_reset_done']
# accounts/ reset/<uidb64>/<token>/ [name='password_reset_confirm']
# accounts/ reset/done/ [name='password_reset_complete']


# Django provides almost everything you need to create authentication pages to handle login, log out,
# and password management "out of the box". This includes a URL mapper, views and forms, but it does
# not include the templates, you have to create your template.
# Note: You'll almost certainly need to change the form handling code if you change your user model
# but even so, you would still be able to use the stock view functions.


# Naturally, Django look for the above automatically generated urls templates in the project template
# folder. for example, (http://127.0.0.1:8000/accounts/login/) will look for a template named
# 'login.html' in registration folder of the the main Project template folder, so in essence,
# FILE PATH will be Project_Template/registration/login.html


# The URLs (and implicitly, views) that we just added expect to find their associated templates in a
# directory /registration/ somewhere in the templates search path.


# After putting in the right credentials at (http://127.0.0.1:8000/accounts/login/), Django expects
# that upon logging in, you will want to be taken to a profile page, which may or may not be the case.
# As you haven't defined this page yet, you'll get another error!. To correct this, if you don't want
# to go to the profile page, you open the project settings and add <LOGIN_REDIRECT_URL = '/'>
# below to the bottom. This should redirect to the site homepage by default now.

# PASSWORD RESET TEMPLATES: The default password reset system uses email to send the user a reset link.
# You need to create forms to get the user's email address, send the email, allow them to enter a new
# password, and to note when the whole process is complete. Below is the sequential step of the process:

# 1. Password Reset Form: This is the form used to get the user's email address (for sending the password reset email)
# templates/registration/password_reset_form.html

# 2. Password Reset Done: This form is displayed after your email address has been collected.
# templates/registration/password_reset_done.html

# 3. Password Reset Email: This template provides the text of the HTML email containing the reset link that we will send
# to users. /templates/registration/password_reset_email.html

# 4. Password Reset Confirm: This page is where you enter your new password after clicking the link in the password
# reset email. /templates/registration/password_reset_confirm.html

# 5. Password Reset Complete: This is the last password-reset template, which is displayed to notify you when the
# password reset has succeeded. templates/registration/password_reset_complete.html
