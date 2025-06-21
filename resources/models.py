from django.db import models
from django.utils import timezone
import logging
logger = logging.getLogger(__name__)

class Year(models.Model):
    YEAR_TYPE=[
        ('Year 1','BHCS-Y-1'),
        ('Year 2','BHCS-Y-2'),
        ('Year 3','BHCS-Y-3'),
    ]
    year = models.CharField(max_length=10,choices=YEAR_TYPE)
    def __str__(self):
        return self.year
    
class Semester(models.Model):
    SEMESTER_TYPE=[
            ('Semester 1','BHCS-Y-1-S-1'),
            ('Semester 2','BHCS-Y-1-S-2'),
            ('Semester 3','BHCS-Y-2-S-3'),
            ('Semester 4','BHCS-Y-2-S-4'),
            ('Semester 5','BHCS-Y-3-S-5'),
            ('Semester 6','BHCS-Y-3-S-6'),
        ]
    semester = models.CharField(max_length=20,choices=SEMESTER_TYPE,default='Semester 1')
    year=models.ForeignKey(Year,on_delete=models.CASCADE)
    
    def __str__(self):
        return self.semester + ' | ' + str(self.year)
    


class Resource(models.Model):
    SEMESTER_SUBJECTS = {
            "semester 1 | Year 1": [
                ('Programming Fundamental & C', 'Programming Fundamental & C'),
                ('Introduction to Web and HTML', 'Introduction to Web and HTML'),
                ('Digital Electronics', 'Digital Electronics'),
                ('Maths I', 'Maths I'),
                ('Environmental Studies', 'Environmental Studies'),
                ('C/ C++ Programming Lab', 'C/ C++ Programming Lab'),
                ('Web Programming Lab', 'Web Programming Lab'),
            ],
            "semester 2 | Year 1": [
                ('Data Structure', 'Data Structure'),
                ('Maths II', 'Maths II'),
                ('Professional Communication', 'Professional Communication'),
                ('Computer Organization and Architecture', 'Computer Organization and Architecture'),
                ('Human Values and Professional Ethics', 'Human Values and Professional Ethics'),
                ('Data Structure Lab', 'Data Structure Lab'),
                ('CBNST LAB', 'CBNST LAB'),
            ],
            "semester 3 | Year 2": [
                ('Statistical Computing With R Programming', 'Statistical Computing With R Programming'),
                ('DBMS and SQL/ PLSQL', 'DBMS and SQL/ PLSQL'),
                ('Mathematics III', 'Mathematics III'),
                ('Operating System', 'Operating System'),
                ('R Programming Lab', 'R Programming Lab'),
                ('DBMS LAB', 'DBMS LAB'),
            ],
            "semester 4 | Year 2": [
                ('Java Programming', 'Java Programming'),
                ('Computer Networks', 'Computer Networks'),
                ('Design and Analysis of Algorithms', 'Design and Analysis of Algorithms'),
                ('Compiler Design', 'Compiler Design'),
                ('Java Programming Lab', 'Java Programming Lab'),
                ('Design and Analysis of Algorithms Lab', 'Design and Analysis of Algorithms Lab'),
            ],
            "semester 5 | Year 3": [
                ('Interactive Computer Graphics & Multimedia', 'Interactive Computer Graphics & Multimedia'),
                ('Software Engineering', 'Software Engineering'),
                ('Introduction to Artificial Intelligence', 'Introduction to Artificial Intelligence'),
                ('Analytical Programming Using Python Concepts', 'Analytical Programming Using Python Concepts'),
                ('Computer Graphics Lab', 'Computer Graphics Lab'),
            ],
            "semester 6 | Year 3": [
                ('IoT & Cloud Computing', 'IoT & Cloud Computing'),
                ('Information Security & Cyber Laws', 'Information Security & Cyber Laws'),
                ('Soft Computing', 'Soft Computing'),
                ('Data Science and Machine Learning Techniques', 'Data Science and Machine Learning Techniques'),
            ],
        }
    
    subject = models.CharField(max_length=100, choices=SEMESTER_SUBJECTS,blank=True,  # allow blank in admin form
    null=True  )
    
    RESOURCE_TYPE=[
        ('PYQs','Previous Year Question Paper'),
        ('BOOK','BOOK'),
        ('Youtube Video URL','Youtube Video URL'),
        ('Syllabus','Syllabus'),
        
    ]
    resource_type = models.CharField(max_length=20,choices=RESOURCE_TYPE)
    resource_file = models.FileField(upload_to='PDF/', blank=True, null=True)
    resource_file_year = models.IntegerField(choices=[(year, year) for year in range(2019, 2031)], blank=True, null=True)
    is_ignored = models.BooleanField(default=False)  # Add this field
    resource_url = models.URLField(blank=True, null=True)
    semester=models.ForeignKey(Semester,on_delete=models.CASCADE)
    created_at = models.DateField(default=timezone.now)
    url_source=models.CharField(max_length=100, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if self.resource_type == 'Youtube Video URL':
            self.resource_file = None
            self.resource_file_year = None
        elif self.resource_type in ['PYQs', 'BOOK']:
            self.resource_url = None
        elif self.resource_type == 'BOOK':
            self.resource_file_year = None
            self.resource_url = None
        elif self.resource_type == 'Syllabus':
            self.resource_file_year = None
            self.resource_url = None
            self.subject= None
        super().save(*args, **kwargs)
        
        if self.resource_file and hasattr(self.resource_file, 'name'):
            logger.info(f"Uploading file: {self.resource_file.name}")
        else:
            logger.info("No file uploaded.")
    
    def __str__(self):
        subject = self.subject if self.subject else 'No Subject'
        resource_year = self.resource_file_year if self.resource_file_year else 'N/A'
        return f"{subject} | {self.resource_type} | {resource_year} | {self.semester} | {self.created_at}"

        
    
    
