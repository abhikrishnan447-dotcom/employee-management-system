# Employee Management System

A Django-based Employee Management System for managing employees, departments, tasks, progress updates, extension requests, notifications, messages, and visitor messages.

## Features

### Admin
- Admin login and dashboard
- Employee management
- Department management
- Task assignment and task management
- Task file management
- Progress monitoring
- Extension request management
- Employee/team messaging
- Notifications
- Visitor message management

### Employee
- Employee login and dashboard
- View assigned tasks
- Update task progress
- Upload task-related files
- Request task extensions
- View notifications
- Send and receive messages
- Manage profile information

### Public / Landing Pages
- Home/landing page
- About section
- Visitor "Let's Talk" contact/message form

## Technology Stack

- Python
- Django
- SQLite (development database)
- HTML5
- CSS3
- JavaScript
- Bootstrap / frontend libraries used by the project

## Project Structure

```text
work_management/
└── work_manage/
    ├── manage.py
    ├── work_manage/
    │   ├── settings.py
    │   ├── urls.py
    │   ├── asgi.py
    │   └── wsgi.py
    └── work_manage_app/
        ├── models.py
        ├── views.py
        ├── urls.py
        ├── admin.py
        ├── apps.py
        ├── migrations/
        ├── templates/
        │   ├── admin/
        │   ├── employee/
        │   └── landing/
        └── static/
            ├── css/
            ├── js/
            └── images/
```

## Installation

Open a terminal in the folder containing `manage.py`.

```bash
python -m venv venv
```

Activate the virtual environment on Windows PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

Install the project dependencies available for the project environment, then run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Run the Development Server

```bash
python manage.py runserver
```

Then open the local Django server address shown in the terminal.

## Useful Django Commands

Check the project for configuration errors:

```bash
python manage.py check
```

Create migrations after model changes:

```bash
python manage.py makemigrations
```

Apply migrations:

```bash
python manage.py migrate
```

Collect static files when required for production deployment:

```bash
python manage.py collectstatic
```

## Notes

- Keep uploaded media files separate from source code when deploying to production.
- Do not expose production secrets or credentials in publicly accessible source code.
- Development settings such as SQLite and Django's development server should be reviewed before production deployment.

## Project Status

The project is under active development. Features and deployment configuration may change as the application is improved.
