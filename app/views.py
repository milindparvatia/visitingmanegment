from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404

from app.models import Host,Visitor
from django.contrib.auth.models import User, Group
from rest_framework import viewsets,status
from rest_framework.generics import ListAPIView
from app.serializers import HostSerializer,VisitorSerializer
from app.forms import VisitorForm,HostForm
from .forms import ToDoForm, StatusForm

from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.mail import send_mail
from django.contrib import messages

from projectvisitor.settings import EMAIL_HOST_USER

class VisitorViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Visitor.objects.all()
    serializer_class = VisitorSerializer

class HostViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Host.objects.all()
    serializer_class = HostSerializer

class HostView(ListAPIView):
    queryset = Host.objects.all()
    serializer_class = HostSerializer

class VisitorView(ListAPIView):
    queryset = Visitor.objects.all()
    serializer_class = VisitorSerializer
    
def addnewvisit(request):
    form = VisitorForm(request.POST)
    if form.is_valid():
        instance = form.save(commit=False)

        name = form.cleaned_data.get("full_name")
        email = form.cleaned_data.get("email")
        hostname= form.cleaned_data.get("visiting")
        fromtime = form.cleaned_data.get("start_time").strftime('%H:%M:%S')
        totime = form.cleaned_data.get("end_time").strftime('%H:%M:%S')
        ondate = form.cleaned_data.get("date").strftime('%m-%d-%Y')
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
        send_mail(hostsubject,hostmessage,hostsender_email,[hostreceipient_email],fail_silently=False)
        send_mail(reciversubject,recivermessage,sender_email,[receipient_email],fail_silently=False)
        instance.save()
        form.save_m2m()
        # hostnamemain = [full_name for full_name in list_result]
        # print(hostnamemain)
        # print(list_result[1]['full_name'])
        # print(ondate)
        # print(form.cleaned_data.get("end_time"))
        # print(form.cleaned_data.get("date"))
    else:
        form = VisitorForm()
            
    instance = {'form':form}
    return render(request, 'account/addnewvisit.html', instance)

def addnewhost(request):
    form = HostForm(request.POST)
    if form.is_valid():
        instance = form.save(commit=False)
        print(form.cleaned_data.get("full_name"))
        fname= form.cleaned_data.get("full_name")
        instance.save()
        messages.success(request, "Successfully Create New Entry for "+fname)
    else:
        form = HostForm()
            
    instance = {'form':form}
    return render(request, 'account/addnewhost.html', instance)

def register(request):
    if request.method == 'POST':    
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username = username, password = password)
            login(request, user)
        return render(request,'account/logbook.html')
    else:
        form=UserCreationForm()
    context={'form' : form}
    return render(request,'registration/register.html',context)

def statusupdate(request,id=None): 
    instance = get_object_or_404(Visitor,id=id)

    form = StatusForm(request.POST or None, instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        print(form.cleaned_data.get("status"))
        instance.save(update_fields=["status"])
    else:
        form = StatusForm()
            
    instance = {'form':form}
    return HttpResponseRedirect('../../logbook/')


def logbook(request): 
    query_list = Visitor.objects.all().order_by('-date')
    one = Host.objects.prefetch_related('relateds')
    
    user_form = ToDoForm()
    
    form = StatusForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        print(form.cleaned_data.get("status"))
        instance.save(update_fields=["status"])
    else:
        form = StatusForm()
    
    datequery = request.POST.get("date")

    if datequery:
        query_list = query_list.filter(
            Q(date__icontains=datequery)
            )
    query = request.GET.get("q")

    if query:
        query_list = query_list.filter(
            Q(full_name__icontains=query)|
            Q(email__icontains=query)|
            Q(company_name__icontains=query)
            # Q(address__icontains=query)
            )

    instance = {
        "objects_all":query_list,
        "objects_all1":one,
        'form1':form,
        'form':user_form
    }
    return render(request, 'account/logbook.html', instance)

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

    instance = {
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

    instance = {
        "objects_all":query_list
    }
    return render(request, 'account/colleagues.html', instance)

def about(request):
    return render(request,'app/about.html')

def contact(request):
    return render(request,'app/contact.html')

def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("/logbook/")
    else:
        return render(request,'app/index.html')

def locations(request):
    user_form = ToDoForm()
    return render(request, 'account/Locations.html', {'form': user_form})

def analytics(request):
    return render(request,'account/analytics.html')