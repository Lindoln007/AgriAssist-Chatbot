from django import forms
from .models import GovUpdate

class GovUpdateForm(forms.ModelForm):
    class Meta:
        model = GovUpdate
        fields = ['title', 'category', 'content', 'file', 'date_posted']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter update title'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Enter detailed information about the policy or subsidy...'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            }),
            'date_posted': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
        
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if file.size > 10 * 1024 * 1024:  # 10MB limit
                raise forms.ValidationError('File size cannot exceed 10MB')
            if not file.name.endswith('.pdf'):
                raise forms.ValidationError('Only PDF files are allowed')
        return file
