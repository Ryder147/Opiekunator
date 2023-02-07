
from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'login', 'password','birth_date','first_name','last_name', 'stripe_id','photolink','phonenumber']
        extra_kwargs = {
            #'password': {'write_only': True},
            #'stripe_id': {'write_only': True}
        }

class DateBookedSerializer(serializers.ModelSerializer):
    class Meta:
        model=DateBooked
        fields='__all__'

'''       
class BookedSerializer(serializers.ModelSerializer):
    class Meta:
        model=avBooked
        fields=['user','date_booked']
'''
class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model=Offer
        fields='__all__'
