from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404

from app.models import Host,Visit,Visitor
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from app.serializers import HostSerializer,VisitorSerializer,VisitSerializer
from app.forms import VisitorForm,HostForm
from .forms import ToDoForm

from django.db.models import Q
# class VisitorViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows users to be viewed or edited.
#     """
#     queryset = Group.objects.all()
#     serializer_class = VisitorSerializer


# class VisitViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows groups to be viewed or edited.
#     """
#     queryset = Group.objects.all()
#     serializer_class = VisitSerializer

class HostView(ListAPIView):
    queryset = Host.objects.all()
    serializer_class = HostSerializer

class VisitView(ListAPIView):
    queryset = Visit.objects.all()
    serializer_class = VisitSerializer

class VisitorView(ListAPIView):
    queryset = Visitor.objects.all()
    serializer_class = VisitorSerializer
    
def addnewvisit(request):
    form = VisitorForm(request.POST)
    if form.is_valid():
        instance = form.save(commit=False)
        print(form.cleaned_data.get("full_name"))
        instance.save()
    else:
        form = VisitorForm()
            
    instance = {'form':form}
    return render(request, 'account/addnewvisit.html', instance)

def addnewhost(request):
    form = HostForm(request.POST)
    if form.is_valid():
        instance = form.save(commit=False)
        print(form.cleaned_data.get("full_name"))
        instance.save()
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
    
def about(request):
    return render(request,'app/about.html')

def contact(request):
    return render(request,'app/contact.html')

def index(request):
    return render(request,'app/index.html')

from rest_framework.views import APIView
from rest_framework.response import Response

# class CompanyListView(APIView):
#     def get(self, request):
#         query_list = VisitSerializer
#         # one = Host.objects.prefetch_related('relateds')
#         query = request.GET.get("q")

#         if query:
#             query_list = query_list.filter(
#                 Q(visit=query)|
#                 Q(visitor=query)|
#                 Q(host=query)|
#                 Q(invite_reason=query)
#                 )

#         instance = {
#             "objects_all":query_list,
#             # "objects_all1":events
#         }
#         return Response(instance)

from django.forms.models import model_to_dict

def logbook(request):
    query_list = Visit.objects.all()
    one = Host.objects.prefetch_related('relateds')
    # print(query_list[0].visiting.value)
    query = request.GET.get("q")

    if query:
        query_list = query_list.filter(
            Q(visit=query)|
            Q(visitor=query)|
            Q(host=query)|
            Q(invite_reason=query)
            )

    instance = {
        "objects_all":query_list,
        "objects_all1":one
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

    # return render(request,'account/addressbook.html')

def locations(request):
    user_form = ToDoForm()
    return render(request, 'account/Locations.html', {'form': user_form})

def analytics(request):
    return render(request,'account/analytics.html')

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
    