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

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        queryset = self.queryset
        query_set = queryset.filter(id=self.request.user.id)
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
            map_data = Map.objects.filter(name=request.user.our_company.location.all()[0])
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
    mapdata = request.user.our_company.location.all()
    map_key = Map.objects.filter(slug=slug).values('id')
    query_list = Meeting.objects.all().filter(location_id=map_key[0]['id']).order_by('-date')
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

            # sendmail.delay(hostsubject, hostmessage,
            #             hostsender_email, hostreceipient_email)
            # sendmail.delay(reciversubject, recivermessage,
            #             sender_email, receipient_email)

            instance2 = form2.save(commit=False)
            instance2.our_company = request.user.our_company
            instance2.visitor_id = instance1.pk
            instance2.save()
            form2.save_m2m()
    else:
        form1 = VisitorForm()
        form2 = MeetingForm(thecompany[0])


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
            fromtime = form2.cleaned_data.get("start_time").strftime('%H:%M:%S')
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
            messages.success(request, "Successfully Create New Entry for "+name)

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


def addressbookdetail(request,id, slug):
    query_list = Meeting.objects.all().filter(visitor_id=id).order_by('-date')
    query_list_visitor = Visitor.objects.prefetch_related('relateds')

    mapdata = request.user.our_company.location.all()
    image = request.user.profile_pic

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
    mapdata = request.user.our_company.location.all()
    image = request.user.profile_pic
    
    id_lists = request.GET.getlist("id[]")
    
    for id_list in id_lists:
        id = id_list
    
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

    mapdata = request.user.our_company.location.all()
    image = request.user.profile_pic

    if request.method == 'POST':
        print('isPost')
        form = ColleaguesForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.is_active = False
            instance.set_password(randomstring)
            instance.our_company = request.user.our_company
            instance.save()
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


def addnewlocations(request,slug=None):
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
    
        company = TheCompany.objects.get(name=request.user.our_company)
        company.location.add(ismap[0].id)

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


def analytics(request, slug):
    print(slug)
    datalist = Visitor.objects.all().order_by('-date')

    mapdata = request.user.our_company.location.all()
    image = request.user.profile_pic

    instance = {
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


def edituser(request,id, slug):
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
            return redirect('../../../')
    else:
        form = UserForm(instance=request.user)
    instance = {
        'image': image,
        'form': form,
        'slug': slug,
        "map": mapdata,
    }
    return render(request, 'account/profile/edit_user.html', instance)


def password(request, slug,id):
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
        'form':form,
        'image': image,
        'slug': slug,
        "map": mapdata,
    }
    return render(request, 'account/profile/password.html', instance)
