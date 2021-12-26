from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import UserManager


class User(AbstractBaseUser):
    username_validator = UnicodeUsernameValidator()
    ROLE_CHOICES = (
        ('S', 'Student'),
        ('T', 'Teacher'),
    )
    username = models.CharField(max_length=150, unique=True,
                                help_text='Required. No more than 150 characters.',
                                validators=[username_validator],
                                error_messages={
                                    'unique': "A user with that username already exists.",
                                },
                                )
    first_name = models.CharField(max_length=250, blank=False)
    last_name = models.CharField(max_length=250, blank=False)
    email = models.EmailField(unique=True, blank=False)
    registration_role = models.CharField(max_length=1, choices=ROLE_CHOICES, default='S',)

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        ordering = ['username']

    objects = UserManager()


class Course(models.Model):
    title = models.CharField(db_index=True, unique=True, max_length=250)
    description = models.TextField(max_length=256)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    student = models.ManyToManyField(User, blank=True, related_name='students')
    teacher = models.ManyToManyField(User, blank=True, related_name='teachers')

    def __str__(self):
        return '{}, created by: {}'.format(self.title, self.creator)

    class Meta:
        ordering = ['title']


class Lecture(models.Model):
    title = models.CharField(db_index=True, unique=True, max_length=64)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_lectures', blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='creator')
    presentation = models.FileField(upload_to='presentation/%Y-%m-%d-', blank=True, null=True)

    def __str__(self):
        return '{}, from {}'.format(self.title, self.course.title)

    class Meta:
        ordering = ['-id']


class Hometask(models.Model):
    title = models.CharField(db_index=True, unique=True, max_length=64)
    description = models.TextField(max_length=256)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teacher')
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name='hometask', blank=True)

    def __str__(self):
        return '{}'.format(self.title)

    class Meta:
        ordering = ['title']


#
class CompletedHomework(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='completed_homework')
    link = models.URLField(max_length=200, blank=True, null=True)
    hometask = models.ForeignKey(Hometask, on_delete=models.SET_NULL, blank=True, null=True,
                                 related_name='completed_homework')

    def __str__(self):
        return '{} {}: link {}'.format(self.creator.first_name, self.creator.last_name, self.link)


class Mark(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='marks')
    completed_homework = models.OneToOneField(CompletedHomework, on_delete=models.CASCADE, related_name='mark',
                                              blank=True)
    mark = models.IntegerField()

    def __str__(self):
        return 'Evaluated: {} by {} {}'.format(self.mark, self.creator.first_name, self.creator.last_name)


class Comment(models.Model):
    mark = models.ForeignKey(Mark, on_delete=models.CASCADE, related_name='comments', blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    comment_text = models.TextField(max_length=1024)

    def __str__(self):
        return '{} {} commented: {}'.format(self.creator.first_name, self.creator.last_name, self.comment_text)
