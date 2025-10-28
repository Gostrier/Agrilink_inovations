from django import forms
from .models import Note
from .models import SoilTest, CropDisease
from .models import Listing

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'file']
        # widgets = {
        #     'title': forms.TextInput(attrs={
        #         'class': 'w-full p-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none',
        #         'placeholder': 'Enter note title...'
        #     }),
        #     'subject': forms.Select(attrs={
        #         'class': 'Aw-full p-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none'
        #     }),
        #     'level': forms.Select(attrs={
        #         'class': 'w-full p-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none'
        #     }),
        #     'file': forms.ClearableFileInput(attrs={
        #         'class': 'w-full p-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none'
        #     }),
        # }


class SoilTestForm(forms.ModelForm):
    class Meta:
        model = SoilTest
        fields = ["image"]


class CropDiseaseForm(forms.ModelForm):
    class Meta:
        model = CropDisease
        fields = ["image"]



