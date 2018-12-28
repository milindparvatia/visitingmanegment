from django import forms
from .models import Visit,Visitor,Host
from bootstrap_datepicker_plus import DatePickerInput
from django import forms

class ToDoForm(forms.Form):
    date = forms.DateField(
        widget=DatePickerInput(
            format='%m/%d/%Y',
            attrs={'id':'date','onchange':'myFunction()'}
        ),
        label=''
    )

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
            "visiting"
        ]

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

class VisitForm(forms.ModelForm):
    attrs={
        'class': 'form-control'
    }
    class Meta:
        model = Visit
        fields = [
            "visitor",
            "host",
            "visit",
            "invite_reason"
        ]