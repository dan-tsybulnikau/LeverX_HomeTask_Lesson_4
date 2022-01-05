from django.urls import path
from .views import UserRegistrationView, UserView, LoginView, LogoutView, CourseView, SingleCourseView, LectureView, \
    LectureDetailView, HometaskView, HometaskDetailView, CompletedHomeworkView, CompletedHomeworkDetailView, MarkView, \
    MarkDetailView, CommentView, CommentDetailView

urlpatterns = [
    path('register', UserRegistrationView.as_view(), name='register'),
    path('users', UserView.as_view(), name='users'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('course', CourseView.as_view(), name='course'),
    path('course/<int:pk>', SingleCourseView.as_view(), name='detailed-course'),
    path('course/<int:course_pk>/lectures', LectureView.as_view(), name='course-lectures'),
    path('course/<int:course_pk>/lectures/<int:pk>', LectureDetailView.as_view(), name='detailed-course-lecture'),
    path('lectures/<int:lecture_pk>/hometasks', HometaskView.as_view(), name='lecture-hometask'),
    path('lectures/<int:lecture_pk>/hometasks/<int:pk>', HometaskDetailView.as_view(), name='detailed-hometask'),
    path('hometasks/<int:hometasks_pk>/completed', CompletedHomeworkView.as_view(), name='hometask-completed'),
    path('hometasks/<int:hometasks_pk>/completed/<int:pk>', CompletedHomeworkDetailView.as_view(),
         name='detailed-hometask-completed'),
    path('completed/<int:pk>/mark', MarkView.as_view(), name='marks'),
    path('completed/mark/<int:pk>', MarkDetailView.as_view(), name='detailed-mark'),
    path('completed/mark/<int:mark_pk>/comments', CommentView.as_view(), name='comments'),
    path('completed/mark/<int:mark_pk>/comments/<int:pk>', CommentDetailView.as_view(), name='detailed-comment'),
]
