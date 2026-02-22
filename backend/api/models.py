from django.db import models
from django.contrib.auth.models import AbstractUser
from auditlog.registry import auditlog

class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'STUDENT', 'Student'
        FACULTY = 'FACULTY', 'Faculty'
        HOD = 'HOD', 'HOD/Coordinator'
        EXAM_CELL = 'EXAM_CELL', 'Examination Cell'
        ADMIN = 'ADMIN', 'Administrator'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

# Audit log registry
auditlog.register(User)

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    roll_number = models.CharField(max_length=20, unique=True)
    batch = models.CharField(max_length=10)
    branch = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.roll_number})"

auditlog.register(Student)

class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='faculty_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.employee_id})"

auditlog.register(Faculty)

class Course(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    credits = models.IntegerField()
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')

    def __str__(self):
        return f"{self.code} - {self.name}"

auditlog.register(Course)

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    semester = models.IntegerField()

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student} enrolled in {self.course}"

auditlog.register(Enrollment)

class Attendance(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.BooleanField(default=False) # True for Present, False for Absent

    class Meta:
        unique_together = ('enrollment', 'date')

    def __str__(self):
        return f"{self.enrollment} on {self.date}: {'Present' if self.status else 'Absent'}"

auditlog.register(Attendance)

class Assessment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assessments')
    name = models.CharField(max_length=50) # e.g., Midterm 1, Final
    max_marks = models.DecimalField(max_digits=5, decimal_places=2)
    weightage = models.DecimalField(max_digits=5, decimal_places=2) # e.g., 20.00 for 20%

    def __str__(self):
        return f"{self.course} - {self.name}"

auditlog.register(Assessment)

class ExamResult(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        SUBMITTED = 'SUBMITTED', 'Submitted'
        APPROVED = 'APPROVED', 'Approved (Exam Cell)'
        PUBLISHED = 'PUBLISHED', 'Published'

    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='exam_results')
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    class Meta:
        unique_together = ('enrollment', 'assessment')

    def __str__(self):
        return f"{self.enrollment} - {self.assessment}: {self.marks_obtained}"

auditlog.register(ExamResult)

class Notice(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    target_roles = models.CharField(max_length=100, help_text="Comma-separated list of roles, or 'ALL'")

    def __str__(self):
        return self.title

auditlog.register(Notice)
