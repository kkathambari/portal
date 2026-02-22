from rest_framework import serializers
from .models import User, Student, Faculty, Course, Enrollment, Attendance, Assessment, ExamResult, Notice

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']

class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Student
        fields = '__all__'

class FacultySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Faculty
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    faculty = FacultySerializer(read_only=True)
    faculty_id = serializers.PrimaryKeyRelatedField(
        queryset=Faculty.objects.all(), source='faculty', write_only=True, required=False, allow_null=True
    )
    class Meta:
        model = Course
        fields = '__all__'

class EnrollmentSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), source='student', write_only=True
    )
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), source='course', write_only=True
    )
    class Meta:
        model = Enrollment
        fields = '__all__'

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'

class AttendanceInlineSerializer(serializers.ModelSerializer):
    enrollment = EnrollmentSerializer(read_only=True)
    class Meta:
        model = Attendance
        fields = '__all__'

class AssessmentSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(source='course.code', read_only=True)
    class Meta:
        model = Assessment
        fields = '__all__'

class ExamResultSerializer(serializers.ModelSerializer):
    assessment = AssessmentSerializer(read_only=True)
    enrollment = EnrollmentSerializer(read_only=True)
    
    class Meta:
        model = ExamResult
        fields = '__all__'

class ExamResultWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamResult
        fields = ['enrollment', 'assessment', 'marks_obtained', 'status']

class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = '__all__'
