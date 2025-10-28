from django import forms
from .models import TutoringRoom

class TutoringRoomForm(forms.ModelForm):
    class Meta:
        model = TutoringRoom
        fields = ['subject']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter subject (e.g., Agriculture)'
            }),
        }
