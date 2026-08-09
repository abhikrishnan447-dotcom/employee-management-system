from django.urls import path
from . import views
from . import fixes
from . import password_reset

urlpatterns = [
    # ==============================
    # PUBLIC / LANDING PAGE
    # ==============================
    path("", views.index, name="index"),
    path("home/", views.home, name="home"),

    # ==============================
    # EMPLOYEE REGISTRATION & LOGIN
    # ==============================
    path("register/", views.register, name="register"),
    path("register/departments/", views.registration_departments, name="registration_departments"),
    path("login/", views.login_view, name="login"),
    path("forgot-password/", password_reset.forgot_password, name="forgot_password"),
    path("logout/", views.logout, name="logout"),

    # ==============================
    # EMPLOYEE DASHBOARD
    # ==============================
    path("dashboard/", views.dashboard, name="dashboard"),
    path("tasks/", views.employee_tasks, name="employee_tasks"),
    path("tasks/<int:task_id>/", views.task_detail, name="task_detail"),
    path("progress-updates/", views.progress_updates, name="progress_updates"),
    path("tasks/<int:task_id>/progress/", fixes.progress_update_fixed, name="progress_update"),
    path("tasks/<int:task_id>/upload-file/", fixes.task_file_upload_fixed, name="task_file_upload"),
    path("task-files/<int:file_id>/delete/", views.task_file_delete, name="task_file_delete"),
    path("progress-updates/<int:update_id>/edit/", fixes.progress_edit_fixed, name="progress_edit"),
    path("progress-updates/<int:update_id>/delete/", fixes.progress_delete_fixed, name="progress_delete"),

    # ==============================
    # EMPLOYEE EXTENSION REQUESTS
    # ==============================
    path("extension-requests/", views.extension_requests_employee, name="extension_requests_employee"),
    path("tasks/<int:task_id>/extension/", views.request_extension, name="request_extension"),
    path("extension-requests/<int:request_id>/edit/", views.extension_edit, name="extension_edit"),
    path("extension-requests/<int:request_id>/delete/", views.extension_delete, name="extension_delete"),

    # ==============================
    # EMPLOYEE NOTIFICATIONS & MESSAGES
    # ==============================
    path("notifications/", views.notifications, name="notifications"),
    path("notifications/clear/", views.clear_notifications, name="clear_notifications"),
    path("messages/", views.messages_view, name="messages"),
    path("messages/clear/", views.clear_messages, name="clear_messages"),
    path("messages/<int:message_id>/delete/", views.delete_message, name="delete_message"),

    # ==============================
    # EMPLOYEE PROFILE & SETTINGS
    # ==============================
    path("profile/", views.profile, name="profile"),
    path("settings/", views.settings_view, name="settings"),

    # ==============================
    # ADMIN LOGIN & DASHBOARD
    # ==============================
    path("adminlogin/", views.adminlogin, name="adminlogin"),
    path("admin/dashboard/", views.admin_dash, name="admin_dash"),
    path("admin/logout/", views.adminlogout, name="adminlogout"),

    # ==============================
    # ADMIN EMPLOYEE MANAGEMENT
    # ==============================
    path("admin/employees/", views.employee_management, name="employee_management"),
    path("admin/employees/<int:employee_id>/edit/", views.employee_edit, name="employee_edit"),
    path("admin/employees/<int:employee_id>/delete/", views.employee_delete, name="employee_delete"),

    # ==============================
    # ADMIN DEPARTMENT MANAGEMENT
    # ==============================
    path("admin/departments/", views.department_management, name="department_management"),
    path("admin/departments/<int:department_id>/delete/", views.department_delete, name="department_delete"),

    # ==============================
    # ADMIN TASK MANAGEMENT
    # ==============================
    path("admin/tasks/", views.task_management, name="task_management"),
    path("admin/tasks/assign/", views.assign_task, name="assign_task"),
    path("admin/tasks/<int:task_id>/edit/", views.task_edit, name="task_edit"),
    path("admin/tasks/<int:task_id>/delete/", views.task_delete, name="task_delete"),

    # ==============================
    # ADMIN TASK FILES
    # ==============================
    path("admin/task-files/", views.admin_task_files, name="admin_task_files"),
    path("admin/task-files/<int:file_id>/delete/", views.admin_task_file_delete, name="admin_task_file_delete"),

    # ==============================
    # ADMIN EXTENSION REQUESTS
    # ==============================
    path("admin/extensions/", views.extension_requests, name="extension_requests"),
    path("admin/extensions/<int:request_id>/<str:action>/", views.extension_action, name="extension_action"),

    # ==============================
    # ADMIN REPORTS
    # ==============================
    path("admin/reports/", views.reports, name="reports"),

    # ==============================
    # ADMIN NOTIFICATIONS
    # ==============================
    path("admin/notifications/", views.admin_notifications, name="admin_notifications"),
    path("admin/notifications/clear/", views.admin_clear_notifications, name="admin_clear_notifications"),

    # ==============================
    # ADMIN MESSAGES
    # ==============================
    path("admin/messages/", views.admin_messages, name="admin_messages"),
    path("admin/messages/clear/", views.admin_clear_messages, name="admin_clear_messages"),
    path("admin/messages/<int:message_id>/reply/", views.admin_message_reply, name="admin_message_reply"),

    # ==============================
    # ADMIN PROFILE
    # ==============================
    path("admin/profile/", views.admin_profile, name="admin_profile"),
]
