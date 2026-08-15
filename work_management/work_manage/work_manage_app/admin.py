from django.contrib import admin

from .models import Department, EmployeeDepartment, ExtensionRequest, Message, Notification, ProgressUpdate, Register, Task


# ==============================
# EMPLOYEE / DEPARTMENT ADMIN
# ==============================
@admin.register(Register)
class RegisterAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "status")
    list_filter = ("status",)
    search_fields = ("name", "email", "phone")


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(EmployeeDepartment)
class EmployeeDepartmentAdmin(admin.ModelAdmin):
    list_display = ("employee", "department", "employee_designation")
    list_filter = ("department",)

    @admin.display(description="Designation")
    def employee_designation(self, obj):
        return obj.employee.designation


# ==============================
# TASK / PROGRESS ADMIN
# ==============================
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "assigned_to", "deadline", "status", "priority", "progress")
    list_filter = ("status", "priority", "department")
    search_fields = ("title", "assigned_to__name")


@admin.register(ProgressUpdate)
class ProgressUpdateAdmin(admin.ModelAdmin):
    list_display = ("task", "employee", "progress", "created_at")


@admin.register(ExtensionRequest)
class ExtensionRequestAdmin(admin.ModelAdmin):
    list_display = ("task", "employee", "requested_deadline", "status", "created_at")
    list_filter = ("status",)


# ==============================
# NOTIFICATION / MESSAGE ADMIN
# ==============================
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "recipient", "is_read", "created_at")
    list_filter = ("is_read",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "sender", "recipient", "is_read", "created_at")
    search_fields = ("subject", "body", "sender__name", "recipient__name")
