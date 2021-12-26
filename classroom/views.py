from django.contrib.auth import get_user_model
from rest_framework import status, generics
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Course, Lecture, Hometask, CompletedHomework, Mark, Comment
from .permissions import (IsTeacherOrReadOnly, IsCourseTeacherOrIsEnrolledReadOnly, IsAbleToAddLecturesOrReadOnly,
                          IsAbleToAddHomeworkOrReadOnly, IsAbleToUploadSolutionOrReadOnly,
                          IsAbleToEvaluateOrEvaluatedReadOnly, IsAbleToCommentOrOwnerReadOnly)
from .serializers import (UserRegisterSerializer, UserSerializer, CourseSerializer, CourseDetailSerializer,
                          LectureSerializer, LectureDetailSerializer, HometaskSerializer, HometaskDetailSerializer,
                          CompletedHomeworkSerializer, CompletedHomeworkDetailSerializer, MarkSerializer,
                          MarkDetailSerializer, CommentSerializer, CommentDetailSerializer)


User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserRegisterSerializer


class UserView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    queryset = User.objects.all()


class LoginView(ObtainAuthToken):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        user = User.objects.get(username=username)
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            data={'token': token.key, 'user_id': user.pk, 'username': user.username},
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


class CourseView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = (IsAuthenticated, IsTeacherOrReadOnly,)

    def perform_create(self, serializer):
        creator = get_object_or_404(User, id=self.request.user.id)
        return serializer.save(creator=creator, teacher=(creator,))


class SingleCourseView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CourseDetailSerializer
    permission_classes = (IsAuthenticated, IsCourseTeacherOrIsEnrolledReadOnly,)

    def get_queryset(self):
        queryset = Course.objects.filter(id=self.kwargs['pk'])
        return queryset


class LectureView(generics.ListCreateAPIView):
    parser_class = (FileUploadParser,)
    serializer_class = LectureSerializer
    permission_classes = (IsAuthenticated, IsAbleToAddLecturesOrReadOnly,)

    def get_queryset(self):
        queryset = Lecture.objects.filter(course=self.kwargs['course_pk'])
        return queryset

    def perform_create(self, serializer):
        course = Course.objects.get(id=self.kwargs['course_pk'])
        return serializer.save(course=course)


class LectureDetailView(generics.RetrieveUpdateDestroyAPIView):
    parser_class = (FileUploadParser,)
    serializer_class = LectureDetailSerializer
    permission_classes = (IsAuthenticated, IsAbleToAddLecturesOrReadOnly,)

    def get_queryset(self):
        queryset = Lecture.objects.filter(course=self.kwargs['course_pk'])
        return queryset


class HometaskView(generics.ListCreateAPIView):
    serializer_class = HometaskSerializer
    permission_classes = (IsAuthenticated, IsAbleToAddHomeworkOrReadOnly,)

    def get_queryset(self):
        queryset = Hometask.objects.filter(lecture=self.kwargs['lecture_pk'])
        return queryset

    def perform_create(self, serializer):
        lecture = Lecture.objects.get(id=self.kwargs['lecture_pk'])
        return serializer.save(lecture=lecture)


class HometaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = HometaskDetailSerializer
    permission_classes = (IsAuthenticated, IsAbleToAddHomeworkOrReadOnly,)

    def get_queryset(self):
        queryset = Hometask.objects.filter(lecture=self.kwargs['lecture_pk'])
        return queryset


class CompletedHomeworkView(generics.ListCreateAPIView):
    serializer_class = CompletedHomeworkSerializer
    permission_classes = (IsAuthenticated, IsAbleToUploadSolutionOrReadOnly,)

    def get_queryset(self):
        user = self.request.user
        parent_course = Course.objects.get(course_lectures__hometask=self.kwargs['hometasks_pk'])
        if user in parent_course.teacher.all():
            queryset = CompletedHomework.objects.filter(hometask=self.kwargs['hometasks_pk'])
        elif user in parent_course.student.all():
            queryset = CompletedHomework.objects.filter(hometask=self.kwargs['hometasks_pk']).filter(creator=user)
        return queryset

    def perform_create(self, serializer):
        hometask = Hometask.objects.get(id=self.kwargs['hometasks_pk'])
        return serializer.save(hometask=hometask)


class CompletedHomeworkDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CompletedHomeworkDetailSerializer
    permission_classes = (IsAuthenticated, IsAbleToUploadSolutionOrReadOnly,)

    def get_queryset(self):
        queryset = CompletedHomework.objects.filter(hometask=self.kwargs['hometasks_pk'])
        return queryset


class MarkView(generics.ListCreateAPIView):
    serializer_class = MarkSerializer
    permission_classes = (IsAuthenticated, IsAbleToEvaluateOrEvaluatedReadOnly,)

    def get_queryset(self):
        queryset = Mark.objects.filter(completed_homework=self.kwargs['pk'])
        return queryset

    def perform_create(self, serializer):
        completed_homework = CompletedHomework.objects.get(id=self.kwargs['pk'])
        return serializer.save(completed_homework=completed_homework)


class MarkDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = MarkDetailSerializer
    permission_classes = (IsAuthenticated, IsAbleToEvaluateOrEvaluatedReadOnly)

    def get_queryset(self):
        queryset = Mark.objects.filter(id=self.kwargs['pk'])
        return queryset


class CommentView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated, IsAbleToCommentOrOwnerReadOnly,)

    def get_queryset(self):
        queryset = Comment.objects.filter(mark=self.kwargs['mark_pk'])
        return queryset

    def perform_create(self, serializer):
        mark = Mark.objects.get(id=self.kwargs['mark_pk'])
        return serializer.save(mark=mark)


class CommentDetailView(generics.RetrieveAPIView):
    serializer_class = CommentDetailSerializer
    permission_classes = (IsAuthenticated, IsAbleToCommentOrOwnerReadOnly,)

    def get_queryset(self):
        queryset = Comment.objects.filter(id=self.kwargs['pk'])
        return queryset
