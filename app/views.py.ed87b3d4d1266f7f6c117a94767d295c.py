from django.utils.timezone import localdate
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect, get_object_or_404
from .models import Host, Visitor, Map, Meeting, UserProfile
from .serializers import HostSerializer, MeetingSerializer,UserProfileSerializer, VisitorSerializer, MAPSerializer, UserSerializer
from .forms import VisitorForm, HostForm, RegistraionForm, SearchVisitorForm, UserForm, UserProfileForm, MeetingForm, MapForm, ToDoForm, StatusForm
from django.db.models import Q

from rest_framework import viewsets, status, generics, filters
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from django.contrib import messages
from projectvisitor.settings import EMAIL_HOST_USER

from itertools import chain
from haystack.query import SearchQuerySet
import json
from .tasks import add, sendmail

class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = [JSONWebTokenAuthentication,
                              SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        queryset = self.queryset
        query_set = queryset.filter(username=self.request.user)
        return query_set


class UserProfileViewSet(viewsets.ModelViewSet):
    authentication_classes = [JSONWebTokenAuthentication,
                              SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        queryset = self.queryset
        query_set = queryset.filter(user=self.request.user)
        return query_set


class VisitorViewSet(viewsets.ModelViewSet):
    authentication_classes = [JSONWebTokenAuthentication,
                              SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    queryset = Visitor.objects.all()
    serializer_class = VisitorSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ['full_name']
    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        queryset = self.queryset
        query_set = queryset.filter(user=self.request.user)
        return query_set


class HostViewSet(viewsets.ModelViewSet):
    authentication_classes = [JSONWebTokenAuthentication,
                              SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Host.objects.all()
    serializer_class = HostSerializer

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        queryset = self.queryset
        query_set = queryset.filter(user=self.request.user)
        return query_set


class MAPViewSet(viewsets.ModelViewSet):
    authentication_classes = [JSONWebTokenAuthentication,
                              SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Map.objects.all()
    serializer_class = MAPSerializer

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        queryset = self.queryset
        query_set = queryset.filter(user=self.request.user)
        return query_set


class MeetingViewSet(viewsets.ModelViewSet):
    authentication_classes = [JSONWebTokenAuthentication,
                              SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        queryset = self.queryset
        query_set = queryset.filter(user=self.request.user)
        return query_set


def index(request):
    if request.user.is_authenticated:
        map_key = Map.objects.filter(user=request.user).first()
        url = map_key.slug + '/logbook'
        return HttpResponseRedirect(url)
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
            instance = form.save(commit=False)
            instance.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            profile_instance = UserProfile.objects.create(user=user)
            login(request, user)
            return HttpResponseRedirect('../addnewlocations/')
    else:
        form = RegistraionForm()
    context = {'form': form}
    return render(request, 'registration/register.html', context)


def logbook(request, slug=None):
    print(slug)
    map_key = Map.objects.all().filter(slug=slug).values('id')
    query_list = Meeting.objects.all().filter(
        location_id=map_key[0]['id']).order_by('-date')
    query_list_host = Host.objects.prefetch_related('relateds')
    query_list_visitor = Visitor.objects.prefetch_related('relateds')

    user_form = ToDoForm(request.POST or None)
    form = StatusForm()

    datequery = request.POST.get("date")
    if not datequery:
        today = localdate()
        datequery = today

    query_list = query_list.filter(
        Q(date__icontains=datequery)
    )
    query = request.GET.get("q")

    if query:
        query_list_visitor_list = query_list_visitor.filter(
            Q(full_name__icontains=query) |
            Q(email__icontains=query) |
            Q(company_name__icontains=query)
        )

        query_list_v = query_list_visitor.filter(Q(full_name__icontains=query) &
                                                 Q(email__icontains=query))
        y = 0
        report = None
        for x in query_list_visitor_list:
            if y == 0:
                query_list_vi = query_list.filter(
                    visitor=query_list_visitor_list[y])
                report = chain(query_list_v, query_list_vi)
                y = y+1
            else:
                query_list_vi = query_list.filter(
                    visitor=query_list_visitor_list[y])
                report = chain(report, query_list_vi)
                y = y + 1

    mapdata = Map.objects.filter(user=request.user)
    puserdata = UserProfile.objects.filter(user=request.user).values()
    if puserdata:
        image = puserdata[0]['profile_pic']
    else:
        image = puserdata
    if mapdata.exists() and query:
        instance = {
            'image': image,
            "map": mapdata,
            "query_list_visitor": query_list_visitor_list,
            "objects_all": report,
            "objects_all1": query_list_host,
            'form1': form,
            'form': user_form,
            'slug': slug,
        }
        return render(request, 'account/logbook.html', instance)
    elif mapdata.exists():
        instance = {
            'image': image,
            'slug': slug,
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
            'image': image,
            "map": mapdata,
        }
        return redirect('../addnewlocations/')


def statusupdate(request, slug, id=None):
    instance = get_object_or_404(Meeting, id=id)

    form = StatusForm(request.POST or None, instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        print(form.cleaned_data.get("status"))
        instance.save(update_fields=["status"])
    else:
        form = StatusForm()

    instance = {
        'slug': slug,
        'form': form
    }
    return HttpResponseRedirect('../../logbook/')


def delselected(request, id, slug=None):
    query = request.GET.getlist("id[]")

    for target_list in query:
        arg = Meeting.objects.get(id=target_list).delete()

    data = {
        'slug': slug,
        "context": arg
    }
    return render(request, 'account/logbook.html', data)


def addnewvisit(request, slug):
    print(slug)
    form2 = MeetingForm(request.POST)
    form1 = VisitorForm(request.POST)
    form = ToDoForm()

    a = form1.is_valid()
    b = form2.is_valid()

    if a and b:
        instance1 = form1.save(commit=False)
        instance1.user = request.user
        instance1.save()

        name = form1.cleaned_data.get("full_name")
        email = form1.cleaned_data.get("email")
        hostname = form2.cleaned_data.get("host")
        fromtime = form2.cleaned_data.get("start_time").strftime('%H:%M:%S')
        totime = form2.cleaned_data.get("end_time").strftime('%H:%M:%S')
        ondate = form2.cleaned_data.get("date").strftime('%m-%d-%Y')
        hostval = hostname.values()
        list_result = [entry for entry in hostval]
        hname = list_result[0]['full_name']

        hostsubject = 'New apointment is created with '+name
        hostmessage = 'New visit is added with '+hname + \
            ' on '+ondate + ' from '+fromtime + ' to '+totime
        hostsender_email = email
        hostreceipient_email = EMAIL_HOST_USER

        reciversubject = 'New apointment is created with '+hname
        recivermessage = 'New visit is added with '+name + \
            ' on '+ondate + ' from '+fromtime + ' to '+totime
        sender_email = EMAIL_HOST_USER
        receipient_email = email
        messages.success(request, "Successfully Create New Entry for "+name)

        sendmail.delay(hostsubject, hostmessage,
                       hostsender_email, hostreceipient_email)
        sendmail.delay(reciversubject, recivermessage,
                       sender_email, receipient_email)

        instance1.save()
        instance2 = form2.save(commit=False)
        instance2.user = request.user
        instance2.visitor_id = instance1.pk
        instance2.save()
        form2.save_m2m()
    else:
        form = ToDoForm()
        form1 = VisitorForm()
        form2 = MeetingForm()

    mapdata = Map.objects.filter(user=request.user)
    puserdata = UserProfile.objects.filter(user=request.user).values()
    if puserdata:
        image = puserdata[0]['profile_pic']
    else:
        image = puserdata
    instance = {
        'image': image,
        "map": mapdata,
        'form': form,
        'form1': form1,
        'form2': form2,
        'slug': slug,
    }
    return render(request, 'account/addnewvisit.html', instance)


def use_old_visit(request,id=None, slug=None):
    print(id)
    query_list = Visitor.objects.filter(id=id)
    form2 = MeetingForm(request.POST)
    form = ToDoForm()

    if form2.is_valid():
        # instance1 = form1.save(commit=False)
        # instance1.user = request.user
        # instance1.save()

        # name = form1.cleaned_data.get("full_name")
        # email = form1.cleaned_data.get("email")
        # hostname = form2.cleaned_data.get("host")
        # fromtime = form2.cleaned_data.get("start_time").strftime('%H:%M:%S')
        # totime = form2.cleaned_data.get("end_time").strftime('%H:%M:%S')
        # ondate = form2.cleaned_data.get("date").strftime('%m-%d-%Y')
        # hostval = hostname.values()
        # list_result = [entry for entry in hostval]
        # hname = list_result[0]['full_name']

        # hostsubject = 'New apointment is created with '+name
        # hostmessage = 'New visit is added with '+hname + \
        #     ' on '+ondate + ' from '+fromtime + ' to '+totime
        # hostsender_email = email
        # hostreceipient_email = EMAIL_HOST_USER

        # reciversubject = 'New apointment is created with '+hname
        # recivermessage = 'New visit is added with '+name + \
        #     ' on '+ondate + ' from '+fromtime + ' to '+totime
        # sender_email = EMAIL_HOST_USER
        # receipient_email = email
        # messages.success(request, "Successfully Create New Entry for "+name)

        # send_mail(hostsubject,hostmessage,hostsender_email,[hostreceipient_email],fail_silently=False)
        # send_mail(reciversubject,recivermessage,sender_email,[receipient_email],fail_silently=False)

        # add karvanu che mailing

        # instance1.save()
        instance2 = form2.save(commit=False)
        instance2.user = request.user
        instance2.visitor_id = id
        instance2.save()
        form2.save_m2m()
    else:
        form2 = MeetingForm()
    mapdata = Map.objects.filter(user=request.user)
    puserdata = UserProfile.objects.filter(user=request.user).values()
    if puserdata:
        image = puserdata[0]['profile_pic']
    else:
        image = puserdata
    instance = {
        'image': image,
        "objects_all": query_list,
        "map": mapdata,
        # 'form1': form1,
        'form2': form2,
        'slug': slug,
    }
    return render(request, 'account/useoldvisit.html', instance)

def search_visitor(request, slug=None):
    print(slug)
    puserdata = UserProfile.objects.filter(user=request.user).values()
    if puserdata:
        image = puserdata[0]['profile_pic']
    else:
        image = puserdata
    instance = {
        'image': image,
        'slug': slug,
    }
    return render(request, 'account/searchvisitor.html', instance)


def searchlist(request, slug=None):
    visitor = SearchQuerySet().autocomplete(
        content_auto=request.POST.get('search_text', ''))
    if visitor:
        visitor[:5]
    print(slug)
    puserdata = UserProfile.objects.filter(user=request.user).values()
    if puserdata:
        image = puserdata[0]['profile_pic']
    else:
        image = puserdata
    instance = {
        'image': image,
        'visitor': visitor,
        'slug': slug,
    }
    return render(request, 'account/searchlist.html', instance)


def search_list(request, slug=None):
    sqs = SearchQuerySet().autocomplete(
        content_auto=request.GET.get('q', ''))[:5]
    suggestions = [result.text for result in sqs]
    # Make sure you return a JSON object, not a bare list.
    # Otherwise, you could be vulnerable to an XSS attack.
    print(suggestions)
    the_data = json.dumps({
        'results': suggestions
    })
    return HttpResponse(the_data, content_type='application/json')


def addressbook(request, slug):
    print(request.user)
    query_list = Visitor.objects.filter(user=request.user)

    query = request.GET.get("q")

    if query:
        query_list = query_list.filter(
            Q(full_name__icontains=query) |
            Q(email__icontains=query) |
            Q(company_name__icontains=query)
            # Q(address__icontains=query)
        )

    mapdata = Map.objects.filter(user=request.user)
    puserdata = UserProfile.objects.filter(user=request.user).values()
    if puserdata:
        image = puserdata[0]['profile_pic']
    else:
        image = puserdata
    instance = {
        'image': image,
        "map": mapdata,
        "objects_all": query_list,
        'slug': slug,
    }
    return render(request, 'account/addressbook.html', instance)


def colleagues(request, slug):
    print(slug)
    query_list = Host.objects.filter(user=request.user)
    query = request.GET.get("q")

    if query:
        query_list = query_list.filter(
            Q(full_name__icontains=query) |
            Q(email__icontains=query) |
            Q(mobile__icontains=query)
        )
    mapdata = Map.objects.filter(user=request.user)
    puserdata = UserProfile.objects.filter(user=request.user).values()
    if puserdata:
        image = puserdata[0]['profile_pic']
    else:
        image = puserdata
    instance = {
        'image': image,
        "map": mapdata,
        "objects_all": query_list,
        'slug': slug,
    }
    return render(request, 'account/colleagues.html', instance)


def addnewhost(request, slug):
    print(slug)
    form = HostForm(request.POST)
    mapdata = Map.objects.filter(user=request.user)
    
    puserdata = UserProfile.objects.filter(user=request.user).values()
    if puserdata:
        image = puserdata[0]['profile_pic']
    else:
        image = puserdata

    if form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        print(form.cleaned_data.get("full_name"))
        fname = form.cleaned_data.get("full_name")
        instance.save()
        messages.success(request, "Successfully Create New Entry for " + fname)
    else:
        form = HostForm()
    
    instance = {
        'image': image,
        "map": mapdata,
        'form': form,
        'slug': slug,
    }
    return render(request, 'account/addnewhost.html', instance)


def locations(request, slug):
    print(slug)
    user_form = ToDoForm()
    mapdata = Map.objects.filter(user=request.user)
    puserdata = UserProfile.objects.filter(user=request.user).values()
    if puserdata:
        image = puserdata[0]['profile_pic']
    else:
        image = puserdata
    instance = {
        'image': image,
        "map": mapdata,
        'form': user_form,
        'slug': slug,
    }
    return render(request, 'account/locations.html', instance)


def addnewlocations(request):
    form = MapForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        # fname = form.cleaned_data.get("name")
        instance.save()
        old_slug = Map.objects.get(id=instance.pk)
        print(old_slug.slug)
        # messages.success(request, "Successfully Create New Entry for " + fname)
        slug = old_slug.slug
        context = {
            'form': form,
            'slug': slug
        }
        return render(request, 'account/logbook.html', context)
        # return render(request, url)
    else:
        mapdata = Map.objects.filter(user=request.user).values()
        mapdata = mapdata[0]['slug']
        context = {
            'Map': mapdata,
            'form': form,

        }
        print('addnewlocations error')
        return render(request, 'account/addnewlocations.html', context)


def analytics(request, slug=None):
    print(slug)
    mapdata = Map.objects.filter(user=request.user)
    datalist = Visitor.objects.all().order_by('-date')
    puserdata = UserProfile.objects.filter(user=request.user).values()
    if puserdata:
        image = puserdata[0]['profile_pic']
    else:
        image = puserdata
    instance = {
        'image': image,
        "map": mapdata,
        "datalist": datalist,
        'slug': slug,
    }
    return render(request, 'account/analytics.html', instance)


def settings_general_company(request, slug=None):
    print(slug)
    puserdata = UserProfile.objects.filter(user=request.user).values()
    if puserdata:
        image = puserdata[0]['profile_pic']
    else:
        image = puserdata
    instance = {
        'image': image,
        'slug': slug,
    }
    return render(request, 'account/settings/general/company.html', instance)


def settings_general_management(request, slug=None):
    print(slug)

    puserdata = UserProfile.objects.filter(user=request.user).values()
    if puserdata:
        image = puserdata[0]['profile_pic']
    else:
        image = puserdata
    instance = {
        'image': image,
        'slug': slug,
    }
    return render(request, 'account/settings/general/usermanagement.html', instance)


def settings_general_rights(request, slug=None):
    print(slug)

    puserdata = UserProfile.objects.filter(user=request.user).values()
    if puserdata:
        image = puserdata[0]['profile_pic']
    else:
        image = puserdata
    instance = {
        'image': image,
        'slug': slug,
    }
    return render(request, 'account/settings/general/user-rights.html', instance)


def settings_other_billing(request, slug=None):
    print(slug)

    puserdata = UserProfile.objects.filter(user=request.user).values()
    if puserdata:
        image = puserdata[0]['profile_pic']
    else:
        image = puserdata
    instance = {
        'image': image,
        'slug': slug,
    }
    return render(request, 'account/settings/othersettings/billing-plan.html', instance)


def settings_other_buildingsecurity(request, slug=None):
    print(slug)

    puserdata = UserProfile.objects.filter(user=request.user).values()
    if puserdata:
        image = puserdata[0]['profile_pic']
    else:
        image = puserdata
    instance = {
        'image': image,
        'slug': slug,
    }
    return render(request, 'account/settings/othersettings/building-security.html', instance)


def settings_other_integrations(request, slug=None):
    print(slug)

    puserdata = UserProfile.objects.filter(user=request.user).values()
    if puserdata:
        image = puserdata[0]['profile_pic']
    else:
        image = puserdata
    instance = {
        'image': image,
        'slug': slug,
    }
    return render(request, 'account/settings/othersettings/integrations.html', instance)


def settings_other_privacy(request, slug=None):
    print(slug)

    puserdata = UserProfile.objects.filter(user=request.user).values()
    if puserdata:
        image = puserdata[0]['profile_pic']
    else:
        image = puserdata
    instance = {
        'image': image,
        'slug': slug,
    }
    return render(request, 'account/settings/othersettings/privacy.html', instance)


def settings_visitslist_kiosklist(request, slug=None):
    print(slug)

    puserdata = UserProfile.objects.filter(user=request.user).values()
    if puserdata:
        image = puserdata[0]['profile_pic']
    else:
        image = puserdata
    instance = {
        'image': image,
        'slug': slug,
    }
    return render(request, 'account/settings/visitslist/kiosk_list.html', instance)


def settings_visitslist_logbook(request, slug=None):
    print(slug)

    puserdata = UserProfile.objects.filter(user=request.user).values()
    if puserdata:
        image = puserdata[0]['profile_pic']
    else:
        image = puserdata
    instance = {
        'image': image,
        'slug': slug,
    }
    return render(request, 'account/settings/visitslist/logbook.html', instance)


def settings_visitslist_printer(request, slug=None):
    print(slug)

    puserdata = UserProfile.objects.filter(user=request.user).values()
    if puserdata:
        image = puserdata[0]['profile_pic']
    else:
        image = puserdata
    instance = {
        'image': image,
        'slug': slug,
    }
    return render(request, 'account/settings/visitslist/printer.html', instance)


def settings_visitslist_notifications(request, slug=None):
    print(slug)

    puserdata = UserProfile.objects.filter(user=request.user).values()
    if puserdata:
        image = puserdata[0]['profile_pic']
    else:
        image = puserdata
    instance = {
        'image': image,
        'slug': slug,
    }
    return render(request, 'account/settings/visitslist/notifications.html', instance)


def view(request, slug=None):
    print(slug)

    puserdata = UserProfile.objects.filter(user=request.user).values()
    if puserdata:
        image = puserdata[0]['profile_pic']
    else:
        image = puserdata
    user = User.objects.filter(username=request.user)
    userprofile = UserProfile.objects.filter(user=request.user)
    instance = {
        'user': user,
        'userprofile': userprofile,
        'image': image,
        'slug': slug,
    }
    return render(request, 'account/profile/view.html', instance)


def edituser(request, slug=None):
    mapdata = Map.objects.filter(user=request.user)
    puserdata = UserProfile.objects.filter(user=request.user).values()
    
    print(puserdata)
    if puserdata:
        image = puserdata[0]['profile_pic']
    else:
        image = puserdata
    
    if request.method == 'POST':
        form = UserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('../../profile/view')
        else:
            print('error2')
    else:
        form = UserForm(instance=request.user)
    instance = {
        'image': image,
        'form1': form,
        'slug': slug,
        "map": mapdata,
    }
    return render(request, 'account/profile/edit_user.html', instance)


def edituserprofile(request, slug=None):
    mapdata = Map.objects.filter(user=request.user)
    puserdata = UserProfile.objects.filter(user=request.user).values()
    instance = get_object_or_404(UserProfile, user=request.user)
    if puserdata:
        image = puserdata[0]['profile_pic']
    else:
        image = puserdata

    if request.method == 'POST':
        form = UserProfileForm(request.POST or None,
                        request.FILES or None, instance=instance)
        if form.is_valid():
            edit = form.save(commit=False)
            edit.save()
            return redirect('../../profile/view')
        else:
            print('error2')
    else:
        form = UserProfileForm(instance=instance)
    instance = {
        'image': image,
        'form2': form,
        'slug': slug,
        "map": mapdata,
    }
    return render(request, 'account/profile/edit_userprofile.html', instance)


def password(request, slug=None):
    print(slug)

    puserdata = UserProfile.objects.filter(user=request.user).values()
    if puserdata:
        image = puserdata[0]['profile_pic']
    else:
        image = puserdata
    instance = {
        'image': image,
        'slug': slug,
    }
    return render(request, 'account/profile/password.html', instance)
