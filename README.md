# WorkSphere — Employee Work Management System

WorkSphere is a Django application for managing an organisation's employees, departments, assigned work, progress updates, submitted files, review decisions, and reports.

Employees register for an account, but cannot sign in until an administrator approves them. Administrators manage the workforce and work review process from a dedicated dashboard; employees track their personal and shared work from an employee workspace.

## Core workflow

1. An employee registers with profile, department, designation, and password details.
2. The new account is created with **Pending** status. The employee cannot log in yet.
3. An administrator opens **Employee Approvals**, reviews the employee details, and changes the status to **Active** (approve) or **Inactive** (reject/disable).
4. The administrator creates a task and assigns it to one employee or multiple employees for team work.
5. Employees add progress milestones. For example, 20% today and 30% tomorrow produces 50% total progress.
6. Employees can attach ZIP work files to their latest progress milestone.
7. The administrator reviews uploaded files from **Pending File Reviews** and approves or rejects them with a reason. Rejecting a file deducts the linked milestone from the employee's progress.
8. Employees see their cumulative work completion, task status, and teammate progress for shared tasks. Administrators can download a PDF report.

## Features

### Administrator workspace

- Dashboard counters for employees, departments, total/pending/in-progress/completed/overdue work, inactive employees, employee approvals, file reviews, and extension requests.
- Clickable dashboard counters:
  - **Employee Approvals** opens the pending employee list.
  - **Overdue Works** opens the overdue work filter with assigned employees.
  - **Extension Requests** opens the request review page.
  - **Pending File Reviews** opens the submitted-file review panel.
- Employee management with photo, contact details, department, designation, and status.
- A red notification dot on the employee edit action when an account is awaiting approval.
- Department creation and management.
- Single-employee and multi-employee task assignment, deadline, priority, and status management.
- Filters for task status and assigned employee, including overdue work.
- Central file-review panel with approve/reject action and rejection reason.
- Extension-request review, notifications, employee/admin messaging, and visitor messages.
- Downloadable PDF report with employee details, assigned work, status, and progress.

### Employee workspace

- Sign in only after administrator approval.
- View assigned tasks, deadlines, priorities, extension status, and cumulative progress.
- Add progress milestones; values are cumulative and cannot exceed 100%.
- Upload JPG/PNG profile photos up to 15 MB during registration.
- Upload ZIP work files for administrator review.
- See a rejection reason when a submitted file is rejected.
- Work Overview with exact completed-versus-remaining progress and completed/pending/in-progress counters.
- Teammate progress bars for shared tasks.
- Extension requests, notifications, messages, profile, and account settings.

## Technology

- Python and Django
- SQLite for local development
- HTML, CSS, JavaScript, Bootstrap Icons, and Chart.js

## Project structure

```text
work_management/
└── work_manage/
    ├── manage.py
    ├── db.sqlite3
    ├── media/
    ├── work_manage/             # Django settings and root URLs
    └── work_manage_app/
        ├── models.py             # Employee, task, progress, file, and message models
        ├── views.py              # Application workflows and PDF response
        ├── urls.py               # Application routes
        ├── migrations/           # Database schema history
        ├── templates/            # Admin, employee, and landing pages
        ├── static/               # CSS, JavaScript, and images
        └── tests.py              # Workflow regression tests
```

## Local setup

Run the commands from `work_management/work_manage`.

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install django pillow
python manage.py migrate
python manage.py runserver
```

Open the local URL printed by Django, normally `http://127.0.0.1:8000/`.

### Useful commands

```powershell
python manage.py check
python manage.py test
python manage.py makemigrations --check --dry-run
python manage.py migrate
```

## Deployment notes

- Run `python manage.py migrate` after pulling changes so the file-review and approval fields exist in the database.
- Configure `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, and `DJANGO_ALLOWED_HOSTS` for production.
- Configure email environment variables only when email delivery is required.
- Store `media/` uploads in persistent storage and run `collectstatic` when required by the hosting platform.
