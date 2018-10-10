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

class EditProfileForm(forms.ModelForm):
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


class LibrarianCopySubmissionForm(forms.ModelForm):
    Shelfmark = forms.CharField(label="Shelfmark", required=True)
    Local_Notes = forms.CharField(label="Local Notes", widget=forms.Textarea, required=True)
    prov_info = forms.CharField(label="Provenance Information", widget=forms.Textarea, required=True)
    Height = forms.IntegerField(label="Height (cm)", initial=0, required=False)
    Width = forms.IntegerField(label="Width (cm)", initial=0, required=False)
    Marginalia = forms.CharField(label="Marginalia", widget=forms.Textarea, required=False)
    Binding = forms.CharField(label="Binding", required=False)
    Binder = forms.CharField(label="Binder", required=False)

    class Meta:
        model = DraftCopy
        fields = ['Shelfmark', 'Local_Notes', 'prov_info', 
                  'Height', 'Width', 'Marginalia', 'Binding', 'Binder']

class AdminCopySubmissionForm(forms.ModelForm):
    location = forms.ModelChoiceField(queryset=Location.objects.order_by('name'), required=True)
    Shelfmark = forms.CharField(label="Shelfmark", required=True)
    Local_Notes = forms.CharField(label="Local Notes", widget=forms.Textarea, required=True)
    prov_info = forms.CharField(label="Provenance Information", widget=forms.Textarea, required=True)
    Height = forms.IntegerField(label="Height (cm)", initial=0, required=False)
    Width = forms.IntegerField(label="Width (cm)", initial=0, required=False)
    Marginalia = forms.CharField(label="Marginalia", widget=forms.Textarea, required=False)
    Binding = forms.CharField(label="Binding", required=False)
    Binder = forms.CharField(label="Binder", required=False)

    class Meta:
        model = CanonicalCopy
        fields = ['location', 'Shelfmark', 'Local_Notes', 'prov_info', 
                  'Height', 'Width', 'Marginalia', 'Binding', 'Binder']

class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')
    affiliation = forms.ModelChoiceField(queryset=Location.objects.order_by('name'), required=True)
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
