from django.contrib import admin
from .models import Year, Semester, Resource
from django import forms
class ResourceAdminForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Only if a semester is selected (during editing)
        if self.instance and self.instance.semester_id:
            sem = self.instance.semester
            key = f"{sem.semester.lower()} | {sem.year.year}"
            subject_choices = dict(Resource.SEMESTER_SUBJECTS).get(key, [])
            self.fields['subject'].widget = forms.Select(choices=subject_choices)
            
    

class ResourceAdmin(admin.ModelAdmin):
    list_display = ('subject','semester' ,'resource_type','resource_file_year')
    list_filter = ('semester','resource_type')
    
    
admin.site.register(Year)
admin.site.register(Semester)
admin.site.register(Resource, ResourceAdmin)
# admin.site.register(Subject)
