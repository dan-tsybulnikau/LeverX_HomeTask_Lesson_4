from rest_framework import permissions
from .models import Course, CompletedHomework


class IsTeacherOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.registration_role == 'T'


class IsCourseTeacherOrIsEnrolledReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user in obj.student.all() or request.user in obj.teacher.all()
        return request.user in obj.teacher.all()


class IsAbleToAddLecturesOrReadOnly(permissions.BasePermission):
    def check(self, request, course):
        if request.method in permissions.SAFE_METHODS:
            return request.user in course.student.all() or request.user in course.teacher.all()
        return request.user in course.teacher.all()

    def has_permission(self, request, view):
        parent_course = Course.objects.get(id=view.kwargs['course_pk'])
        return self.check(request, parent_course)

    def has_object_permission(self, request, view, obj):
        parent_course = Course.objects.get(id=obj.course.id)
        return self.check(request, parent_course)


class IsAbleToAddHomeworkOrReadOnly(permissions.BasePermission):

    def check(self, request, course):
        if request.method in permissions.SAFE_METHODS:
            return request.user in course.student.all() or request.user in course.teacher.all()
        return request.user in course.teacher.all()

    def has_permission(self, request, view):
        parent_course = Course.objects.get(course_lectures=view.kwargs['lecture_pk'])
        return self.check(request, parent_course)

    def has_object_permission(self, request, view, obj):
        parent_course = Course.objects.get(id=obj.lecture.course.id)
        return self.check(request, parent_course)


class IsAbleToUploadSolutionOrReadOnly(permissions.BasePermission):
    def check(self, request, course):
        if request.method in permissions.SAFE_METHODS:
            return request.user in course.teacher.all() or request.user in course.student.all()
        return request.user in course.student.all()

    def has_permission(self, request, view):
        parent_course = Course.objects.get(course_lectures__hometask=view.kwargs['hometasks_pk'])
        return self.check(request, parent_course)

    def has_object_permission(self, request, view, obj):
        parent_course = Course.objects.get(id=obj.hometask.lecture.course.id)
        return self.check(request, parent_course)


class IsAbleToEvaluateOrEvaluatedReadOnly(IsAbleToAddHomeworkOrReadOnly):
    def check(self, request, course, task):
        if request.method in permissions.SAFE_METHODS:
            return request.user in course.teacher.all() or request.user == task.creator
        return request.user in course.teacher.all()

    def has_permission(self, request, view):
        parent_course = Course.objects.get(course_lectures__hometask__completed_homework=view.kwargs['pk'])
        parent_completed_task = CompletedHomework.objects.get(id=view.kwargs['pk'])
        return self.check(request, parent_course, parent_completed_task)

    def has_object_permission(self, request, view, obj):
        parent_course = Course.objects.get(id=obj.completed_homework.hometask.lecture.course.id)
        parent_completed_task = CompletedHomework.objects.get(id=obj.completed_homework.id)
        return self.check(request, parent_course, parent_completed_task)


class IsAbleToCommentOrOwnerReadOnly(IsAbleToAddHomeworkOrReadOnly):
    def check(self, request, course, task):
        return request.user in course.teacher.all() or request.user == task.creator

    def has_permission(self, request, view):
        parent_course = Course.objects.get(course_lectures__hometask__completed_homework=view.kwargs['mark_pk'])
        parent_completed_task = CompletedHomework.objects.get(id=view.kwargs['mark_pk'])
        return self.check(request, parent_course, parent_completed_task)

    def has_object_permission(self, request, view, obj):
        parent_course = Course.objects.get(id=obj.mark.completed_homework.hometask.lecture.course.id)
        parent_completed_task = CompletedHomework.objects.get(id=obj.mark.completed_homework.id)
        return self.check(request, parent_course, parent_completed_task)
