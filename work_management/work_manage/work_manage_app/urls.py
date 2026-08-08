from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("home/", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),

    # Admin
    path("adminlogin/", views.adminlogin, name="adminlogin"),
    path("admin/dashboard/", views.admin_dash, name="admin_dash"),
    path("admin/logout/", views.adminlogout, name="adminlogout"),
    path("admin/employees/", views.employee_management, name="employee_management"),
    path("admin/employees/<int:employee_id>/edit/", views.employee_edit, name="employee_edit"),
    path("admin/departments/", views.department_management, name="department_management"),
    path("admin/departments/<int:department_id>/delete/", views.department_delete, name="department_delete"),
    path("admin/tasks/", views.task_management, name="task_management"),
    path("admin/tasks/assign/", views.assign_task, name="assign_task"),
    path("admin/extensions/", views.extension_requests, name="extension_requests"),
    path("admin/extensions/<int:request_id>/<str:action>/", views.extension_action, name="extension_action"),
    path("admin/reports/", views.reports, name="reports"),
    path("admin/notifications/", views.admin_notifications, name="admin_notifications"),
    path("admin/messages/", views.admin_messages, name="admin_messages"),
    path("admin/settings/", views.admin_settings, name="admin_settings"),
    path("admin/profile/", views.admin_profile, name="admin_profile"),

    # Employee
    path("tasks/", views.employee_tasks, name="employee_tasks"),
    path("tasks/<int:task_id>/", views.task_detail, name="task_detail"),
    path("tasks/<int:task_id>/progress/", views.progress_update, name="progress_update"),
    path("tasks/<int:task_id>/extension/", views.request_extension, name="request_extension"),
    path("notifications/", views.notifications, name="notifications"),
    path("messages/", views.messages_view, name="messages"),
    path("profile/", views.profile, name="profile"),
    path("settings/", views.settings_view, name="settings"),
]
