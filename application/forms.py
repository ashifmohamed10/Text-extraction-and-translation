from django import forms
from application.models import ImageUpload,PdfUpload,TextUpload,AudioUpload

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model=ImageUpload
        fields="__all__"

class PdfUploadForm(forms.ModelForm):
    class Meta:
        model=PdfUpload
        fields="__all__"

class TextUploadForm(forms.ModelForm):
    class Meta:
        model=TextUpload
        fields="__all__"

class AudioUploadForm(forms.ModelForm):
    class Meta:
        model=AudioUpload
        fields="__all__"


