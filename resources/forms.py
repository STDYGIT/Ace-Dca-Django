from django import forms
from .models import Resource

class ResourceUploadForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = [
            'semester',
            'subject',
            'resource_type',
            'resource_file',
            'resource_file_year',
            'resource_url',
            'url_source',
        ]
        widgets = {
            'semester': forms.HiddenInput(),  # prefilled from URL
            'subject': forms.TextInput(attrs={'readonly': True}),
            'resource_file_year': forms.NumberInput(attrs={'placeholder': 'e.g. 2024'}),
            'resource_url': forms.URLInput(attrs={'placeholder': 'https://...'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        rtype = cleaned_data.get("resource_type")

        # Basic rules
        if rtype == "PYQs":
            if not cleaned_data.get("resource_file_year"):
                self.add_error("resource_file_year", "Year is required for PYQs")
            if not cleaned_data.get("resource_file"):
                self.add_error("resource_file", "Upload file is required for PYQs")
            cleaned_data["resource_url"] = None

        elif rtype == "BOOK":
            if not cleaned_data.get("resource_file"):
                self.add_error("resource_file", "Book file is required")
            cleaned_data["resource_file_year"] = None
            cleaned_data["resource_url"] = None

        elif rtype == "Youtube Video URL":
            if not cleaned_data.get("resource_url"):
                self.add_error("resource_url", "YouTube URL is required")
            cleaned_data["resource_file"] = None
            cleaned_data["resource_file_year"] = None

        elif rtype == "Syllabus":
            cleaned_data["subject"] = None
            cleaned_data["resource_file_year"] = None
            cleaned_data["resource_url"] = None

        return cleaned_data
