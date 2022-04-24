from django import forms

from university.models import (
    Homework,
) 

class CreateHWForm(forms.ModelForm):
    
    class Meta:
        model = Homework 
        fields: tuple = (
            'title', 
            'subject', 
            'logo'
        )