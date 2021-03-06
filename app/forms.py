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
            'full_name',
            'company_name',
            "email",
            "password1",
            "password2",
            'mobile',
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
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            "full_name",
            "password1",
            "password2",
            'user_type'
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


class NumberOFVisitorForm(forms.Form):
    id = forms.IntegerField(max_value=10, min_value=1, label='')


class M2MVisitorForm(forms.Form):
    visitor = forms.ModelMultipleChoiceField(
        queryset=Visitor.objects.all(), widget=Select2MultipleWidget)

    def __init__(self, thecompany, *args, **kwargs):
        super(M2MVisitorForm, self).__init__(*args, **kwargs)
        print(thecompany)
        self.fields['visitor'].queryset = Visitor.objects.filter(
            our_company=thecompany)


class AdminMeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = '__all__'


class GroupVisitorForm(forms.ModelForm):
    class Meta:
        model = Visitor
        fields = [
            "full_name",
            "company_name",
            "email",
        ]


class VisitorForm(forms.ModelForm):
    profile_pic = forms.ImageField(label='Visitor Logo', required=False,
                                   widget=forms.FileInput)

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


class MeetingForm(forms.ModelForm):
    host = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(), widget=Select2MultipleWidget)
    location = forms.ModelChoiceField(queryset=TheCompany.objects.all())
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
            'date',
            "status",
            'start_time',
            'pre_registered',
            'end_time',
            'status',
        ]
        widgets = {
            'start_time': TimePickerInput().start_of('party time'),
            'end_time': TimePickerInput().end_of('party time'),
        }

    def __init__(self, thecompany, *args, **kwargs):
        super(MeetingForm, self).__init__(*args, **kwargs)
        self.fields['pre_registered'].label = 'Directly Check-In'
        self.fields['date'].required = False
        self.fields['start_time'].required = False
        self.fields['end_time'].required = False
        self.fields['host'].queryset = User.objects.filter(
            our_company=thecompany)
        self.fields['location'].queryset = Map.objects.filter(
            related_maps=thecompany)

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

        # forms.ModelForm.__init__(self, *args, **kwargs)

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


class UserForm(forms.ModelForm):
    profile_pic = forms.ImageField(label='User Logo', required=False,
                                   widget=forms.FileInput)

    class Meta:
        model = User
        fields = [
            'full_name',
            'email',
            'is_active',
            'mobile',
            'licenseplate',
            'about',
            'comment',
            'profile_pic',
        ]


class SearchVisitorForm(forms.ModelForm):
    class Meta:
        model = Visitor
        fields = [
            'full_name',
            'email'
        ]
