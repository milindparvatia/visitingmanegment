from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect, get_object_or_404
from .models import Host, Visitor, Map, Meeting
from .serializers import HostSerializer, MeetingSerializer, VisitorSerializer, MAPSerializer
from .forms import VisitorForm, HostForm, RegistraionForm, MeetingForm, MapForm, ToDoForm, StatusForm

from rest_framework import viewsets, status
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.db.models import Q, FilteredRelation
from itertools import chain
import operator
from functools import reduce

from django.core.mail import send_mail
from django.contrib import messages
from projectvisitor.settings import EMAIL_HOST_USER

import datetime
import pandas as pd

class VisitorViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    queryset = Visitor.objects.all()
    serializer_class = VisitorSerializer

class HostViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    queryset = Host.objects.all()
    serializer_class = HostSerializer

class MAPViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    queryset = Map.objects.all()
    serializer_class = MAPSerializer

class MeetingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer

def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("/logbook/")
    else:
        return render(request, 'app/index.html')

def about(request):
    return render(request, 'app/about.html')

def contact(request):
    return render(request, 'app/contact.html')

def register(request):
    if request.method == 'POST':
        form = RegistraionForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            return HttpResponseRedirect('../addnewlocations/')
    else:
        form = RegistraionForm()
    context = {'form': form}
    return render(request, 'registration/register.html', context)

def logbook(request):
    query_list = Meeting.objects.all().order_by('-date')
    query_list_host = Host.objects.prefetch_related('relateds')
    query_list_visitor = Visitor.objects.prefetch_related('relateds')

    user_form = ToDoForm(request.POST or None)
    form = StatusForm()
    
    datequery = request.POST.get("date")
    if not datequery:
        print('1')
        today = datetime.date.today()
        datequery = today
    
    query_list = query_list.filter(
        Q(date__icontains=datequery)
    )
    query = request.GET.get("q")

    if query:
        print(query_list)
        query_list_visitor_list = query_list_visitor.filter(
            Q(full_name__icontains=query) |
            Q(email__icontains=query) |
            Q(company_name__icontains=query)
        )
        
        query_list_v = query_list_visitor.filter(Q(full_name__icontains=query)&
                                                        Q(email__icontains=query))
        y = 0
        for x in query_list_visitor_list:
            if y==0:
                query_list_vi = query_list.filter(
                    visitor=query_list_visitor_list[y])
                report = chain(query_list_v, query_list_vi)
                y = y+1
            else:
                query_list_vi = query_list.filter(
                    visitor=query_list_visitor_list[y])
                report = chain(report,query_list_vi)
                y = y+1

    mapdata = Map.objects.all()

    if mapdata.exists() and query:
        instance = {
        "map":mapdata,
        "query_list_visitor": query_list_visitor_list,
        "objects_all": report,
        "objects_all1":query_list_host,
        'form1':form,
        'form':user_form
        }
        return render(request, 'account/logbook.html', instance)
    elif mapdata.exists():
        instance = {
            "map": mapdata,
            "query_list_visitor": query_list_visitor,
            "objects_all": query_list,
            "objects_all1": query_list_host,
            'form1': form,
            'form': user_form
        }
        return render(request, 'account/logbook.html', instance)
    else:
        instance = {
        "map":mapdata,
        }
        return redirect('../addnewlocations/')

def statusupdate(request,id=None):
    instance = get_object_or_404(Meeting,id=id)

    form = StatusForm(request.POST or None, instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        print(form.cleaned_data.get("status"))
        instance.save(update_fields=["status"])
    else:
        form = StatusForm()

    instance = {'form': form}
    return HttpResponseRedirect('../../logbook/')

def delselected(request,id):
    query = request.GET.getlist("id[]")

    for target_list in query:
        arg = Meeting.objects.get(id=target_list).delete()

    data = {
        "context" : arg
    }
    return render(request,'account/logbook.html',data)

def addnewvisit(request):
    form2 = MeetingForm(request.POST)
    form1 = VisitorForm(request.POST)
    form = ToDoForm()

    a = form1.is_valid()
    b = form2.is_valid()

    if a and b:
        instance1 = form1.save()
        
        name = form1.cleaned_data.get("full_name")
        email = form1.cleaned_data.get("email")
        hostname= form2.cleaned_data.get("host")
        fromtime = form2.cleaned_data.get("start_time").strftime('%H:%M:%S')
        totime = form2.cleaned_data.get("end_time").strftime('%H:%M:%S')
        ondate = form2.cleaned_data.get("date").strftime('%m-%d-%Y')
        hostval = hostname.values()
        list_result = [entry for entry in hostval]
        hname=list_result[0]['full_name']
    
        hostsubject='New apointment is created with '+name
        hostmessage='New visit is added with '+hname+' on '+ondate+ ' from '+fromtime+ ' to '+totime
        hostsender_email=email
        hostreceipient_email=EMAIL_HOST_USER

        reciversubject='New apointment is created with '+hname
        recivermessage='New visit is added with '+name+' on '+ondate+ ' from '+fromtime+ ' to '+totime
        sender_email=EMAIL_HOST_USER
        receipient_email=email
        messages.success(request, "Successfully Create New Entry for "+name)
        
        # send_mail(hostsubject,hostmessage,hostsender_email,[hostreceipient_email],fail_silently=False)
        # send_mail(reciversubject,recivermessage,sender_email,[receipient_email],fail_silently=False)
    
        # add karvanu che mailing

        instance1.save()
        instance2 = form2.save(commit=False)
        instance2.visitor_id = instance1.pk
        instance2.save()
        form2.save_m2m()
    else:
        form = ToDoForm()
        form1 = VisitorForm()
        form2 = MeetingForm()

    mapdata = Map.objects.all()

    instance = {
        "map": mapdata,
        'form': form,
        'form1':form1,
        'form2':form2
        }
    return render(request, 'account/addnewvisit.html', instance)

def addressbook(request):
    query_list = Visitor.objects.all()

    query = request.GET.get("q")

    if query:
        query_list = query_list.filter(
            Q(full_name__icontains=query)|
            Q(email__icontains=query)|
            Q(company_name__icontains=query)
            # Q(address__icontains=query)
            )

    mapdata = Map.objects.all()

    instance = {
        "map":mapdata,
        "objects_all":query_list
    }
    return render(request, 'account/addressbook.html', instance)

def colleagues(request):
    query_list = Host.objects.all()
    query = request.GET.get("q")

    if query:
        query_list = query_list.filter(
            Q(full_name__icontains=query)|
            Q(email__icontains=query)|
            Q(mobile__icontains=query)
            )
    mapdata = Map.objects.all()

    instance = {
        "map":mapdata,
        "objects_all":query_list
    }
    return render(request, 'account/colleagues.html', instance)

def addnewhost(request):
    form = HostForm(request.POST)
    if form.is_valid():
        instance = form.save(commit=False)
        # instance.user = request.user
        print(form.cleaned_data.get("full_name"))
        fname= form.cleaned_data.get("full_name")
        instance.save()
        messages.success(request, "Successfully Create New Entry for "+fname)
    else:
        form = HostForm()
            
    mapdata = Map.objects.all()

    instance = {
        "map":mapdata,
        'form':form
        }
    return render(request, 'account/addnewhost.html', instance)

def locations(request):
    user_form = ToDoForm()
    mapdata = Map.objects.all()

    instance = {
        "map":mapdata,
        'form': user_form
    }
    return render(request, 'account/locations.html', instance)

def addnewlocations(request):
    form = MapForm()

    context = {
        'form':form
    }
    return render(request,'account/addnewlocations.html',context)

def newlocations(request):
    if request.method == 'POST':
        print(request.POST.get('loc'))
        loc = request.POST.get('loc')
        name = request.POST.get('name')
        lon = request.POST.get('lon')
        lat = request.POST.get('lat')
        print(lon)
        print(lat)
        print(name)
        savemap = Map(loc = loc, name = name, lon = lon, lat = lat)
        savemap.save()
        return redirect('../logbook/')
    else:
        return redirect('../logbook/')

def analytics(request):
    mapdata = Map.objects.all()
    datalist = Visitor.objects.all().order_by('-date')

    instance = {
        "map":mapdata,
        "datalist":datalist
    }
    return render(request,'account/analytics.html', instance)
