# Courser web API app
This is a web application for courses created with Django, Django REST framework and PostgreSQL database.
Code and all its dependencies are packaged up with Docker and runs on Gunicorn WSGI HTTP Server.

## Main features

### All users can

1) Register (user should select his registration role - 'T' (teacher) or 'S' (student), default is 'S').
2) After registration all users must login in order to receive their unique authorization token.
3) Authorize themselves with request header "Authorization: Token _XXXX_".

### Teachers can
1) CRUD of courses.
2) Add / Removing a Student to selected Course.
3) Add a new teacher to course.
4) CRUD Lectures of their courses (Lecture is a topic and a file with a presentation).
5) Add homework to each lecture (Text information).
6) View completed homework.
7) For each completed homework assign / change grades for each student who sent homework.
8) Add comments to each rating.

### Students can
1) View available courses.
2) View available lectures within selected course.
3) View lecture's hometask.
4) Send completed hometask for check.
5) View their completed hometask.
6) View mark of their completed hometask.
7) View / Add comments to mark.

## Permissions
The only action available for unregistered users (and unauthorized) is registration.
All other actions require authentication (with Authentication header and unique Token, 
which is provided after registered user logs in).

For each request different levels of permissions are set, for example, students that are not enrolled in course
are not able to see lectures of this course; list of all completed homeworks is available only for teachers of this 
course, meanwhile students can see only their homework.

## List of API
List of all available routes and request methods is available at

http://127.0.0.1:8000/api/schema/swagger-ui/

or

https://app.swaggerhub.com/apis-docs/dan-tsybulnikau/lever-x_task_api/1.0.0

## Installation
1) Download files from GitHub.
2) Unpack files to preferred directory.
3) Open this directory in terminal.
4) Run
```bash
$ docker-compose up -d --build 
```
5) Run migrations
```bash
$ docker-compose exec web python manage.py makemigrations
$ docker-compose exec web python manage.py migrate
```
6) Check installation going to http://127.0.0.1:8000/api/v1/register

## Tests
```bash
Name                                   Stmts   Miss  Cover
----------------------------------------------------------
__init__.py                                0      0   100%
app\__init__.py                            0      0   100%
app\asgi.py                                4      4     0%
app\settings.py                           23      0   100%
app\urls.py                                4      0   100%
app\wsgi.py                                4      4     0%
classroom\__init__.py                      0      0   100%
classroom\admin.py                         1      0   100%
classroom\apps.py                          4      0   100%
classroom\migrations\0001_initial.py       9      0   100%
classroom\migrations\__init__.py           0      0   100%
classroom\models.py                       66      1    98%
classroom\permissions.py                  69      9    87%
classroom\serializers.py                 110     12    89%
classroom\tests.py                       634      0   100%
classroom\urls.py                          3      0   100%
classroom\views.py                       129     16    88%
manage.py                                 12      2    83%
----------------------------------------------------------
TOTAL                                   1072     48    96%
```
