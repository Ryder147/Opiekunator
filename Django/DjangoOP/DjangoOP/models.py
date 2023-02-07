from django.db import models 
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from typing import List




class User(AbstractUser):
   
    login=models.CharField(unique=True,max_length=50)
    password=models.CharField(max_length=250)
    email=models.CharField(unique=True,max_length=50)
    first_name=models.CharField(max_length=50)
    last_name=models.CharField(max_length=50)
    birth_date=models.DateField(auto_now=False)    
    date_joined = models.DateTimeField(default=timezone.now())
    stripe_id = models.CharField(max_length=255, blank=True, null=True)
    username=None
    photolink=models.CharField(max_length=255, blank=True, null=True)
    phonenumber=models.CharField(max_length=30, blank=True, null=True)
    
    USERNAME_FIELD: str = 'email'
    REQUIRED_FIELDS: List[str] = []

    class Meta:
        db_table = 'users'

class Offer(models.Model):
    
    babies=models.BooleanField(default=False)
    kids=models.BooleanField(default=False)
    old=models.BooleanField(default=False)
    localization=models.CharField(max_length=50)
    av_start=models.DateTimeField()
    av_end=models.DateTimeField()
    description=models.CharField(max_length=800)
    reference=models.CharField(max_length=800,blank=True, null=True)
    create_time=models.DateTimeField(auto_now=True)
    user=models.ForeignKey('User', on_delete=models.CASCADE,related_name='user') 

    class Meta():
        db_table='offers'



class DateBooked(models.Model):
     
    date_booked= models.DateField(auto_now=False)
    start_hour=models.TimeField(auto_now=False)
    end_hour=models.TimeField(auto_now=False)
    years_old=models.IntegerField()                     #ile lat ma dziecko
    localization=models.CharField(max_length=50) 
    description=models.CharField(max_length=800)
    employee=models.ForeignKey('User', on_delete=models.CASCADE,related_name='employee')  #pracownik / opiekun
    employer=models.ForeignKey('User', on_delete=models.CASCADE,related_name='employer')  #pracodawca / użytkownik który wynajmuje opiekuna
    accepted=models.BooleanField(default=None, null=True,blank=True) #czy zaakceptowana przez opiekuna
    #offer=models.ForeignKey('Offer', on_delete=models.CASCADE,related_name='offer')
    paid=models.BooleanField(default=False)    #czy opłacona
    


    class Meta():
        db_table='date_booked'

'''
#użytkownik który wystawił ofertę
class UserDateBookedConnection(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    date_booked=models.ForeignKey(DateBooked, on_delete=models.CASCADE)
    class Meta():
        db_table='user_date_booked_connection'

#klient który zamówił opiekunkę  
class ClientDateBookedConnection(models.Model):
    client=models.ForeignKey(User, on_delete=models.CASCADE)
    date_boodek=models.ForeignKey(DateBooked, on_delete=models.CASCADE)
    class Meta():
        db_table='client_date_booked_connection'

class ClientOfferConnection(models.Model):
    client=models.ForeignKey(User, on_delete=models.CASCADE) 
    offer=models.ForeignKey(Offer,on_delete=models.CASCADE)
    
    class Meta():
        db_table='client_offer_connection'


class avBooked(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True) 
    date_booked= models.DateField(auto_now=False,null=True,blank=True)

    def __str__(self):
        return f'{self.user.id} {self.user.name} {self.date_booked}'

'''