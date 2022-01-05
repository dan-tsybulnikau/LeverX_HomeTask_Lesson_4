import json
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from rest_framework import status
from .models import User, Course, Lecture, Hometask, CompletedHomework, Mark, Comment
from .views import (UserRegistrationView, UserView, CourseView, SingleCourseView, LectureView, LectureDetailView,
                    HometaskView, HometaskDetailView, CompletedHomeworkView, CompletedHomeworkDetailView, MarkView,
                    MarkDetailView, CommentView, CommentDetailView)

TEST_TEACHER_1 = {
    'username': 'teacher1',
    'password': 'teacher1',
    'first_name': 'teacher1',
    'last_name': 'teacher1',
    'email': 'teacher1@teacher.com',
    'registration_role': 'T'
}
TEST_TEACHER_2 = {
    'username': 'teacher2',
    'password': 'teacher2',
    'first_name': 'teacher2',
    'last_name': 'teacher2',
    'email': 'teacher2@teacher.com',
    'registration_role': 'T'
}
TEST_STUDENT_1 = {
    'username': 'student1',
    'password': 'student1',
    'first_name': 'student1',
    'last_name': 'student1',
    'email': 'student1@student.ru',
    'registration_role': 'S'
}
TEST_STUDENT_2 = {
    'username': 'student2',
    'password': 'student2',
    'first_name': 'student2',
    'last_name': 'student2',
    'email': 'student2@student.ru',
    'registration_role': 'S'
}
TEST_BAD_USER = {
    'username': '1',
    'password': 'test',
    'first_name': 'S',
    'last_name': 'W',
    'email': 'dan@mail.',
    'registration_role': 'S'
}
TEST_USER = {
    'username': 'testuser',
    'password': 'testuser',
    'first_name': 'testuser',
    'last_name': 'testuser',
    'email': 'testuser@testuser.ru',
    'registration_role': 'S'
}
TEST_COURSE = {
    'title': 'Test_course',
    'description': 'Test_description',
}
TEST_LECTURE = {
    'title': 'Test Lecture',
    'presentation': SimpleUploadedFile("test.txt", b"these are the file contents!")
}
TEST_HOMETASK = {
    'title': 'Test_hometask',
    'description': 'Test_hometask',
}


class TestUsers(APITestCase):

    @classmethod
    def setUpClass(cls):
        super(TestUsers, cls).setUpClass()
        cls.test_teacher_1 = TEST_TEACHER_1
        cls.test_teacher_2 = TEST_TEACHER_2
        cls.test_student_1 = TEST_STUDENT_1
        cls.test_student_2 = TEST_STUDENT_2
        cls.test_bad_user = TEST_BAD_USER
        cls.test_user = TEST_USER

    def setUp(self):
        self.factory = APIRequestFactory()
        self.teacher_user_1 = User.objects._create_user(**self.test_teacher_1)
        self.student_user_1 = User.objects._create_user(**self.test_student_1)
        self.teacher_user_2 = User.objects._create_user(**self.test_teacher_2)
        self.student_user_2 = User.objects._create_user(**self.test_student_2)

    def test_create_account(self):
        view = UserRegistrationView.as_view()
        request = self.factory.post(
            reverse('register'),
            data=json.dumps(self.test_user),
            content_type='application/json',
        )
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_account_with_wrong_data(self):
        view = UserRegistrationView.as_view()
        request = self.factory.post(
            reverse('register'),
            data=json.dumps(self.test_bad_user),
            content_type='application/json',
        )
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_account_with_wrong_method(self):
        view = UserRegistrationView.as_view()
        request = self.factory.get(reverse('register'))
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_unauthorized_usage(self):
        view = UserView.as_view()
        request = self.factory.get(reverse('users'))
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_users_view(self):
        user = User.objects.get(username='teacher1')
        view = UserView.as_view()
        request = self.factory.get(reverse('users'))
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestCourseCreate(APITestCase):
    @classmethod
    def setUpClass(cls):
        super(TestCourseCreate, cls).setUpClass()
        cls.test_teacher_1 = TEST_TEACHER_1
        cls.test_student_1 = TEST_STUDENT_1
        cls.teacher_user_1 = User.objects._create_user(**cls.test_teacher_1)
        cls.student_user_1 = User.objects._create_user(**cls.test_student_1)

    def setUp(self):
        self.factory = APIRequestFactory()

    def test_course_creation(self):
        user = User.objects.get(username='teacher1')
        view = CourseView.as_view()
        request = self.factory.post(
            reverse('course'),
            data=json.dumps({'title': 'Test_course', 'description': 'Test_description'}),
            content_type='application/json',
        )
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        course_view = SingleCourseView.as_view()
        request = self.factory.get(reverse('detailed-course', kwargs={'pk': 1}))
        force_authenticate(request, user=user)
        response = course_view(request, pk=1)
        self.assertIn(user.id, json.loads(response.render().content)['teacher'])

    def test_course_creation_forbidden(self):
        user = User.objects.get(username='student1')
        view = CourseView.as_view()
        request = self.factory.post(
            reverse('course'),
            data=json.dumps({'title': 'Test_course', 'description': 'Test_description'}),
            content_type='application/json',
        )
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestCourseView(APITestCase):

    @classmethod
    def setUpClass(cls):
        super(TestCourseView, cls).setUpClass()
        cls.test_teacher_1 = TEST_TEACHER_1
        cls.test_student_1 = TEST_STUDENT_1
        cls.test_student_2 = TEST_STUDENT_2
        cls.teacher_user_1 = User.objects._create_user(**cls.test_teacher_1)
        cls.student_user_1 = User.objects._create_user(**cls.test_student_1)
        cls.student_user_2 = User.objects._create_user(**cls.test_student_2)
        cls.test_course = Course(**TEST_COURSE, creator=cls.teacher_user_1)
        cls.test_course.save()

    def setUp(self):
        self.factory = APIRequestFactory()

    def test_course_view(self):
        user = User.objects.get(username='teacher1')
        view = CourseView.as_view()
        request = self.factory.get(reverse('course'))
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_course_view_forbidden_method(self):
        user = User.objects.get(username='teacher1')
        view = CourseView.as_view()
        request = self.factory.delete(reverse('course'))
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_student_can_see_course_details(self):
        user = User.objects.get(username='student1')
        course = Course.objects.get(id=1)
        course.student.add(user)
        course_view = SingleCourseView.as_view()
        request = self.factory.get(reverse('detailed-course', kwargs={'pk': 1}))
        force_authenticate(request, user=user)
        response = course_view(request, pk=1)
        self.assertIn(user.id, json.loads(response.render().content)['student'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_foreign_student_cant_see_course_details(self):
        user = User.objects.get(username='student2')
        course_view = SingleCourseView.as_view()
        request = self.factory.get(reverse('detailed-course', kwargs={'pk': 1}))
        force_authenticate(request, user=user)
        response = course_view(request, pk=1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestLectureCreate(APITestCase):
    test_teacher_1 = None

    @classmethod
    def setUpClass(cls):
        super(TestLectureCreate, cls).setUpClass()
        cls.test_teacher_1 = TEST_TEACHER_1
        cls.test_student_1 = TEST_STUDENT_1
        cls.test_student_2 = TEST_STUDENT_2
        cls.teacher_user_1 = User.objects._create_user(**cls.test_teacher_1)
        cls.student_user_1 = User.objects._create_user(**cls.test_student_1)
        cls.student_user_2 = User.objects._create_user(**cls.test_student_2)
        cls.test_course = Course(**TEST_COURSE, creator=cls.teacher_user_1)
        cls.test_course.save()

    def setUp(self):
        self.factory = APIRequestFactory()

    def test_lecture_creation(self):
        user = User.objects.get(username='teacher1')
        view = LectureView.as_view()
        course = Course.objects.get(id=1)
        course.teacher.add(user)
        request = self.factory.post(
            reverse('course-lectures', kwargs={'course_pk': 1}),
            data={
                'title': 'Test Lecture',
                'description': 'Test_description',
                'creator': user,
                'course': course,
                'presentation': SimpleUploadedFile("test.txt", b"these are the file contents!"),
            },
        )
        force_authenticate(request, user=user)
        response = view(request, course_pk=1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_lecture_creation_forbidden(self):
        user = User.objects.get(username='student1')
        view = LectureView.as_view()
        course = Course.objects.get(id=1)
        request = self.factory.post(
            reverse('course-lectures', kwargs={'course_pk': 1}),
            data={
                'title': 'Test Lecture',
                'description': 'Test_description',
                'creator': user,
                'course': course,
                'presentation': SimpleUploadedFile("test.txt", b"these are the file contents!"),
            },
        )
        force_authenticate(request, user=user)
        response = view(request, course_pk=1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestLectureView(APITestCase):

    @classmethod
    def setUpClass(cls):
        super(TestLectureView, cls).setUpClass()
        cls.test_teacher_1 = TEST_TEACHER_1
        cls.test_student_1 = TEST_STUDENT_1
        cls.test_student_2 = TEST_STUDENT_2
        cls.teacher_user_1 = User.objects._create_user(**cls.test_teacher_1)
        cls.student_user_1 = User.objects._create_user(**cls.test_student_1)
        cls.student_user_2 = User.objects._create_user(**cls.test_student_2)
        cls.test_course = Course(**TEST_COURSE, creator=cls.teacher_user_1)
        cls.test_course.save()
        cls.course = Course.objects.get(id=1)
        cls.course.teacher.add(cls.teacher_user_1)
        cls.test_lecture = Lecture(creator=cls.teacher_user_1, course=cls.course, **TEST_LECTURE)
        cls.test_lecture.save()

    def setUp(self):
        self.factory = APIRequestFactory()

    def test_lecture_view(self):
        user = User.objects.get(username='teacher1')
        view = LectureView.as_view()
        request = self.factory.get(reverse('course-lectures', kwargs={'course_pk': 1}))
        force_authenticate(request, user=user)
        response = view(request, course_pk=1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_course_view_forbidden_method(self):
        user = User.objects.get(username='teacher1')
        view = LectureView.as_view()
        request = self.factory.delete(reverse('course-lectures', kwargs={'course_pk': 1}))
        force_authenticate(request, user=user)
        response = view(request, course_pk=1)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_student_can_see_lectures_and_its_details(self):
        user = User.objects.get(username='student1')
        course = Course.objects.get(id=1)
        course.student.add(user)
        lecture_view = LectureView.as_view()
        request = self.factory.get(reverse('course-lectures', kwargs={'course_pk': 1}))
        force_authenticate(request, user=user)
        response = lecture_view(request, course_pk=1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        lecture_detail_view = LectureDetailView.as_view()
        request = self.factory.get(reverse('detailed-course-lecture', kwargs={'course_pk': 1, 'pk': 1}))
        force_authenticate(request, user=user)
        response = lecture_detail_view(request, course_pk=1, pk=1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_foreign_student_cant_see_lecture_and_its_details(self):
        user = User.objects.get(username='student2')
        lecture_view = LectureView.as_view()
        request = self.factory.get(reverse('course-lectures', kwargs={'course_pk': 1}))
        force_authenticate(request, user=user)
        response = lecture_view(request, course_pk=1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        lecture_detail_view = LectureDetailView.as_view()
        request = self.factory.get(reverse('detailed-course-lecture', kwargs={'course_pk': 1, 'pk': 1}))
        force_authenticate(request, user=user)
        response = lecture_detail_view(request, course_pk=1, pk=1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestHometaskCreate(APITestCase):

    @classmethod
    def setUpClass(cls):
        super(TestHometaskCreate, cls).setUpClass()
        cls.test_teacher_1 = TEST_TEACHER_1
        cls.test_student_1 = TEST_STUDENT_1
        cls.test_student_2 = TEST_STUDENT_2
        cls.teacher_user_1 = User.objects._create_user(**cls.test_teacher_1)
        cls.student_user_1 = User.objects._create_user(**cls.test_student_1)
        cls.student_user_2 = User.objects._create_user(**cls.test_student_2)
        cls.test_course = Course(creator=cls.teacher_user_1, **TEST_COURSE)
        cls.test_course.save()
        cls.test_lecture = Lecture(creator=cls.teacher_user_1, course=Course.objects.get(id=1), **TEST_LECTURE)
        cls.test_lecture.save()

    def setUp(self):
        self.factory = APIRequestFactory()

    def test_hometask_creation(self):
        user = User.objects.get(username='teacher1')
        view = HometaskView.as_view()
        course = Course.objects.get(id=1)
        course.teacher.add(user)
        lecture = Lecture.objects.get(id=1)
        request = self.factory.post(
            reverse('lecture-hometask', kwargs={'lecture_pk': 1}),
            data={
                'title': 'Test Lecture',
                'description': 'Test_description',
                'creator': user,
                'lecture': lecture, },
        )
        force_authenticate(request, user=user)
        response = view(request, lecture_pk=1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_hometask_creation_forbidden(self):
        user = User.objects.get(username='student1')
        view = HometaskView.as_view()
        lecture = Lecture.objects.get(id=1)
        request = self.factory.post(
            reverse('lecture-hometask', kwargs={'lecture_pk': 1}),
            data={
                'title': 'Test Lecture',
                'description': 'Test_description',
                'creator': user,
                'lecture': lecture,
            },
        )
        force_authenticate(request, user=user)
        response = view(request, lecture_pk=1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestHometaskView(APITestCase):

    @classmethod
    def setUpClass(cls):
        super(TestHometaskView, cls).setUpClass()
        cls.test_teacher_1 = {'username': 'teacher1',
                              'password': 'teacher1',
                              'first_name': 'teacher1',
                              'last_name': 'teacher1',
                              'email': 'teacher1@teacher.com',
                              'registration_role': 'T'
                              }
        cls.test_student_1 = {'username': 'student1',
                              'password': 'student1',
                              'first_name': 'student1',
                              'last_name': 'student1',
                              'email': 'student1@student.ru',
                              'registration_role': 'S'
                              }
        cls.test_student_2 = {'username': 'student2',
                              'password': 'student2',
                              'first_name': 'student2',
                              'last_name': 'student2',
                              'email': 'student2@student.ru',
                              'registration_role': 'S'
                              }
        cls.teacher_user_1 = User.objects._create_user(**cls.test_teacher_1)
        cls.student_user_1 = User.objects._create_user(**cls.test_student_1)
        cls.student_user_2 = User.objects._create_user(**cls.test_student_2)
        cls.test_course = Course(title='Test_course', description='Test_description', creator=cls.teacher_user_1, )
        cls.test_course.save()
        cls.test_lecture = Lecture(
            title='Test Lecture',
            creator=cls.teacher_user_1,
            course=Course.objects.get(id=1),
            presentation=SimpleUploadedFile("test.txt", b"these are the file contents!"),
        )
        cls.test_lecture.save()
        cls.test_hometask = Hometask(title='Test_hometask', description='Test_hometask', creator=cls.teacher_user_1,
                                     lecture=Lecture.objects.get(id=1))
        cls.test_hometask.save()

    def setUp(self):
        self.factory = APIRequestFactory()

    def test_hometask_view(self):
        user = User.objects.get(username='teacher1')
        self.test_course.teacher.add(user)
        view = HometaskView.as_view()
        request = self.factory.get(reverse('lecture-hometask', kwargs={'lecture_pk': 1}))
        force_authenticate(request, user=user)
        response = view(request, lecture_pk=1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_course_view_forbidden_method(self):
        user = User.objects.get(username='teacher1')
        self.test_course.teacher.add(user)
        view = HometaskView.as_view()
        request = self.factory.delete(reverse('lecture-hometask', kwargs={'lecture_pk': 1}))
        force_authenticate(request, user=user)
        response = view(request, lecture_pk=1)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_student_can_see_hometask_and_its_details(self):
        user = User.objects.get(username='student1')
        course = Course.objects.get(id=1)
        course.student.add(user)
        hometask_view = HometaskView.as_view()
        request = self.factory.get(reverse('lecture-hometask', kwargs={'lecture_pk': 1}))
        force_authenticate(request, user=user)
        response = hometask_view(request, lecture_pk=1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        hometask_detail_view = HometaskDetailView.as_view()
        request = self.factory.get(reverse('detailed-hometask', kwargs={'lecture_pk': 1, 'pk': 1}))
        force_authenticate(request, user=user)
        response = hometask_detail_view(request, lecture_pk=1, pk=1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_foreign_student_cant_see_lecture_and_its_details(self):
        user = User.objects.get(username='student2')
        hometask_view = HometaskView.as_view()
        request = self.factory.get(reverse('lecture-hometask', kwargs={'lecture_pk': 1}))
        force_authenticate(request, user=user)
        response = hometask_view(request, lecture_pk=1)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        hometask_detail_view = HometaskDetailView.as_view()
        request = self.factory.get(reverse('detailed-hometask', kwargs={'lecture_pk': 1, 'pk': 1}))
        force_authenticate(request, user=user)
        response = hometask_detail_view(request, lecture_pk=1, pk=1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestCompletedHometaskCreate(APITestCase):

    @classmethod
    def setUpClass(cls):
        super(TestCompletedHometaskCreate, cls).setUpClass()
        cls.test_teacher_1 = TEST_TEACHER_1
        cls.test_student_1 = TEST_STUDENT_1
        cls.test_student_2 = TEST_STUDENT_2
        cls.teacher_user_1 = User.objects._create_user(**cls.test_teacher_1)
        cls.student_user_1 = User.objects._create_user(**cls.test_student_1)
        cls.student_user_2 = User.objects._create_user(**cls.test_student_2)
        cls.test_course = Course(creator=cls.teacher_user_1, **TEST_COURSE)
        cls.test_course.save()
        cls.test_lecture = Lecture(creator=cls.teacher_user_1, course=Course.objects.get(id=1), **TEST_LECTURE)
        cls.test_lecture.save()
        cls.test_hometask = Hometask(creator=cls.teacher_user_1, lecture=Lecture.objects.get(id=1), **TEST_HOMETASK)
        cls.test_hometask.save()

    def setUp(self):
        self.factory = APIRequestFactory()

    def test_completed_hometask_creation(self):
        user = User.objects.get(username='student1')
        view = CompletedHomeworkView.as_view()
        course = Course.objects.get(id=1)
        course.student.add(user)
        hometask = Hometask.objects.get(id=1)
        request = self.factory.post(
            reverse('hometask-completed', kwargs={'hometasks_pk': 1}),
            data={
                'link': 'https://www.test.com',
                'creator': user,
                'hometask': hometask,
            },
        )
        force_authenticate(request, user=user)
        response = view(request, hometasks_pk=1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_hometask_creation_forbidden_for_teacher(self):
        user = User.objects.get(username='teacher1')
        view = CompletedHomeworkView.as_view()
        course = Course.objects.get(id=1)
        course.teacher.add(user)
        hometask = Hometask.objects.get(id=1)
        request = self.factory.post(
            reverse('hometask-completed', kwargs={'hometasks_pk': 1}),
            data={
                'link': 'https://www.test.com',
                'creator': user,
                'hometask': hometask,
            },
        )
        force_authenticate(request, user=user)
        response = view(request, hometasks_pk=1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestCompletedHometaskView(APITestCase):

    @classmethod
    def setUpClass(cls):
        super(TestCompletedHometaskView, cls).setUpClass()
        cls.test_teacher_1 = TEST_TEACHER_1
        cls.test_student_1 = TEST_STUDENT_1
        cls.test_student_2 = TEST_STUDENT_2
        cls.teacher_user_1 = User.objects._create_user(**cls.test_teacher_1)
        cls.student_user_1 = User.objects._create_user(**cls.test_student_1)
        cls.student_user_2 = User.objects._create_user(**cls.test_student_2)
        cls.test_course = Course(creator=cls.teacher_user_1, **TEST_COURSE)
        cls.test_course.save()
        cls.test_lecture = Lecture(creator=cls.teacher_user_1, course=Course.objects.get(id=1), **TEST_LECTURE)
        cls.test_lecture.save()
        cls.test_hometask = Hometask(creator=cls.teacher_user_1, lecture=Lecture.objects.get(id=1), **TEST_HOMETASK)
        cls.test_hometask.save()
        cls.test_completed_hometask = CompletedHomework(link='https://www.test.com',
                                                        creator=cls.student_user_1,
                                                        hometask=Hometask.objects.get(id=1),
                                                        )
        cls.test_completed_hometask.save()

    def setUp(self):
        self.factory = APIRequestFactory()

    def test_completed_hometask_view_for_teacher(self):
        user = User.objects.get(username='teacher1')
        test_course = Course.objects.get(id=1)
        test_course.teacher.add(user)
        view = CompletedHomeworkView.as_view()
        request = self.factory.get(reverse('hometask-completed', kwargs={'hometasks_pk': 1}))
        force_authenticate(request, user=user)
        response = view(request, hometasks_pk=1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_course_view_forbidden_method(self):
        user = User.objects.get(username='student1')
        test_course = Course.objects.get(id=1)
        test_course.student.add(user)
        view = CompletedHomeworkView.as_view()
        request = self.factory.delete(reverse('hometask-completed', kwargs={'hometasks_pk': 1}))
        force_authenticate(request, user=user)
        response = view(request, hometasks_pk=1)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_teacher_can_see_all_completed_homework(self):
        teacher = User.objects.get(username='teacher1')
        test_course = Course.objects.get(id=1)
        test_course.teacher.add(teacher)
        user = User.objects.get(username='student2')
        test_other_completed_hometask = CompletedHomework(link='https://www.othertest.com',
                                                          creator=user,
                                                          hometask=Hometask.objects.get(id=1),
                                                          )
        test_other_completed_hometask.save()
        view = CompletedHomeworkView.as_view()
        request = self.factory.get(reverse('hometask-completed', kwargs={'hometasks_pk': 1}))
        force_authenticate(request, user=teacher)
        response = view(request, hometasks_pk=1)
        self.assertEqual(len(json.loads(response.render().content)), 2)

    def test_student_cant_see_completed_homework_and_its_details_if_not_creators(self):
        user = User.objects.get(username='student2')
        hometask_view = CompletedHomeworkView.as_view()
        test_other_completed_hometask = CompletedHomework(link='https://www.othertest.com',
                                                          creator=user,
                                                          hometask=Hometask.objects.get(id=1),
                                                          )
        test_other_completed_hometask.save()
        request = self.factory.get(reverse('hometask-completed', kwargs={'hometasks_pk': 1}))
        force_authenticate(request, user=user)
        response = hometask_view(request, hometasks_pk=1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        hometask_detail_view = CompletedHomeworkDetailView.as_view()
        request = self.factory.get(reverse('detailed-hometask-completed', kwargs={'hometasks_pk': 1, 'pk': 1}))
        force_authenticate(request, user=user)
        response = hometask_detail_view(request, hometasks_pk=1, pk=1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestMarkCreation(APITestCase):

    @classmethod
    def setUpClass(cls):
        super(TestMarkCreation, cls).setUpClass()
        cls.test_teacher_1 = TEST_TEACHER_1
        cls.test_student_1 = TEST_STUDENT_1
        cls.test_student_2 = TEST_STUDENT_2
        cls.teacher_user_1 = User.objects._create_user(**cls.test_teacher_1)
        cls.student_user_1 = User.objects._create_user(**cls.test_student_1)
        cls.student_user_2 = User.objects._create_user(**cls.test_student_2)
        cls.test_course = Course(creator=cls.teacher_user_1, **TEST_COURSE)
        cls.test_course.save()
        cls.test_lecture = Lecture(creator=cls.teacher_user_1, course=Course.objects.get(id=1), **TEST_LECTURE)
        cls.test_lecture.save()
        cls.test_hometask = Hometask(creator=cls.teacher_user_1, lecture=Lecture.objects.get(id=1), **TEST_HOMETASK)
        cls.test_hometask.save()
        cls.test_completed_hometask = CompletedHomework(link='https://www.test.com',
                                                        creator=cls.student_user_1,
                                                        hometask=Hometask.objects.get(id=1),
                                                        )
        cls.test_completed_hometask.save()

    def setUp(self):
        self.factory = APIRequestFactory()

    def test_mark_creation(self):
        user = User.objects.get(username='teacher1')
        view = MarkView.as_view()
        course = Course.objects.get(id=1)
        course.teacher.add(user)
        completed_hometask = CompletedHomework.objects.get(id=1)
        request = self.factory.post(
            reverse('marks', kwargs={'pk': 1}),
            data={
                'mark': 100,
                'creator': user,
                'completed_homework': completed_hometask,
            },
        )
        force_authenticate(request, user=user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_mark_creation_forbidden(self):
        user = User.objects.get(username='student1')
        view = MarkView.as_view()
        course = Course.objects.get(id=1)
        course.student.add(user)
        completed_hometask = CompletedHomework.objects.get(id=1)
        request = self.factory.post(
            reverse('marks', kwargs={'pk': 1}),
            data={
                'mark': 100,
                'creator': user,
                'completed_homework': completed_hometask,
            },
        )
        force_authenticate(request, user=user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestMarkView(APITestCase):

    @classmethod
    def setUpClass(cls):
        super(TestMarkView, cls).setUpClass()
        cls.test_teacher_1 = TEST_TEACHER_1
        cls.test_student_1 = TEST_STUDENT_1
        cls.test_student_2 = TEST_STUDENT_2
        cls.teacher_user_1 = User.objects._create_user(**cls.test_teacher_1)
        cls.student_user_1 = User.objects._create_user(**cls.test_student_1)
        cls.student_user_2 = User.objects._create_user(**cls.test_student_2)
        cls.test_course = Course(creator=cls.teacher_user_1, **TEST_COURSE)
        cls.test_course.save()
        cls.test_lecture = Lecture(creator=cls.teacher_user_1, course=Course.objects.get(id=1), **TEST_LECTURE)
        cls.test_lecture.save()
        cls.test_hometask = Hometask(creator=cls.teacher_user_1, lecture=Lecture.objects.get(id=1), **TEST_HOMETASK)
        cls.test_hometask.save()
        cls.test_completed_hometask = CompletedHomework(link='https://www.test.com',
                                                        creator=cls.student_user_1,
                                                        hometask=Hometask.objects.get(id=1),
                                                        )
        cls.test_completed_hometask.save()
        cls.test_mark = Mark(mark=100, creator=cls.teacher_user_1,
                             completed_homework=CompletedHomework.objects.get(id=1))
        cls.test_mark.save()

    def setUp(self):
        self.factory = APIRequestFactory()

    def test_completed_hometask_view_for_student(self):
        user = User.objects.get(username='student1')
        test_course = Course.objects.get(id=1)
        test_course.student.add(user)
        view = MarkView.as_view()
        request = self.factory.get(reverse('marks', kwargs={'pk': 1}))
        force_authenticate(request, user=user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_course_view_forbidden_method(self):
        user = User.objects.get(username='teacher1')
        view = MarkView.as_view()
        course = Course.objects.get(id=1)
        course.teacher.add(user)
        request = self.factory.delete(reverse('marks', kwargs={'pk': 1}))
        force_authenticate(request, user=user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_student_cant_see_mark_and_its_details_if_not_creators(self):
        user = User.objects.get(username='student2')
        test_other_completed_hometask = CompletedHomework(link='https://www.othertest.com',
                                                          creator=user,
                                                          hometask=Hometask.objects.get(id=1), )
        test_other_completed_hometask.save()
        teacher = User.objects.get(username='teacher1')
        mark_view = MarkView.as_view()
        test_other_mark = Mark(mark=99, creator=teacher, completed_homework=CompletedHomework.objects.get(id=2))
        test_other_mark.save()
        request = self.factory.get(reverse('marks', kwargs={'pk': 1}))
        force_authenticate(request, user=user)
        response = mark_view(request, pk=1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        mark_detail_view = MarkDetailView.as_view()
        request = self.factory.get(reverse('detailed-mark', kwargs={'pk': 1}))
        force_authenticate(request, user=user)
        response = mark_detail_view(request, hometasks_pk=1, pk=1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestCommentCreation(APITestCase):

    @classmethod
    def setUpClass(cls):
        super(TestCommentCreation, cls).setUpClass()
        cls.test_teacher_1 = TEST_TEACHER_1
        cls.test_student_1 = TEST_STUDENT_1
        cls.test_student_2 = TEST_STUDENT_2
        cls.teacher_user_1 = User.objects._create_user(**cls.test_teacher_1)
        cls.student_user_1 = User.objects._create_user(**cls.test_student_1)
        cls.student_user_2 = User.objects._create_user(**cls.test_student_2)
        cls.test_course = Course(creator=cls.teacher_user_1, **TEST_COURSE)
        cls.test_course.save()
        cls.test_lecture = Lecture(creator=cls.teacher_user_1, course=Course.objects.get(id=1), **TEST_LECTURE)
        cls.test_lecture.save()
        cls.test_hometask = Hometask(creator=cls.teacher_user_1, lecture=Lecture.objects.get(id=1), **TEST_HOMETASK)
        cls.test_hometask.save()
        cls.test_completed_hometask = CompletedHomework(link='https://www.test.com',
                                                        creator=cls.student_user_1,
                                                        hometask=Hometask.objects.get(id=1),
                                                        )
        cls.test_completed_hometask.save()
        cls.test_mark = Mark(mark=100, creator=cls.teacher_user_1,
                             completed_homework=CompletedHomework.objects.get(id=1))
        cls.test_mark.save()

    def setUp(self):
        self.factory = APIRequestFactory()

    def test_teacher_comment_creation(self):
        user = User.objects.get(username='teacher1')
        view = CommentView.as_view()
        course = Course.objects.get(id=1)
        course.teacher.add(user)
        mark = Mark.objects.get(id=1)
        request = self.factory.post(
            reverse('comments', kwargs={'mark_pk': 1}),
            data={
                'mark': mark,
                'creator': user,
                'comment_text': 'Test comment text',
            },
        )
        force_authenticate(request, user=user)
        response = view(request, mark_pk=1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_student_comment_creation(self):
        user = User.objects.get(username='student1')
        view = CommentView.as_view()
        course = Course.objects.get(id=1)
        course.student.add(user)
        mark = Mark.objects.get(id=1)
        request = self.factory.post(
            reverse('comments', kwargs={'mark_pk': 1}),
            data={
                'mark': mark,
                'creator': user,
                'comment_text': 'Another test comment text',
            },
        )
        force_authenticate(request, user=user)
        response = view(request, mark_pk=1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class TestCommentView(APITestCase):

    @classmethod
    def setUpClass(cls):
        super(TestCommentView, cls).setUpClass()
        cls.test_teacher_1 = TEST_TEACHER_1
        cls.test_student_1 = TEST_STUDENT_1
        cls.test_student_2 = TEST_STUDENT_2
        cls.teacher_user_1 = User.objects._create_user(**cls.test_teacher_1)
        cls.student_user_1 = User.objects._create_user(**cls.test_student_1)
        cls.student_user_2 = User.objects._create_user(**cls.test_student_2)
        cls.test_course = Course(creator=cls.teacher_user_1, **TEST_COURSE)
        cls.test_course.save()
        cls.test_lecture = Lecture(creator=cls.teacher_user_1, course=Course.objects.get(id=1), **TEST_LECTURE)
        cls.test_lecture.save()
        cls.test_hometask = Hometask(creator=cls.teacher_user_1, lecture=Lecture.objects.get(id=1), **TEST_HOMETASK)
        cls.test_hometask.save()
        cls.test_completed_hometask = CompletedHomework(link='https://www.test.com',
                                                        creator=cls.student_user_1,
                                                        hometask=Hometask.objects.get(id=1),
                                                        )
        cls.test_completed_hometask.save()
        cls.test_mark = Mark(mark=100, creator=cls.teacher_user_1,
                             completed_homework=CompletedHomework.objects.get(id=1))
        cls.test_mark.save()
        cls.test_comment_1 = Comment(mark=Mark.objects.get(id=1), creator=cls.teacher_user_1,
                                     comment_text='Test comment text')
        cls.test_comment_1.save()
        cls.test_comment_2 = Comment(mark=Mark.objects.get(id=1), creator=cls.student_user_1,
                                     comment_text='Another test comment text')
        cls.test_comment_2.save()

    def setUp(self):
        self.factory = APIRequestFactory()

    def test_teacher_can_see_all_comments(self):
        teacher = User.objects.get(username='teacher1')
        test_course = Course.objects.get(id=1)
        test_course.teacher.add(teacher)
        view = CommentView.as_view()
        request = self.factory.get(reverse('comments', kwargs={'mark_pk': 1}))
        force_authenticate(request, user=teacher)
        response = view(request, mark_pk=1)
        self.assertEqual(len(json.loads(response.render().content)), 2)

    def test_student_can_see_all_comments(self):
        student = User.objects.get(username='student1')
        test_course = Course.objects.get(id=1)
        test_course.student.add(student)
        view = CommentView.as_view()
        request = self.factory.get(reverse('comments', kwargs={'mark_pk': 1}))
        force_authenticate(request, user=student)
        response = view(request, mark_pk=1)
        self.assertEqual(len(json.loads(response.render().content)), 2)

    def test_student_cant_see_comments_and_details_if_not_his_completed_homework(self):
        user = User.objects.get(username='student2')
        test_course = Course.objects.get(id=1)
        test_course.student.add(user)
        comment_view = CommentView.as_view()
        request = self.factory.get(reverse('comments', kwargs={'mark_pk': 1}))
        force_authenticate(request, user=user)
        response = comment_view(request, mark_pk=1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        comment_detail_view = CommentDetailView.as_view()
        request = self.factory.get(reverse('detailed-comment', kwargs={'mark_pk': 1, 'pk': 1}))
        force_authenticate(request, user=user)
        response = comment_detail_view(request, mark_pk=1, pk=1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_comment_view_forbidden_method(self):
        user = User.objects.get(username='teacher1')
        view = CommentView.as_view()
        course = Course.objects.get(id=1)
        course.teacher.add(user)
        request = self.factory.delete(reverse('comments', kwargs={'mark_pk': 1}))
        force_authenticate(request, user=user)
        response = view(request, mark_pk=1)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_comment_cannot_be_deleted(self):
        user = User.objects.get(username='teacher1')
        view = CommentDetailView.as_view()
        course = Course.objects.get(id=1)
        course.teacher.add(user)
        request = self.factory.delete(reverse('detailed-comment', kwargs={'mark_pk': 1, 'pk': 1}))
        force_authenticate(request, user=user)
        response = view(request, mark_pk=1, pk=1)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
