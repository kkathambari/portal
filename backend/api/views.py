from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
import django_filters.rest_framework as django_filters
from .models import User, Student, Faculty, Course, Enrollment, Attendance, Assessment, ExamResult, Notice
from .serializers import (
    UserSerializer, StudentSerializer, FacultySerializer, CourseSerializer,
    EnrollmentSerializer, AttendanceSerializer, AttendanceInlineSerializer, 
    AssessmentSerializer, ExamResultSerializer, ExamResultWriteSerializer, NoticeSerializer
)

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.role == User.Role.ADMIN:
            return True
        return request.method in permissions.SAFE_METHODS

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == User.Role.ADMIN

class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == User.Role.STUDENT
        
class IsFaculty(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == User.Role.FACULTY

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.STUDENT:
            return Student.objects.filter(user=user)
        return super().get_queryset()

class FacultyViewSet(viewsets.ModelViewSet):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    permission_classes = [permissions.IsAuthenticated]

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.FACULTY:
            # Faculty can view their assigned courses
            return Course.objects.filter(faculty__user=user)
        elif user.role == User.Role.STUDENT:
            # Students can view courses they are enrolled in
            return Course.objects.filter(enrollments__student__user=user)
        # Admins, HOD, EXAM_CELL can view all
        return super().get_queryset()

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [django_filters.DjangoFilterBackend]
    filterset_fields = ['student', 'course', 'semester']

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.STUDENT:
            return Enrollment.objects.filter(student__user=user)
        elif user.role == User.Role.FACULTY:
            return Enrollment.objects.filter(course__faculty__user=user)
        return super().get_queryset()

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [django_filters.DjangoFilterBackend]
    filterset_fields = ['enrollment', 'date', 'status']

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return AttendanceInlineSerializer
        return AttendanceSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.STUDENT:
            return Attendance.objects.filter(enrollment__student__user=user)
        elif user.role == User.Role.FACULTY:
            return Attendance.objects.filter(enrollment__course__faculty__user=user)
        return super().get_queryset()

    def perform_create(self, serializer):
        enrollment_id = self.request.data.get('enrollment')
        try:
            enrollment = Enrollment.objects.get(id=enrollment_id)
            if self.request.user.role == User.Role.FACULTY and enrollment.course.faculty.user != self.request.user:
                raise PermissionDenied("You can only mark attendance for your assigned courses.")
            serializer.save()
        except Enrollment.DoesNotExist:
            pass # handled by serializer validation

class AssessmentViewSet(viewsets.ModelViewSet):
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [django_filters.DjangoFilterBackend]
    filterset_fields = ['course']

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.STUDENT:
            return Assessment.objects.filter(course__enrollments__student__user=user)
        elif user.role == User.Role.FACULTY:
            return Assessment.objects.filter(course__faculty__user=user)
        return super().get_queryset()

    def perform_create(self, serializer):
        course_id = self.request.data.get('course')
        try:
            course = Course.objects.get(id=course_id)
            if self.request.user.role == User.Role.FACULTY and course.faculty.user != self.request.user:
                 raise PermissionDenied("You can only create assessments for your assigned courses.")
            serializer.save()
        except Course.DoesNotExist:
             pass

class ExamResultViewSet(viewsets.ModelViewSet):
    queryset = ExamResult.objects.all()
    serializer_class = ExamResultSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [django_filters.DjangoFilterBackend]
    filterset_fields = ['enrollment', 'assessment', 'status']

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return ExamResultSerializer
        return ExamResultWriteSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.STUDENT:
            # Students can only see PUBLISHED results
            return ExamResult.objects.filter(
                enrollment__student__user=user,
                status=ExamResult.Status.PUBLISHED
            )
        elif user.role == User.Role.FACULTY:
            # Faculty can see results for their courses
            return ExamResult.objects.filter(
                assessment__course__faculty__user=user
            )
        return super().get_queryset()

    def perform_create(self, serializer):
        user = self.request.user
        assessment_id = self.request.data.get('assessment')
        try:
            assessment = Assessment.objects.get(id=assessment_id)
            
            # Faculty checks
            if user.role == User.Role.FACULTY:
                if assessment.course.faculty.user != user:
                    raise PermissionDenied("Not assigned to this course.")
                serializer.save(status=ExamResult.Status.DRAFT)
            # Exam Cell checks
            elif user.role == User.Role.EXAM_CELL:
                serializer.save()
            else:
                raise PermissionDenied("You don't have permission to create results.")
                
        except Assessment.DoesNotExist:
             pass

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def submit_for_approval(self, request, pk=None):
        result = self.get_object()
        if request.user.role != User.Role.FACULTY or result.assessment.course.faculty.user != request.user:
            raise PermissionDenied("Only assigned faculty can submit.")
        
        if result.status != ExamResult.Status.DRAFT:
            return Response({'detail': 'Result is not in draft status.'}, status=status.HTTP_400_BAD_REQUEST)
            
        result.status = ExamResult.Status.SUBMITTED
        result.save()
        return Response({'status': 'Result submitted for approval.'})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def approve(self, request, pk=None):
        if request.user.role not in [User.Role.EXAM_CELL, User.Role.ADMIN]:
             raise PermissionDenied("Only Exam Cell or Admin can approve.")
             
        result = self.get_object()
        if result.status != ExamResult.Status.SUBMITTED:
            return Response({'detail': 'Result must be submitted by faculty first.'}, status=status.HTTP_400_BAD_REQUEST)
            
        result.status = ExamResult.Status.APPROVED
        result.save()
        return Response({'status': 'Result approved.'})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def publish(self, request, pk=None):
        if request.user.role not in [User.Role.EXAM_CELL, User.Role.ADMIN]:
             raise PermissionDenied("Only Exam Cell or Admin can publish.")
             
        result = self.get_object()
        if result.status != ExamResult.Status.APPROVED:
            return Response({'detail': 'Result must be approved before publishing.'}, status=status.HTTP_400_BAD_REQUEST)
            
        result.status = ExamResult.Status.PUBLISHED
        result.save()
        return Response({'status': 'Result published.'})


class NoticeViewSet(viewsets.ModelViewSet):
    queryset = Notice.objects.all().order_by('-date_posted')
    serializer_class = NoticeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        # Admins see all
        if user.role == User.Role.ADMIN:
             return queryset
             
        # Filter based on target_roles. 
        # A simple string matching for now. In a real app we might use ArrayField or ManyToMany
        user_role_str = str(user.role)
        return queryset.filter(target_roles__contains=user_role_str) | queryset.filter(target_roles__icontains='ALL')

    def perform_create(self, serializer):
        if self.request.user.role not in [User.Role.ADMIN, User.Role.HOD]:
             raise PermissionDenied("Only Admins and HODs can post notices.")
        serializer.save()
