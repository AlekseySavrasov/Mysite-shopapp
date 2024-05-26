from django import forms
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile


def validate_file_name(file: InMemoryUploadedFile) -> None:
    if file.name and "virus" in file.name:
        raise ValidationError("File name shouldn't contain 'virus'")


def validate_file_size(file: InMemoryUploadedFile) -> None:
    if file.size > 10 ** 6:
        raise ValidationError("File-size should be less than 1Kb")


class UserBioForm(forms.Form):
    name = forms.CharField(max_length=100)
    age = forms.IntegerField(label="Age", min_value=1, max_value=99)
    bio = forms.CharField(label="Biography", widget=forms.Textarea)


class UploadFileForm(forms.Form):
    file = forms.FileField(validators=[validate_file_name, validate_file_size])
