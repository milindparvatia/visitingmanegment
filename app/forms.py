from django_select2.forms import Select2MultipleWidget
from django import forms
import datetime
from .models import *
from bootstrap_datepicker_plus import DatePickerInput, TimePickerInput
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()


class MapForm(forms.ModelForm):
    class Meta:
        model = Map
        fields = [
            'loc',
            'name',
            'lat',
            'lon'
        ]

    def __init__(self, *args, **kwargs):
        super(MapForm, self).__init__(*args, **kwargs)
        self.fields['loc'].label = 'Location'
        self.fields['loc'].widget.attrs = {
            'id': 'pac-input', 'class': 'form-control'}
        self.fields['name'].widget.attrs = {'id': 'name'}


class RegistraionForm(UserCreationForm):
    company_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = [
            "email",
            'full_name',
            'company_name',
            'mobile',
            "password1",
            "password2"
        ]

    # def __init__(self, *args, **kwargs):
    #     super(RegistraionForm, self).__init__(*args, **kwargs)
    #     self.fields['username'].widget.attrs['readonly'] = True
    #     self.fields['first_name'].widget.attrs = {'onkeyup': 'sync()'}
    #     self.fields['last_name'].widget.attrs = {'onkeyup': 'sync()'}

    def save(self, commit=True):
        user = super(RegistraionForm, self).save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

        return user


class ColleaguesForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "full_name",
            "email",
            "password1",
            "password2"
        ]

    def __init__(self, *args, **kwargs):
        super(ColleaguesForm, self).__init__(*args, **kwargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False


class ToDoForm(forms.Form):
    date = forms.DateField(
        widget=DatePickerInput(
            format='%Y-%m-%d',
            attrs={'id': 'date', 'onchange': 'myFunction()'}
        ),
        label='',
        initial=datetime.date.today()
    )


class StatusForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = [
            'status'
        ]

    def __init__(self, *args, **kwargs):
        super(StatusForm, self).__init__(*args, **kwargs)
        self.fields['status'].label = False
        # self.fields['status'].widget.attrs.update({'class': "ssss"})
        # self.fields['status'].widget.attrs={ 'id': '{{ip.id}}', 'class': 'myCustomClass'}


class VisitorForm(forms.ModelForm):
    class Meta:
        model = Visitor
        fields = [
            "full_name",
            "company_name",
            "email",
            "mobile",
            "licenseplate",
            "about",
            "comment",
            'profile_pic'
        ]

    def __init__(self, *args, **kwargs):
        super(VisitorForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['email'].widget.attrs['readonly'] = True


# class HostForm(forms.ModelForm):
#     attrs = {
#         'class': 'form-control'
#     }

#     class Meta:
#         model = Host
#         fields = [
#             "full_name",
#             "email",
#             "mobile",
#             "comment"
#         ]

class MeetingForm(forms.ModelForm):
    host = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(), widget=Select2MultipleWidget)
    date = forms.DateField(
        widget=DatePickerInput(
            format='%m/%d/%Y',
            attrs={'id': 'date', 'onchange': 'myFunction()'}
        ),
        label='Date Visiting'
    )

    class Meta:
        model = Meeting
        fields = [
            "status",
            "location",
            'start_time',
            'end_time',
            'status'
        ]
        widgets = {
            'start_time': TimePickerInput().start_of('party time'),
            'end_time': TimePickerInput().end_of('party time'),
        }

    def __init__(self, thecompany, *args, **kwargs):
        super(MeetingForm, self).__init__(*args, **kwargs)
        self.fields['host'].queryset = User.objects.filter(
            our_company=thecompany)

    # def __init__(self, *args, **kwargs):
    #     # Only in case we build the form from an instance
    #     # (otherwise, 'toppings' list should be empty)
    #     if kwargs.get('instance'):
    #         # We get the 'initial' keyword argument or initialize it
    #         # as a dict if it didn't exist.
    #         initial = kwargs.setdefault('initial', {})
    #         # The widget for a ModelMultipleChoiceField expects
    #         # a list of primary key for the selected data.
    #         initial['host'] = [
    #             t.pk for t in kwargs['instance'].our_company.all()]

    #     forms.ModelForm.__init__(self, *args, **kwargs)

    def save(self, commit=True):
        # Get the unsave Pizza instance
        instance = forms.ModelForm.save(self, False)

        # Prepare a 'save_m2m' method for the form,
        old_save_m2m = self.save_m2m

        def save_m2m():
            old_save_m2m()
            # This is where we actually link the pizza with hosts
            instance.host.clear()
            instance.host.add(*self.cleaned_data['host'])
        self.save_m2m = save_m2m

        # Do we need to save all changes now?
        if commit:
            instance.save()
            self.save_m2m()

        return instance


# class UserProfileForm(forms.ModelForm):
#     class Meta:
#         model = UserProfile
#         fields = [
#             'user',
#             'company_name',
#             'mobile',
#             'licenseplate',
#             'about',
#             'comment',
#             'location',
#             'profile_pic'
#         ]


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'full_name',
            'password',
            'email',
            'is_active',
            'mobile',
            'licenseplate',
            'about',
            'comment',
            'profile_pic',
            'our_company'
        ]


class SearchVisitorForm(forms.ModelForm):
    class Meta:
        model = Visitor
        fields = [
            'full_name',
            'email'
        ]
