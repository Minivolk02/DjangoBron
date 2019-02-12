from django import forms

class UserForm(forms.Form):
    name = forms.CharField(label="Имя", required=True , widget=forms.TextInput(attrs={"size": "50px", "placeholder": "Введите свое имя"}))
    email = forms.EmailField(label="Email", required=True , widget=forms.TextInput(attrs={"size": "50px", "placeholder": "Введите свой email"}))
    booked = forms.CharField(label="", widget=forms.HiddenInput())
    error_css_class = "error"
class HiddenForm(forms.Form):
    booked = forms.CharField(label="", widget=forms.HiddenInput())