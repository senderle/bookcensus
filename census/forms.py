from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django.forms import inlineformset_factory, TextInput, formset_factory
import datetime


class ContactUs(forms.ModelForm):
    choices =(("General feedback", "General feedback"),
    ("I found an error in the data", "I found an error in the data"),
    ("I'd like to suggest a new feature", "I'd like to suggest a new feature"),
    ("I have a copy that should be in your database", "I have a copy that should be in your database"))

    subject=forms.ChoiceField(choices=choices)
    guardian=forms.CharField(widget=forms.Textarea(attrs={'class': 'guardian'}), required=False, label='')

    class Meta:
        model = ContactForm
        fields = '__all__'

class LoginForm(forms.ModelForm):
    error_messages = {'password_mismatch': "The two password fields didn't "
                      "match. Please enter both fields again.",
                      }
    password1 = forms.CharField(widget=forms.PasswordInput,
                                max_length=50,
                                min_length=6,
                                label='Password',
                                )
    password2 = forms.CharField(widget=forms.PasswordInput,
                                max_length=50,
                                min_length=6,
                                label='Password Confirmation',
                                help_text="\n Enter the same password as"
                                " above, for verification.",
                                )
    email = forms.CharField(max_length=75,
                            required=True
                            )

    class Meta:
        model = User
        fields = ['username',
                  'first_name',
                  'last_name',
                  'email',
                  'password1',
                  'password2']

    # raise an error if the entered password1 and password2 are mismatched
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return self.cleaned_data

    # raise an error if email is not an upenn email or the email is already taken
    def clean_email(self):
        data = self.cleaned_data['email']
        if data.endswith("upenn.edu"):
            if User.objects.filter(email=data).exists():
                raise forms.ValidationError("This email is already used.")
        else:
            raise forms.ValidationError("Must be a Penn email address.")
        return data

class editProfileForm(forms.ModelForm):
    email = forms.CharField(max_length=150, required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email',]


    def clean_email(self):
        data = self.cleaned_data['email']
        if data.endswith("upenn.edu"):
            if not data == self.instance.email and User.objects.filter(email=data).exists():
                raise forms.ValidationError("This email is already used.")
        else:
            raise forms.ValidationError("Must be a Penn email address.")
        return data


class copySubMissionForm(forms.ModelForm):
    # choices = forms.ModelChoiceField(queryset=Location.objects.all())
    # issue_id = forms.IntegerField(required=True)
    location = forms.ModelChoiceField(queryset=Location.objects.order_by('name'), required=False)
    Shelfmark = forms.CharField(required=True)
    Local_Notes = forms.CharField(required=True)
    Prov_info = forms.CharField(label="Provenance Information", required=True)
    Height = forms.IntegerField(initial=0, required=False, help_text="cm")
    Width = forms.IntegerField(initial=0, required=False, help_text="cm")

    class Meta:
        model = DraftCopy
        fields = ['location', 'Shelfmark', 'Local_Notes', 'Prov_info', 'Height', 'Width']


class createDraftForm(forms.ModelForm):
    issue_id = forms.IntegerField(required=True)
    location = forms.ModelChoiceField(queryset=Location.objects.all())
    Shelfmark = forms.CharField(required=True)
    Local_Notes = forms.CharField(required=True)
    Prov_info = forms.CharField(label="Provenance Information", required=True)
    Height = forms.IntegerField(initial=0, required=False, help_text="cm")
    Width = forms.IntegerField(initial=0, required=False, help_text="cm")

    class Meta:
        model = DraftCopy
        fields = ['issue_id', 'location', 'Shelfmark', 'Local_Notes', 'Prov_info', 'Height', 'Width']

class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')
    affiliation = forms.ModelChoiceField(queryset=Location.objects.all())
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
