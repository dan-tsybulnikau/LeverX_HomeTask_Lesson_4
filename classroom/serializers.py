from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import Course, Lecture, Hometask, CompletedHomework, Mark, Comment


UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ('username', 'email', 'first_name', 'last_name', 'registration_role')


class UserRegisterSerializer(serializers.ModelSerializer):
    UserUniqueValidator = UniqueValidator(queryset=UserModel.objects.all(),
                                          message='Username already exists.')
    EmailUniqueValidator = UniqueValidator(queryset=UserModel.objects.all(),
                                           message='Email already exists.')

    username = serializers.CharField(min_length=5, max_length=15,
                                     validators=[UserUniqueValidator])
    password = serializers.CharField(min_length=5, max_length=25, write_only=True,
                                     required=True, style={'input_type': 'password'})
    email = serializers.EmailField(max_length=50, validators=[EmailUniqueValidator])

    class Meta:
        model = UserModel
        fields = ('username', 'password', 'email', 'first_name', 'last_name', 'registration_role',)

    def create(self, validated_data):
        password = validated_data.get('password')
        user = UserModel.objects.create(
            username=validated_data.get('username'),
            registration_role=validated_data.get('registration_role', 'S'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            email=validated_data.get('email'),
        )
        user.set_password(password)
        user.save()
        return user


class CourseSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Course
        exclude = ('student', 'teacher',)


class CourseDetailSerializer(serializers.ModelSerializer):
    course_lectures = serializers.StringRelatedField(read_only=True, many=True)
    creator = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Course
        fields = ('id', 'title', 'description', 'creator', 'student', 'teacher', 'course_lectures',)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        students = validated_data.get('student')
        teachers = validated_data.get('teacher')
        if students:
            for person in students:
                instance.student.add(person)
        if teachers:
            for person in teachers:
                instance.teacher.add(person)
        instance.save()
        return instance


class LectureSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Lecture
        exclude = ('course',)


class HometaskSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Hometask
        exclude = ('lecture',)


class HometaskDetailSerializer(serializers.ModelSerializer):
    completed_homework = serializers.StringRelatedField(read_only=True, many=True)
    creator = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Hometask
        exclude = ('lecture',)
        read_only_fields = ('lecture', 'creator',)


class LectureDetailSerializer(serializers.ModelSerializer):
    hometask = serializers.StringRelatedField(read_only=True, many=True)
    creator = serializers.StringRelatedField(read_only=True)
    course = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Lecture
        fields = ('id', 'title', 'course', 'creator', 'presentation', 'hometask')
        read_only_fields = ('course', 'creator',)


class CompletedHomeworkSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = CompletedHomework
        exclude = ('hometask',)


class CompletedHomeworkDetailSerializer(serializers.ModelSerializer):
    mark = serializers.StringRelatedField(read_only=True)
    creator = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = CompletedHomework
        fields = ('id', 'creator', 'link', 'hometask', 'mark',)
        read_only_fields = ('hometask', 'creator',)


class MarkSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    completed_homework = serializers.SlugRelatedField(read_only=True, slug_field='link')

    class Meta:
        model = Mark
        fields = ('id', 'creator', 'completed_homework', 'mark',)


class CommentSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Comment
        exclude = ('mark', )


class CommentDetailSerializer(serializers.ModelSerializer):
    creator = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        exclude = ('mark', )
        read_only_fields = ('mark', 'creator',)


class MarkDetailSerializer(serializers.ModelSerializer):
    comments = CommentDetailSerializer(read_only=True, many=True)
    creator = serializers.StringRelatedField(read_only=True)
    completed_homework = serializers.SlugRelatedField(read_only=True, slug_field='link')

    class Meta:
        model = Mark
        fields = ('id', 'creator', 'completed_homework', 'mark', 'comments',)
        read_only_fields = ('completed_homework', 'creator',)
