from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    UserViewSet, StudentViewSet, FacultyViewSet, CourseViewSet,
    EnrollmentViewSet, AttendanceViewSet, AssessmentViewSet, ExamResultViewSet, NoticeViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'students', StudentViewSet)
router.register(r'faculty', FacultyViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'enrollments', EnrollmentViewSet)
router.register(r'attendance', AttendanceViewSet)
router.register(r'assessments', AssessmentViewSet)
router.register(r'results', ExamResultViewSet)
router.register(r'notices', NoticeViewSet)

urlpatterns = [
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]
