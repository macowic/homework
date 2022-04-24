from django import forms

from university.models import (
    Homework,
    File,
)


class HomeworkForm(forms.ModelForm):

    class Meta:
        model = Homework
        fields = (
            'title',
            'subject',
            'logo',
        )


class FileForm(forms.ModelForm):

    class Meta:
        model = File
        fields = (
            'title',
            'obj',
            'is_checked',
        )
