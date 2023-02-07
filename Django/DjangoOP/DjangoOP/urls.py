"""DjangoOP URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path
from DjangoOP import views
from rest_framework.urlpatterns import format_suffix_patterns

from django.conf.urls.static import static
from django.conf import settings 


urlpatterns = [
    path('admin/', admin.site.urls),
    path('Users/',views.User_List),
    path('Users/<int:id>',views.User_detail),
    path('SaveFile/',views.SaveFile),
    path('avBooked/',views.Booked_List),
    path('avBooked/<int:id>',views.Booked_detail),

    path('register/',views.RegisterView.as_view()),
    path('login/',views.LoginView.as_view()),
    path('offer/',views.OfferView.as_view()),
    path('offerdetails/<int:id>',views.OfferDetails.as_view()),
    path('UserDetails/',views.UserDetails.as_view()),
    path('ChangePassword/',views.ChangePassword.as_view()),
    path('useroffers/',views.UserOfferView.as_view()),
    path('datebookedEmployer/<int:id>',views.DateBookedEmployer.as_view()),
    path('datebookedEmployer/',views.DateBookedEmployer.as_view()),
    path('datebookedEmployee/',views.DateBookedEmployee.as_view()),
    path('datebookedEmployee/<int:id>/<int:accept>',views.DateBookedEmployee.as_view()),
    path('datebookedEmployerStrict/<int:id>',views.DateBookedEmployerStrict.as_view()),
    path('payment/<int:price>',views.PaymentView.as_view()),
    path('paymentaccepted/<int:id>',views.PaymentAcceptedView.as_view())                               

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns = format_suffix_patterns(urlpatterns)