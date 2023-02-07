from django.http import JsonResponse
import json,jwt,datetime
from django.core import serializers

from .models import *
from .serializers import *

from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed

from django.contrib.auth.hashers import make_password

import stripe
from yaml import serialize

from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage

stripe.api_key='sk_test_51Ls6PIC1mtj1ZAE316YPwRH8aW041MC0LJ9e1qmijA3Gj7O33y5KfwRZvAMA6oJhpXzCVEX7o3JrU9u3It7oy9ZW00Dv31Cf5h'

class RegisterView(APIView):
    def post(self, request):
        data = request.data
        data["password"] = make_password(data['password'])        
        print(data)
        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class PaymentView(APIView):
    def post(self,request,price):
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {                    
                    'price': 'price_1MMYoPC1mtj1ZAE3kubl3Ana',
                    'quantity': price,
                },
            ],
            mode='payment',
            success_url='http://localhost:4200/datebooked?action=success',
            cancel_url= 'http://localhost:4200/datebooked?action=cancel',
        )
        return Response(checkout_session.url)


class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed("User not found")
        
        if not user.check_password(password):
            raise AuthenticationFailed("Wrong password")
        
        payload = {
            'id' : user.id,
            'exp' : datetime.datetime.utcnow() + datetime.timedelta(days=1),
            'iat' : datetime.datetime.utcnow()
        }
        serializer=UserSerializer(user)

        token = jwt.encode(payload, 'secret', algorithm='HS256')  
                     
        return Response({token})


def check_jwt(token):

    
    if not token:
        raise AuthenticationFailed("Unauthenticated!")
    
    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed("Token Expired, Unauthenticated!")
    
    user = User.objects.filter(id=payload['id']).first()
     
    return user

class OfferDetails(APIView):
    def get(self, request, id):
        offer = Offer.objects.filter(id=id)
        serializeroffer = OfferSerializer(offer, many = True)     

        return Response(serializeroffer.data)
    def put(self,request,id):
        token = request.headers.get('Authorization').split()[1]        
        user = check_jwt(token)
        offer= Offer.objects.filter(id=id).first()
        data=request.data
               
        data['user']=user.id
        serializer=OfferSerializer(offer,data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    def delete(self,request,id):        
        offer= Offer.objects.filter(id=id).first()
        offer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class DateBookedEmployerStrict(APIView):
    def get(self,request,id):        
        datebooked=DateBooked.objects.filter(id=id).first()
        serializer=DateBookedSerializer(datebooked)
        return Response(serializer.data)


class DateBookedEmployer(APIView):
    #wykupowanie oferty
    def post(self,request,id):
        token = request.headers.get('Authorization').split()[1]        
        employer = check_jwt(token)
        employee=User.objects.filter(id=id).first()
        #offer=Offer.objects.filter(id=idoffer).first()
        data=request.data
        data['employee']=employee.id
        data['employer']=employer.id
        #data['offer']=offer.id
        serializer=DateBookedSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    #wykupione oferty przez klienta
    def get(self,request):
        token = request.headers.get('Authorization').split()[1]        
        employer = check_jwt(token)
        datebooked=DateBooked.objects.filter(employer=employer)
        serializer=DateBookedSerializer(datebooked,many=True)
        return Response(serializer.data)
    
   

    def put(self,request,id):        
        token = request.headers.get('Authorization').split()[1]        
        employer = check_jwt(token)
        datebooked= DateBooked.objects.filter(id=id).first()
        data=request.data
        data['employee']=datebooked.employee.id       
        data['employer']=employer.id
        data['accepted']=datebooked.accepted
        data['paid']=datebooked.paid
        serializer=DateBookedSerializer(datebooked,data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,id):        
        datebooked=DateBooked.objects.filter(id=id).first()
        datebooked.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class PaymentAcceptedView(APIView):
    def put(self,request,id):
        datebooked= DateBooked.objects.filter(id=id).first()        
        data={
            'accepted':True,
            'employee':datebooked.employee.id,
            'employer':datebooked.employer.id,
            'date_booked':datebooked.date_booked,
            'paid':True,
            'start_hour':datebooked.start_hour,
            'end_hour':datebooked.end_hour,
            'years_old':datebooked.years_old,
            'localization':datebooked.localization,
            'description':datebooked.description
        }         
        
        serializer=DateBookedSerializer(datebooked,data=data)        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class DateBookedEmployee(APIView):

    #oferty które ktoś kupił od opiekuna
    def get(self,request):
        token = request.headers.get('Authorization').split()[1]        
        employee = check_jwt(token)
        datebooked=DateBooked.objects.filter(employee=employee)
        serializer=DateBookedSerializer(datebooked,many=True)
        return Response(serializer.data)
    
    def put(self,request,id,accept): 
        

        token = request.headers.get('Authorization').split()[1]        
        employee = check_jwt(token)
        datebooked= DateBooked.objects.filter(id=id).first()
     
        data={}
        
        if(accept==1):
            data['accepted']=True
        else:
            data['accepted']=False    
        data['employee']=employee.id       
        data['employer']=datebooked.employer.id
        data['date_booked']=datebooked.date_booked        
        data['paid']=datebooked.paid
        data['start_hour']=datebooked.start_hour
        data['end_hour']=datebooked.end_hour
        data['years_old']=datebooked.years_old
        data['localization']=datebooked.localization
        data['description']=datebooked.description
        
        
        serializer=DateBookedSerializer(datebooked,data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)




class UserDetails(APIView):
    def get(self,request):
        token = request.headers.get('Authorization').split()[1]        
        user = check_jwt(token)
        serializer = UserSerializer(user)               
        return Response(serializer.data,status=status.HTTP_200_OK)
    def put(self,request):
        token = request.headers.get('Authorization').split()[1]        
        user = check_jwt(token)
        data=request.data
        data['password'] =user.password
        serializer=UserSerializer(user,data=data)
        if serializer.is_valid():
            serializer.save()
            print(data)
            return Response(serializer.data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request):
        token = request.headers.get('Authorization').split()[1]        
        user = check_jwt(token)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ChangePassword(APIView):
    def put(self,request):
        token = request.headers.get('Authorization').split()[1]        
        user = check_jwt(token)
        data=request.data
        data['email']=user.email
        data['login']=user.login
        data['first_name']=user.first_name
        data['last_name']=user.last_name
        data['birth_date']=user.birth_date        
        if user.check_password(data['password']):
            print(1)
            if data['n1_password']== data['n2_password']:                
                data['password'] = make_password(data['n1_password'])   
                print(data)             
                serializer=UserSerializer(user,data=data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    


class OfferView(APIView):
    def get(self,request):
        alloffer=Offer.objects.all()
        serializer=OfferSerializer(alloffer,many=True)        
        return Response(serializer.data)            

    def post(self, request):
        token = request.headers.get('Authorization').split()[1]        
        user = check_jwt(token)
        data = request.data        
        data["user"]=user.id     
        serializer = OfferSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class UserOfferView(APIView):
    def get(self,request):
        token = request.headers.get('Authorization').split()[1]        
        user = check_jwt(token)
        useroffers=Offer.objects.filter(user=user)
        serializer=OfferSerializer(useroffers,many=True)        
        return Response(serializer.data)   


@api_view(['GET','POST'])
def User_List(request,format=None):
    #get all the users
    #serialize them 
    #return json
    if request.method=='GET':
        users=User.objects.all()
        serializer=UserSerializer(users,many=True)
        return Response(serializer.data)
    
    if request.method=='POST':
        serializer=UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)


@api_view(['GET','PUT','DELETE']) 
def User_detail(request,id,format=None):
    try:
        user=User.objects.get(pk=id)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


    if request.method=='GET':        
        serializer = UserSerializer(user)               
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    elif request.method=='PUT':
        serializer=UserSerializer(user,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method=='DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@csrf_exempt
def SaveFile(request):
    file=request.FILES['uploadedFile']
    file_name=default_storage.save(file.name,file)

    return Response(file_name)


@api_view(['GET'])
def Booked_List(request,format=None):
    
    if request.method=='GET':
        booked=avBooked.objects.all()
        serializer=BookedSerializer(booked,many=True)
        return Response({f'Users with reserved dates':serializer.data})    
    

@api_view(['GET','POST','DELETE']) 
def Booked_detail(request,id,format=None):
    try:
        user=User.objects.get(pk=id)

    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
        


    if request.method=='GET':
        try:
            booked=avBooked.objects.filter(user_id=id)
        except avBooked.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = BookedSerializer(booked,many=True)               
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    elif request.method=='POST':
               
        newdate = avBooked.objects.create(user=user,date_booked=request.data.get('date_booked'))
        return Response(status=status.HTTP_201_CREATED)       
   
    
    elif request.method=='DELETE':
        try:
            booked=avBooked.objects.filter(user_id=id)
        except avBooked.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            date_delete=request.data.get('date_booked')
            delete=booked.get(date_booked=date_delete)
        except avBooked.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        delete.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
