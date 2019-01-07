from django import forms
from .models import Visitor,Host
from bootstrap_datepicker_plus import DatePickerInput,TimePickerInput

class ToDoForm(forms.Form):
    date = forms.DateField(
        widget=DatePickerInput(
            format='%m/%d/%Y',
            attrs={'id':'date','onchange':'myFunction()'}
        ),
        label=''
    )

class StatusForm(forms.ModelForm):
    class Meta:
        model = Visitor
        fields = [
            'status'
        ]
    
    def __init__(self, *args, **kwargs):
        super(StatusForm, self).__init__(*args, **kwargs)
        self.fields['status'].label = False
        # self.fields['status'].widget.attrs.update({'class': "ssss"})
        # self.fields['status'].widget.attrs={ 'id': '{{ip.id}}', 'class': 'myCustomClass'}

class VisitorForm(forms.ModelForm):
    date = forms.DateField(
        widget=DatePickerInput(
            format='%m/%d/%Y',
            attrs={'id':'date','onchange':'myFunction()'}
        ),
        label='Date Visiting'
    )
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
            "visiting",
            'start_time', 
            'end_time',
            'status'
            # "durations"
        ]
        widgets = {
            'start_time':TimePickerInput().start_of('party time'),
            'end_time':TimePickerInput().end_of('party time'),
        }

    def __init__(self, *args, **kwargs):
        def new_label_from_instance(self, obj):
            return obj.full_name

        super(VisitorForm, self).__init__(*args, **kwargs)
        funcType = type(self.fields['visiting'].label_from_instance)
        self.fields['visiting'].label_from_instance = funcType(new_label_from_instance, self.fields['visiting'])

    # def __init__ (self, *args, **kwargs):
    #     # # Visitor = kwargs.pop("Visitor")
    #     # super(Visitor, self).__init__(*args, **kwargs)
    #     self.fields["visiting"].widget = forms.widgets.CheckboxSelectMultiple()
    #     # self.fields["visiting"].help_text = ""
    #     # self.fields["visiting"].queryset = FoodPreference.objects.filter(franchise=brand)

class HostForm(forms.ModelForm):
    attrs={
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