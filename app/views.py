from rest_framework.views import APIView
import django
from .tasks import add, sendmail
import json
from haystack.query import SearchQuerySet
from itertools import chain
from projectvisitor import settings
from projectvisitor.settings import EMAIL_HOST_USER
from django.contrib import messages
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import viewsets, status, generics, filters
from django.db.models import Q, Count
from .forms import *
from .serializers import *
from .models import *
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import update_session_auth_hash
from .tokens import account_activation_token
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import localdate
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth import get_user_model
User = get_user_model()
import pandas as pd
import numpy as np

class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = [JSONWebTokenAuthentication,
                              SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = User.objects.all()
    serializer_class = UserSerializer

    # def get_queryset(self):
    #     """
    #     This view should return a list of all the purchases
    #     for the currently authenticated user.
    #     """
    #     queryset = self.queryset
    #     query_set = queryset.filter(id=self.request.user.id)
    #     return query_set


class ListUsers(APIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    authentication_classes = [JSONWebTokenAuthentication,
                              SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = MeetingSerializer

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        register_T = Meeting.objects.filter(pre_registered=True).values(
            'date', 'pre_registered').annotate(count=Count("pre_registered"))

        register_F = Meeting.objects.filter(pre_registered=False).values(
            'date', 'pre_registered').annotate(count=Count("pre_registered"))

        status = Meeting.objects.filter(status='check-out').values('date', 'status').annotate(count=Count("status"))

        counter1 = Meeting.objects.filter(counter='by-kiosk').values('date', 'counter').annotate(count=Count("counter"))

        counter2 = Meeting.objects.filter(counter='by-dashboard').values('date', 'counter').annotate(count=Count("counter"))

        counter3 = Meeting.objects.filter(counter='not-check-in').values('date', 'counter').annotate(count=Count("counter"))

        cabc1 = pd.DataFrame.from_records(counter1)
        cabc2 = pd.DataFrame.from_records(counter2)
        cabc3 = pd.DataFrame.from_records(counter3)
        sabc = pd.DataFrame.from_records(status)
        rt = pd.DataFrame.from_records(register_T)
        rf = pd.DataFrame.from_records(register_F)

        
        
        if counter1:
            count_1 = cabc1['count']
            count_1_date = cabc1['date']
        else:
            count_1 = counter1
            count_1_date = rabc['date']

        
        if counter2:
            count_2 = cabc2['count']
            count_2_date = cabc2['date']
        else:
            count_2 = counter2
            count_2_date = rabc['date']

        
        if counter3:
            count_3 = cabc3['count']
            count_3_date = cabc3['date']

        else:
            count_3 = counter3
            count_3_date = rabc['date']

        
        if status:
            date_s = sabc['date']
            status= sabc['status']
            count_s = sabc['count']
        else:
            date_s = status
            status = status
            count_s = status
        
        instance = {
            'date_s': date_s,
            'status': status,
            'count_s': count_s,
            'count_rt': rt['count'],
            'count_rf': rf['count'],
            'date_rt': rt['date'],
            'date_rf': rf['date'],
            'count_1': count_1,
            'count_1_date': count_1_date,
            'count_2': count_2,
            'count_2_date': count_2_date,
            'count_3': count_3,
            'count_3_date': count_3_date,
        }
        return Response(instance)


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
        query_set = queryset.filter(our_company=self.request.user.our_company)
        return query_set


class TheCompanyViewSet(viewsets.ModelViewSet):
    authentication_classes = [JSONWebTokenAuthentication,
                              SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = TheCompany.objects.all()
    serializer_class = TheCompanySerializer

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        queryset = self.queryset
        query_set = queryset.filter(name=self.request.user.our_company)
        return query_set


class MAPViewSet(viewsets.ModelViewSet):
    authentication_classes = [JSONWebTokenAuthentication,
                              SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Map.objects.all()
    serializer_class = MAPSerializer


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
        query_set = queryset.filter(host=self.request.user.id)
        return query_set


def index(request):
    if request.user.is_authenticated:
        try:
            map_data = Map.objects.filter(slug=request.user.our_company.location.all()[0])
            print(request.user.our_company.location.all()[0])
            url = map_data[0].slug + '/logbook'
            return HttpResponseRedirect(url)
        except (TypeError, ValueError, OverflowError,IndexError, ObjectDoesNotExist):
            return HttpResponseRedirect('../addnewlocations/')
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

            email = form.cleaned_data['email']
            company_name = form.cleaned_data['company_name']
            password = form.cleaned_data['password1']
            company_instance = TheCompany.objects.create(name=company_name)
            instance.our_company = company_instance
            instance.save()

            user = authenticate(username=email, password=password)
            login(request, user)
            return HttpResponseRedirect('../addnewlocations/')
    else:
        form = RegistraionForm()
    context = {'form': form}
    return render(request, 'registration/register.html', context)


def logbook(request, slug):
    mapdata = request.user.our_company.location.all()
    map_key = Map.objects.filter(slug=slug).values('id')
    query_list = Meeting.objects.all().filter(
        location_id=map_key[0]['id']).order_by('-date')
    query_list_visitor = Visitor.objects.prefetch_related('relateds')

    user_form = ToDoForm(request.POST or None)
    status_form = StatusForm()

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

    image = request.user.profile_pic

    if mapdata.exists() and query:
        instance = {
            'image': image,
            "map": mapdata,
            "query_list_visitor": query_list_visitor_list,
            "objects_all": report,
            'form1': status_form,
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
            'form1': status_form,
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


def delselected(request, id, slug):
    query = request.GET.getlist("id[]")

    for target_list in query:
        arg = Meeting.objects.get(id=target_list).delete()

    data = {
        'slug': slug,
        "context": arg
    }
    return render(request, 'account/logbook.html', data)


def addnewvisit(request, slug):

    thecompany = TheCompany.objects.filter(name=request.user.our_company)

    if request.method == 'POST':
        form2 = MeetingForm(thecompany[0], request.POST)
        form1 = VisitorForm(request.POST)

        a = form1.is_valid()
        b = form2.is_valid()

        if a and b:
            instance1 = form1.save(commit=False)
            instance1.our_company = request.user.our_company
            instance1.save()

            instance2 = form2.save(commit=False)
            instance2.counter = 'not-check-in'
            if instance2.pre_registered is True:
                instance2.pre_registered = False
                instance2.counter = 'by-dashboard'
            if instance2.start_time is None:
                instance2.start_time = django.utils.timezone.now().time()
            if instance2.end_time is None:
                instance2.end_time = django.utils.timezone.now(
                ) + django.utils.timezone.timedelta(hours=1)
            if instance2.date is None:
                instance2.date = django.utils.timezone.now()

            name = form1.cleaned_data.get("full_name")
            email = form1.cleaned_data.get("email")
            hostname = form2.cleaned_data.get("host")
            fromtime = instance2.start_time.strftime('%H:%M:%S')
            totime = instance2.end_time.strftime('%H:%M:%S')
            ondate = instance2.date.strftime('%m-%d-%Y')
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
            messages.success(
                request, "Successfully Create New Entry for "+name)

            # sendmail.delay(hostsubject, hostmessage,
            #             hostsender_email, hostreceipient_email)
            # sendmail.delay(reciversubject, recivermessage,
            #             sender_email, receipient_email)
            print(form2.cleaned_data.get("location").id)
            instance2.our_company = request.user.our_company
            instance2.visitor_id = instance1.pk
            instance2.location_id = form2.cleaned_data.get("location").id
            instance2.save()
            form2.save_m2m()
    else:
        form1 = VisitorForm()
        form2 = MeetingForm(thecompany[0], initial={'pre_registered': False, 'date': django.utils.timezone.now(
        ), 'start_time': django.utils.timezone.now(), 'end_time': django.utils.timezone.now()+django.utils.timezone.timedelta(hours=1)})

    mapdata = request.user.our_company.location.all()
    image = request.user.profile_pic

    instance = {
        'image': image,
        "map": mapdata,
        'form1': form1,
        'form2': form2,
        'slug': slug,
    }
    return render(request, 'account/addnewvisit.html', instance)


def use_old_visit(request, slug, id):
    print(id)
    thecompany = TheCompany.objects.filter(name=request.user.our_company)
    query_list = Visitor.objects.filter(id=id)

    if request.method == 'POST':
        form2 = MeetingForm(thecompany[0], request.POST)
        visitor = Visitor.objects.get(id=id)

        if form2.is_valid():
            name = visitor.full_name
            email = visitor.email

            hostname = form2.cleaned_data.get("host")
            fromtime = form2.cleaned_data.get(
                "start_time").strftime('%H:%M:%S')
            totime = form2.cleaned_data.get("end_time").strftime('%H:%M:%S')
            ondate = form2.cleaned_data.get("date").strftime('%m-%d-%Y')
            hostval = hostname.values()
            list_result = [entry for entry in hostval]
            colleagues_names = []
            colleagues_emails = []
            for value in list_result:
                colleagues_names.append(value["full_name"])
                colleagues_emails.append(value["email"])

            hname = list_result[0]['full_name']

            hostsubject = 'New apointment is created with 111'+name
            hostmessage = 'New visit is added with '+hname + \
                ' on '+ondate + ' from '+fromtime + ' to '+totime
            hostsender_email = email
            hostreceipient_email = EMAIL_HOST_USER

            reciversubject = 'New apointment is created with '+hname
            recivermessage = 'New visit is added with '+name + \
                ' on '+ondate + ' from '+fromtime + ' to '+totime
            sender_email = EMAIL_HOST_USER
            receipient_email = email
            messages.success(
                request, "Successfully Create New Entry for "+name)

            sendmail.delay(hostsubject, hostmessage,
                           hostsender_email, hostreceipient_email)
            sendmail.delay(reciversubject, recivermessage,
                           sender_email, receipient_email)

            # add karvanu che mailing

            instance2 = form2.save(commit=False)
            instance2.user = request.user
            instance2.visitor_id = id
            instance2.save()
            form2.save_m2m()
    else:
        form2 = MeetingForm(thecompany[0])

    mapdata = request.user.our_company.location.all()
    image = request.user.profile_pic

    instance = {
        'image': image,
        "objects_all": query_list,
        "map": mapdata,
        'form2': form2,
        'slug': slug,
    }
    return render(request, 'account/useoldvisit.html', instance)


def search_visitor(request, slug):
    print(slug)
    puserdata = User.objects.filter(email=request.user).values()
    if puserdata:
        image = puserdata[0]['profile_pic']
    else:
        image = puserdata
    instance = {
        'image': image,
        'slug': slug,
    }
    return render(request, 'account/searchvisitor.html', instance)


def searchlist(request, slug):
    visitor = SearchQuerySet().autocomplete(
        content_auto=request.POST.get('search_text', ''))
    if visitor:
        visitor[:5]
    print(slug)
    puserdata = User.objects.filter(email=request.user).values()
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


def search_list(request, slug):
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
    query_list = Visitor.objects.filter(our_company=request.user.our_company)

    query = request.GET.get("q")

    if query:
        query_list = query_list.filter(
            Q(full_name__icontains=query) |
            Q(email__icontains=query) |
            Q(company_name__icontains=query)
        )

    mapdata = request.user.our_company.location.all()
    image = request.user.profile_pic

    instance = {
        'image': image,
        "map": mapdata,
        "objects_all": query_list,
        'slug': slug,
    }
    return render(request, 'account/addressbook.html', instance)


def addressbookdetail(request, id, slug):
    query_list = Meeting.objects.all().filter(visitor_id=id).order_by('-date')
    query_list_visitor = Visitor.objects.prefetch_related('relateds')

    mapdata = request.user.our_company.location.all()
    image = request.user.profile_pic

    instance = {
        'id': id,
        "query_list_visitor": query_list_visitor,
        # "objects_all1": query_list_host,
        'image': image,
        "map": mapdata,
        "objects_all": query_list,
        'slug': slug,
    }
    return render(request, 'account/addressbookdetail.html', instance)


def addressbookedit(request, id, slug):
    mapdata = request.user.our_company.location.all()
    image = request.user.profile_pic

    id_lists = request.GET.getlist("id[]")

    for id_list in id_lists:
        id = id_list

    instance = get_object_or_404(Visitor, id=id)

    if request.method == 'POST':
        form = VisitorForm(request.POST or None,
                           request.FILES or None, instance=instance)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            print(form.cleaned_data.get("full_name"))
            fname = form.cleaned_data.get("full_name")
            instance.save()
            messages.success(
                request, "Successfully Create New Entry for " + fname)
    else:
        form = VisitorForm(instance=instance)

    instance = {
        'image': image,
        "map": mapdata,
        'form': form,
        'slug': slug,
        'id': id
    }
    return render(request, 'account/editvisitor.html', instance)


def delselectedaddress(request, id, slug):
    query = request.GET.getlist("id[]")

    for target_list in query:
        arg = Visitor.objects.get(id=target_list).delete()

    data = {
        'slug': slug
    }
    return render(request, 'account/addressbook.html', data)


def colleagues(request, slug):
    query_list = User.objects.filter(our_company=request.user.our_company)
    query = request.GET.get("q")

    if query:
        query_list = query_list.filter(
            Q(full_name__icontains=query) |
            Q(email__icontains=query) |
            Q(mobile__icontains=query)
        )

    mapdata = request.user.our_company.location.all()
    image = request.user.profile_pic

    instance = {
        'image': image,
        "map": mapdata,
        "objects_all": query_list,
        'slug': slug,
    }
    return render(request, 'account/colleagues.html', instance)


def addnewhost(request, slug):
    randomstring = BaseUserManager().make_random_password()

    locations_assign = Map.objects.get(slug=slug)
    mapdata = request.user.our_company.location.all()
    image = request.user.profile_pic

    print(locations_assign.id)
    if request.method == 'POST':
        print('isPost')
        form = ColleaguesForm(request.POST)
        if form.is_valid():
            is_email = form.cleaned_data.get("email")
            is_user = User.objects.filter(email=is_email)
            if is_user.exists():
                print("1")
                messages.success(
                    request, "User Alredy exists so would you like to add this person to this location ?", extra_tags='exists')
            else:
                print("2")
                instance = form.save(commit=False)
                instance.is_active = False
                instance.email=is_email
                instance.set_password(randomstring)
                instance.our_company = request.user.our_company
                instance.save()
                instance.user_location.add(locations_assign.id)
                print(instance)
                fname = form.cleaned_data.get("full_name")

                current_site = get_current_site(request)
                print(instance.id)
                mail_subject = 'Activate your account.'
                message = render_to_string('account_active_email.html', {
                    'usertocreate': instance,
                    'domain': current_site.domain,
                    'randomstring': randomstring,
                    'uid': urlsafe_base64_encode(force_bytes(instance.pk)).decode(),
                    'token': account_activation_token.make_token(instance),
                })
                to_email = form.cleaned_data.get('email')
                sender_email = EMAIL_HOST_USER

                sendmail.delay(mail_subject, message,
                            sender_email, to_email)

                messages.success(request, "Successfully Create New Entry for " + fname)
    else:
        form = ColleaguesForm()

    instance = {
        'image': image,
        "map": mapdata,
        'form': form,
        'slug': slug,
    }
    return render(request, 'account/addnewhost.html', instance)


def addselected(request, email, slug):
    print(email)
    mapdata = request.user.our_company.location.all()
    image = request.user.profile_pic

    locations_assign = Map.objects.get(slug=slug)
    is_user = User.objects.filter(
        email=email, user_location=locations_assign.id)
    if is_user.exists():
        return JsonResponse({"msg": "User is already assign to that location, try someother email"},safe=False)
    else:
        user_instance = User.objects.get(email=email)
        user_instance.user_location.add(locations_assign.id)
        return JsonResponse({"msg": "Location added to the given User"}, safe=False)


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        print(uid)
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        msg11 = 'Thank you for your email confirmation. Now you can login your account with username and password we genrated for you and send you in your mail.'
    else:
        print(user.password)
        msg11 = 'Activation link is invalid!'

    instance = {
        'msg': msg11,
    }
    return render(request, 'app/user_added.html', instance)


def user_added(request):
    return render(request, 'app/user_added.html')


def locations(request, slug):
    mapdata = request.user.our_company.location.all()
    image = request.user.profile_pic

    instance = {
        'image': image,
        "map": mapdata,
        'slug': slug,
    }
    return render(request, 'account/locations.html', instance)


def addnewlocations(request, slug=None):
    form = MapForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        # fname = form.cleaned_data.get("name")
        instance.user = request.user
        instance.save()
        old_slug = Map.objects.get(id=instance.pk)
        # messages.success(request, "Successfully Create New Entry for " + fname)
        slug = old_slug.slug

        ismap = Map.objects.filter(slug=instance.slug)
        print(ismap)
        company = TheCompany.objects.get(name=request.user.our_company)
        company.location.add(ismap[0].id)

        is_user = User.objects.get(email=request.user)
        is_user.user_location.add(ismap[0].id)

        context = {
            'form': form,
            'slug': slug
        }
        return render(request, 'account/logbook.html', context)
    else:
        mapdata = request.user.our_company.location.all()

        if mapdata.exists():
            mapdata = mapdata[0].slug
            context = {
                'Map': mapdata,
                'form': form,
            }
        else:
            context = {
                'form': form,
            }
        return render(request, 'account/addnewlocations.html', context)


def editlocations(request, slug, id):
    instance = get_object_or_404(Map, id=id)
    if request.method == 'POST':
        form = MapForm(request.POST, instance=instance)
        print('isPost')
        print(form)
        print(form.is_valid())
        if form.is_valid():
            print('isvalid.')
            instance = form.save(commit=False)
            # fname = form.cleaned_data.get("name")
            instance.save()
            old_slug = Map.objects.get(id=instance.pk)
            # messages.success(request, "Successfully Create New Entry for " + fname)
            slug = old_slug.slug

            print('11')
            context = {
                'form': form,
                'slug': slug
            }
            return render(request, 'account/logbook.html', context)
            print('111111')
    else:
        form = MapForm(instance=instance)
        location_data = Map.objects.filter(id=id)
        print(location_data)
        mapdata_all = request.user.our_company.location.all()
        mapdata = mapdata_all[0].slug
        context = {
            'locations': location_data,
            'Map': mapdata,
            'form': form,
        }
        return render(request, 'account/editlocations.html', context)


def analytics(request, slug):
    datalist = Visitor.objects.all().order_by('-date')

    mapdata = request.user.our_company.location.all()
    image = request.user.profile_pic

    colleagues = Meeting.objects.values(
        'host').annotate(count=Count("host")).order_by('host')
            
    colleague_frame = pd.DataFrame.from_records(
        colleagues) 
    total = 0
    
    for index, row in colleague_frame.iterrows():
        total = total + row['count']
    print(total)
    prt = []
    
    for index, row in colleague_frame.iterrows():
        val = row['count'] * 100 / total
        prt.append(round(val,2))
    print(prt)

    # for index, row in colleague_frame.iterrows():
    #     colleague_frame['prt'] = prt[index]
    
    colleague_frame.insert(2, "prt", prt, True)
    userlist = colleague_frame['host'].tolist()

    userdata = User.objects.filter(pk__in=userlist)

    print(colleague_frame)

    instance = {
        'userdata': userdata,
        'colleague_frame': colleague_frame['prt'],
        'image': image,
        "map": mapdata,
        "datalist": datalist,
        'slug': slug,
    }
    return render(request, 'account/analytics.html', instance)


def settings_general_company(request, slug):
    image = request.user.profile_pic
    mapdata = request.user.our_company.location.all()

    instance = {
        'image': image,
        'slug': slug,
        "map": mapdata,
    }
    return render(request, 'account/settings/general/company.html', instance)


def settings_general_management(request, slug):
    mapdata = request.user.our_company.location.all()
    image = request.user.profile_pic

    instance = {
        'image': image,
        'slug': slug,
        "map": mapdata,
    }
    return render(request, 'account/settings/general/usermanagement.html', instance)


def settings_general_rights(request, slug):
    mapdata = request.user.our_company.location.all()
    image = request.user.profile_pic
    instance = {
        'image': image,
        'slug': slug,
        "map": mapdata,
    }
    return render(request, 'account/settings/general/user-rights.html', instance)


def settings_other_billing(request, slug):
    mapdata = request.user.our_company.location.all()
    image = request.user.profile_pic

    instance = {
        'image': image,
        'slug': slug,
        "map": mapdata,
    }
    return render(request, 'account/settings/othersettings/billing-plan.html', instance)


def settings_other_buildingsecurity(request, slug):
    mapdata = request.user.our_company.location.all()
    image = request.user.profile_pic

    instance = {
        'image': image,
        'slug': slug,
        "map": mapdata,
    }
    return render(request, 'account/settings/othersettings/building-security.html', instance)


def settings_other_integrations(request, slug):
    mapdata = request.user.our_company.location.all()
    image = request.user.profile_pic

    instance = {
        'image': image,
        'slug': slug,
        "map": mapdata,
    }
    return render(request, 'account/settings/othersettings/integrations.html', instance)


def settings_other_privacy(request, slug):
    mapdata = request.user.our_company.location.all()
    image = request.user.profile_pic
    instance = {
        'image': image,
        'slug': slug,
        "map": mapdata,
    }
    return render(request, 'account/settings/othersettings/privacy.html', instance)


def settings_visitslist_kiosklist(request, slug):
    mapdata = request.user.our_company.location.all()
    image = request.user.profile_pic
    instance = {
        'image': image,
        'slug': slug,
        "map": mapdata,
    }
    return render(request, 'account/settings/visitslist/kiosk_list.html', instance)


def settings_visitslist_logbook(request, slug):
    mapdata = request.user.our_company.location.all()
    image = request.user.profile_pic

    instance = {
        'image': image,
        'slug': slug,
        "map": mapdata,
    }
    return render(request, 'account/settings/visitslist/logbook.html', instance)


def settings_visitslist_printer(request, slug):
    mapdata = request.user.our_company.location.all()
    image = request.user.profile_pic

    instance = {
        'image': image,
        'slug': slug,
        "map": mapdata,
    }
    return render(request, 'account/settings/visitslist/printer.html', instance)


def settings_visitslist_notifications(request, slug):
    mapdata = request.user.our_company.location.all()
    image = request.user.profile_pic

    instance = {
        'image': image,
        'slug': slug,
        "map": mapdata,
    }
    return render(request, 'account/settings/visitslist/notifications.html', instance)


def view(request, slug, id):
    print(id)
    mapdata = request.user.our_company.location.all()
    image = request.user.profile_pic

    user = User.objects.filter(id=id)
    instance = {
        'user': user,
        'image': image,
        'slug': slug,
        "map": mapdata,
    }
    return render(request, 'account/profile/view.html', instance)


def edituser(request, id, slug):
    mapdata = request.user.our_company.location.all()
    image = request.user.profile_pic

    if request.method == 'POST':
        form = UserForm(request.POST or None,
                        request.FILES or None, instance=request.user)
        if form.is_valid():
            form.save()
            instance = {
                'image': image,
                'form': form,
                'slug': slug,
                "map": mapdata,
            }
            return render(request, 'account/profile/edit_user.html', instance)
        else:
            print('eroor')
    else:
        form = UserForm(instance=request.user)
    instance = {
        'image': image,
        'form': form,
        'slug': slug,
        "map": mapdata,
    }
    return render(request, 'account/profile/edit_user.html', instance)


def password(request, slug, id):
    mapdata = request.user.our_company.location.all()
    image = request.user.profile_pic

    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
    else:
        form = PasswordChangeForm(user=request.user)
    instance = {
        'form': form,
        'image': image,
        'slug': slug,
        "map": mapdata,
    }
    return render(request, 'account/profile/password.html', instance)
