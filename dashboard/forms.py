
from django import forms
from .models import File

class FileStatusForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['status']
