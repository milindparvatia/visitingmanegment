from django import forms
import datetime
from .models import Visitor, Host, Map, Meeting
from bootstrap_datepicker_plus import DatePickerInput, TimePickerInput
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


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
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "password1",
            "password2"
        ]

    def save(self, commit=True):
        user = super(RegistraionForm, self).save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

        return user


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
            "comment"
        ]


class HostForm(forms.ModelForm):
    attrs = {
        'class': 'form-control'
    }

    class Meta:
        model = Host
        fields = [
            "full_name",
            "email",
            "mobile",
            "comment"
        ]


class MeetingForm(forms.ModelForm):
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
            "host",
            'start_time',
            'end_time',
            'status'
        ]
        widgets = {
            'start_time': TimePickerInput().start_of('party time'),
            'end_time': TimePickerInput().end_of('party time'),
        }
