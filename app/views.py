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
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
User = get_user_model()
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .serializers import *
from .forms import *
from django.db.models import Q


from rest_framework import viewsets, status, generics, filters
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from django.contrib import messages
from projectvisitor.settings import EMAIL_HOST_USER
from projectvisitor import settings

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

    # def get_queryset(self):
    #     """
    #     This view should return a list of all the purchases
    #     for the currently authenticated user.
    #     """
    #     queryset = self.queryset
    #     query_set = queryset.filter(username=self.request.user)
    #     return query_set


# class UserProfileViewSet(viewsets.ModelViewSet):
#     authentication_classes = [JSONWebTokenAuthentication,
#                               SessionAuthentication, BasicAuthentication]
#     permission_classes = [IsAuthenticated]

#     queryset = User.objects.all()
#     serializer_class = UserProfileSerializer

    # def get_queryset(self):
    #     """
    #     This view should return a list of all the purchases
    #     for the currently authenticated user.
    #     """
    #     queryset = self.queryset
    #     query_set = queryset.filter(user=self.request.user)
    #     return query_set


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


class TheCompanyViewSet(viewsets.ModelViewSet):
    authentication_classes = [JSONWebTokenAuthentication,
                              SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = TheCompany.objects.all()
    serializer_class = TheCompanySerializer

    # def get_queryset(self):
    #     """
    #     This view should return a list of all the purchases
    #     for the currently authenticated user.
    #     """
    #     queryset = self.queryset
    #     query_set = queryset.filter(user=self.request.user)
    #     return query_set


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
        try:
            user = User.objects.filter(email=request.user)
            print(user)
            map_key = TheCompany.objects.filter(name=user[0].our_company)
            print(map_key[0].id)
            map_data = Map.objects.filter(id=map_key[0].id)
            print(map_data[0].slug)
            url = map_data[0].slug + '/logbook'
            return HttpResponseRedirect(url)
        except ObjectDoesNotExist:
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
    print(slug)
    map_key = Map.objects.filter(slug=slug).values('id')
    mapdata=map_key
    query_list = Meeting.objects.all().filter(location_id=map_key[0]['id']).order_by('-date')
    # query_list_host = Host.objects.prefetch_related('relateds')
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

    
    puserdata = User.objects.filter(email=request.user).values()
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
            # "objects_all1": query_list_host,
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
            # "objects_all1": query_list_host,
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
    user = User.objects.filter(email=request.user)
    query_list = User.objects.filter(colleague=user[0].colleague)
    thecompany = TheCompany.objects.filter(name=user[0].our_company)
    print(thecompany)
    
    if request.method == 'POST':
        form2 = MeetingForm(thecompany[0], request.POST)
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

            instance2 = form2.save(commit=False)
            instance2.user = request.user
            instance2.visitor_id = instance1.pk
            instance2.save()
            form2.save_m2m()
    else:
        form = ToDoForm()
        form1 = VisitorForm()
        form2 = MeetingForm(thecompany[0])

    map_key = User.objects.filter(email=request.user)
    mapdata = Map.objects.filter(slug=slug)
    puserdata = User.objects.filter(email=request.user).values()
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


def use_old_visit(request,id=None, slug):
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
    map_key = User.objects.filter(email=request.user)
    mapdata = Map.objects.filter(slug=slug)
    puserdata = User.objects.filter(email=request.user).values()
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
    query_list = Visitor.objects.filter(user=request.user)

    query = request.GET.get("q")

    if query:
        query_list = query_list.filter(
            Q(full_name__icontains=query) |
            Q(email__icontains=query) |
            Q(company_name__icontains=query)
        )

    map_key = User.objects.filter(email=request.user)
    mapdata = Map.objects.filter(slug=slug)
    puserdata = User.objects.filter(email=request.user).values()
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


def addressbookdetail(request,id, slug):
    print(request.user)

    map_key = Map.objects.all().filter(slug=slug).values('id')
    query_list = Meeting.objects.all().filter(
        location_id=map_key[0]['id'], visitor_id=id).order_by('-date')
    # query_list_host = Host.objects.prefetch_related('relateds')
    query_list_visitor = Visitor.objects.prefetch_related('relateds')

    map_key = User.objects.filter(email=request.user)
    mapdata = Map.objects.filter(slug=slug)
    puserdata = User.objects.filter(email=request.user).values()
    if puserdata:
        image = puserdata[0]['profile_pic']
    else:
        image = puserdata
    instance = {
        'id':id,
        "query_list_visitor": query_list_visitor,
        # "objects_all1": query_list_host,
        'image': image,
        "map": mapdata,
        "objects_all": query_list,
        'slug': slug,
    }
    return render(request, 'account/addressbookdetail.html', instance)


def addressbookedit(request, id, slug):
    map_key = User.objects.filter(email=request.user)
    mapdata = Map.objects.filter(slug=slug)
    puserdata = User.objects.filter(email=request.user).values()
    if puserdata:
        image = puserdata[0]['profile_pic']
    else:
        image = puserdata
    
    idlists = request.GET.getlist("id[]")
    
    for idlist in idlists:
        id = idlist
    
    instance = get_object_or_404(Visitor, id=id)
        
    if request.method == 'POST':
        form = VisitorForm(request.POST or None,
                        request.FILES or None,instance=instance)    
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            print(form.cleaned_data.get("full_name"))
            fname = form.cleaned_data.get("full_name")
            instance.save()
            messages.success(request, "Successfully Create New Entry for " + fname)
    else:
        form = VisitorForm(instance=instance)

    instance = {
        'image': image,
        "map": mapdata,
        'form': form,
        'slug': slug,
        'id':id
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
    user = User.objects.filter(email=request.user)
    print(user[0].our_company)
    thethe = TheCompany.objects.filter(name=user[0].our_company)
    print(thethe)
    # hosts = User.objects.filter(email=request.user).values('our_company')
    query_list = User.objects.filter(our_company=thethe[0])
    print(query_list)
    query = request.GET.get("q")

    if query:
        query_list = query_list.filter(
            Q(full_name__icontains=query) |
            Q(email__icontains=query) |
            Q(mobile__icontains=query)
        )
    map_key = User.objects.filter(email=request.user)
    mapdata = Map.objects.filter(slug=slug)
    puserdata = User.objects.filter(email=request.user).values()
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
    map_key = User.objects.filter(email=request.user)
    mapdata = Map.objects.filter(slug=slug)
    puserdata = map_key.values()
    randomstring = BaseUserManager().make_random_password()

    if puserdata:
        image = puserdata[0]['profile_pic']
    else:
        image = puserdata
    if request.method == 'POST':
        print('isPost')
        form = ColleaguesForm(request.POST)
        if form.is_valid():
            print(map_key[0].our_company)
            instance = form.save(commit=False)
            instance.is_active = False
            instance.set_password(randomstring)
            instance.our_company= map_key[0].our_company
            instance.save()
            print(instance)
            fname = form.cleaned_data.get("full_name")
            
            current_site = get_current_site(request)
            print(instance.id)
            mail_subject = 'Activate your account.'
            message = render_to_string('account_active_email.html', {
                'usertocreate': instance,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(instance.pk)).decode(),
                'token': account_activation_token.make_token(instance),
            })
            to_email = form.cleaned_data.get('email')
            sender_email = EMAIL_HOST_USER

            sendmail.delay(mail_subject, message,
                           sender_email, to_email)
            
            messages.success(request, "Successfully Create New Entry for " + fname)
    else:   
        print('error')
        form = ColleaguesForm()

    instance = {
        'image': image,
        "map": mapdata,
        'form': form,
        'slug': slug,
    }
    return render(request, 'account/addnewhost.html', instance)


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
        print('1')
        logout()
        msg11 = 'Thank you for your email confirmation. Now you can login your account with username and password we genrated for you and send you in your mail.'
    else:
        msg11 = 'Activation link is invalid!'
        
    instance = {
        'msg': msg11,
    }
    return render(request, 'app/user_added.html', instance)


def user_added(request):
    return render(request, 'app/user_added.html')


def locations(request, slug):
    print(slug)
    user_form = ToDoForm()
    map_key = User.objects.filter(email=request.user)
    mapdata = Map.objects.filter(slug=slug)
    puserdata = User.objects.filter(email=request.user).values()
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


def addnewlocations(request,slug):
    print(request.user)
    form = MapForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        # fname = form.cleaned_data.get("name")
        instance.user = request.user
        instance.save()
        old_slug = Map.objects.get(id=instance.pk)
        # messages.success(request, "Successfully Create New Entry for " + fname)
        slug = old_slug.slug
    
        ismap = Map.objects.filter(name=instance.name)
        super_user = User.objects.filter(email=instance.user)
        print(super_user[0].our_company)
        thecompany = TheCompany.objects.filter(name=super_user[0].our_company)
        print(thecompany)
        exists = thecompany.exists()
        if exists:
            print(1)
            company = TheCompany.objects.get(name=super_user[0].our_company)
            print(ismap)
            print(instance)
            print(old_slug)
            company.location.add(ismap[0].id)

        context = {
            'form': form,
            'slug': slug
        }
        return render(request, 'account/logbook.html', context)
    else:
        user = User.objects.filter(email=request.user)
        map_key = TheCompany.objects.filter(name=user[0].our_company)
        if map_key[0].location.all().exists():
            mapdata = map_key[0].location.all()[0].slug
            context = {
                'Map': mapdata,
                'form': form,
            }
        else:
            context = {
                'form': form,
            }
        return render(request, 'account/addnewlocations.html', context)


def analytics(request, slug):
    print(slug)
    map_key = User.objects.filter(email=request.user)
    mapdata = Map.objects.filter(slug=slug)
    datalist = Visitor.objects.all().order_by('-date')
    puserdata = User.objects.filter(email=request.user).values()
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


def settings_general_company(request, slug):
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
    return render(request, 'account/settings/general/company.html', instance)


def settings_general_management(request, slug):
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
    return render(request, 'account/settings/general/usermanagement.html', instance)


def settings_general_rights(request, slug):
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
    return render(request, 'account/settings/general/user-rights.html', instance)


def settings_other_billing(request, slug):
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
    return render(request, 'account/settings/othersettings/billing-plan.html', instance)


def settings_other_buildingsecurity(request, slug):
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
    return render(request, 'account/settings/othersettings/building-security.html', instance)


def settings_other_integrations(request, slug):
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
    return render(request, 'account/settings/othersettings/integrations.html', instance)


def settings_other_privacy(request, slug):
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
    return render(request, 'account/settings/othersettings/privacy.html', instance)


def settings_visitslist_kiosklist(request, slug):
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
    return render(request, 'account/settings/visitslist/kiosk_list.html', instance)


def settings_visitslist_logbook(request, slug):
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
    return render(request, 'account/settings/visitslist/logbook.html', instance)


def settings_visitslist_printer(request, slug):
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
    return render(request, 'account/settings/visitslist/printer.html', instance)


def settings_visitslist_notifications(request, slug):
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
    return render(request, 'account/settings/visitslist/notifications.html', instance)


def view(request, slug):
    print(slug)

    puserdata = User.objects.filter(email=request.user).values()
    if puserdata:
        image = puserdata[0]['profile_pic']
    else:
        image = puserdata
    user = User.objects.filter(username=request.user)
    userprofile = User.objects.filter(email=request.user)
    instance = {
        'user': user,
        'userprofile': userprofile,
        'image': image,
        'slug': slug,
    }
    return render(request, 'account/profile/view.html', instance)


def edituser(request, slug):
    map_key = User.objects.filter(email=request.user)
    mapdata = Map.objects.filter(slug=slug)
    puserdata = User.objects.filter(email=request.user).values()
    
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


def edituserprofile(request, slug):
    map_key = User.objects.filter(email=request.user)
    mapdata = Map.objects.filter(slug=slug)
    puserdata = User.objects.filter(email=request.user).values()
    instance = get_object_or_404(User, user=request.user)
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


def password(request, slug):
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
    return render(request, 'account/profile/password.html', instance)
