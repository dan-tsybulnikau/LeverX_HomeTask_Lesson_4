<h1>Courser web API app</h1>
This is a web application for courses created with Django, Django REST framework and PostgreSQL database.
Code and all its dependencies are packaged up with Docker and runs on Gunicorn WSGI HTTP Server.

<h2>Main features</h2>

<h3>All users can</h3>

- Register (user should select his registration role - 'T' (teacher) or 'S' (student), default is 'S').
- After registration all users must login in order to receive their unique authorization token.
- Authorize themselves with request header "Authorization: Token _XXXX_".

<h3>Teachers can</h3>
- CRUD of courses.
- Add / Removing a Student to selected Course.
- Add a new teacher to course.
- CRUD Lectures of their courses (Lecture is a topic and a file with a presentation).
- Add homework to each lecture (Text information).
- View completed homework.
- For each completed homework assign / change grades for each student who sent homework.
- Add comments to each rating.
- 
<h3>Students can</h3>
- View available courses.
- View available lectures within selected course.
- View lecture's hometask.
- Send completed hometask for check.
- View their completed hometask.
- View mark of their completed hometask.
- View / Add comments to mark.

<h2>Permissions</h2>
The only action available for unregistered users (and unauthorized) is registration.
All other actions require authentication (with Authentication header and unique Token, 
which is provided after registered user logs in).

For each request different levels of permissions are set, for example, students that are not enrolled in course
are not able to see lectures of this course; list of all completed homeworks is available only for teachers of this 
course, meanwhile students can see only their homework).

<h2>List of API</h2>
List of all available routes and request methods is available at
```console
http://127.0.0.1:8000/api/schema/swagger-ui/
```
or
```
https://app.swaggerhub.com/apis-docs/dan-tsybulnikau/lever-x_task_api/1.0.0
```
<h2>Installation</h2>
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
6) Check installation going to
```bash
http://127.0.0.1:8000/api/v1/register
```
