from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Register(models.Model):
    name = models.CharField(max_length=100)
    profile_photo = models.ImageField(upload_to="profile_photos/", blank=True, null=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=10)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name="registered_employees")
    password = models.CharField(max_length=128)
    STATUS_CHOICES = (("Active", "Active"), ("Inactive", "Inactive"))
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Active")

    def __str__(self):
        return self.name


class EmployeeDepartment(models.Model):
    employee = models.OneToOneField(Register, on_delete=models.CASCADE, related_name="department_assignment")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name="employees")
    designation = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.employee.name} - {self.department or 'Unassigned'}"


class Task(models.Model):
    STATUS_CHOICES = (("Pending", "Pending"), ("In Progress", "In Progress"), ("Completed", "Completed"), ("Overdue", "Overdue"))
    PRIORITY_CHOICES = (("Low", "Low"), ("Medium", "Medium"), ("High", "High"))
    title = models.CharField(max_length=200)
    description = models.TextField()
    assigned_to = models.ForeignKey(Register, on_delete=models.CASCADE, related_name="tasks")
    assigned_employees = models.ManyToManyField(Register, related_name="assigned_tasks", blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks")
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="Medium")
    progress = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["deadline", "-created_at"]

    def __str__(self):
        return self.title

    def employees(self):
        return self.assigned_employees.all() if self.assigned_employees.exists() else Register.objects.filter(id=self.assigned_to_id)


class ProgressUpdate(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="updates")
    employee = models.ForeignKey(Register, on_delete=models.CASCADE, related_name="progress_updates")
    progress = models.PositiveIntegerField()
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.task.title} - {self.progress}%"


class TaskFile(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="uploaded_files")
    employee = models.ForeignKey(Register, on_delete=models.CASCADE, related_name="task_files")
    file = models.FileField(upload_to="task_files/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.task.title} - {self.employee.name}"


class ExtensionRequest(models.Model):
    STATUS_CHOICES = (("Pending", "Pending"), ("Approved", "Approved"), ("Rejected", "Rejected"))
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="extension_requests")
    employee = models.ForeignKey(Register, on_delete=models.CASCADE, related_name="extension_requests")
    requested_deadline = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    admin_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.task.title} - {self.status}"


class Notification(models.Model):
    recipient = models.ForeignKey(Register, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=150)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Message(models.Model):
    # Null sender/recipient is used only for the admin side of a conversation.
    sender = models.ForeignKey(Register, on_delete=models.CASCADE, related_name="sent_messages", null=True, blank=True)
    recipient = models.ForeignKey(Register, on_delete=models.CASCADE, related_name="received_messages", null=True, blank=True)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    is_admin_sender = models.BooleanField(default=False)
    is_admin_recipient = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
