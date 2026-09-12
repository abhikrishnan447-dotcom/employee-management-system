from datetime import date, timedelta

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import ExtensionRequest, ProgressUpdate, Register, Task, TaskFile
from .views import employee_progress, sync_task_progress


class WorkProgressTests(TestCase):
    def setUp(self):
        self.employee = Register.objects.create(
            name="Test Employee",
            email="employee@example.com",
            phone="9876543210",
            password="unused",
            status="Active",
        )
        self.task = Task.objects.create(
            title="Test task",
            description="Regression test task",
            assigned_to=self.employee,
            deadline=date.today() + timedelta(days=7),
        )

    def test_progress_is_cumulative_and_rejected_file_is_deducted(self):
        first = ProgressUpdate.objects.create(task=self.task, employee=self.employee, progress=20)
        second = ProgressUpdate.objects.create(task=self.task, employee=self.employee, progress=30)

        self.assertEqual(employee_progress(self.task, self.employee), 50)
        TaskFile.objects.create(
            task=self.task,
            employee=self.employee,
            progress_update=second,
            file="task_files/evidence.zip",
            review_status="Rejected",
            rejection_reason="Incomplete evidence",
        )
        self.assertEqual(employee_progress(self.task, self.employee), 20)

        sync_task_progress(self.task)
        self.task.refresh_from_db()
        self.assertEqual(self.task.progress, 20)
        self.assertEqual(self.task.status, "In Progress")
        self.assertEqual(first.progress, 20)

    def test_employee_task_list_uses_employee_progress(self):
        ProgressUpdate.objects.create(task=self.task, employee=self.employee, progress=20)
        self.task.progress = 85
        self.task.save(update_fields=["progress"])
        session = self.client.session
        session["user_id"] = self.employee.id
        session.save()

        response = self.client.get("/tasks/")
        self.assertContains(response, "20%")
        self.assertNotContains(response, "85%")

    def test_employee_dashboard_chart_uses_progress_percentages(self):
        ProgressUpdate.objects.create(task=self.task, employee=self.employee, progress=20)
        ProgressUpdate.objects.create(task=self.task, employee=self.employee, progress=30)
        session = self.client.session
        session["user_id"] = self.employee.id
        session.save()

        response = self.client.get("/dashboard/")
        self.assertEqual(response.context["overall_progress"], 50)
        self.assertEqual(response.context["completed_work_units"], 50)
        self.assertEqual(response.context["remaining_work_units"], 50)
        self.assertContains(response, "Overall Progress")
        self.assertContains(response, "<strong>50%</strong>", html=False)

    def test_employee_dashboard_shows_teammate_progress_for_shared_work(self):
        teammate = Register.objects.create(
            name="Teammate",
            email="teammate@example.com",
            phone="9876543213",
            password="unused",
            status="Active",
        )
        self.task.assigned_employees.set([self.employee, teammate])
        ProgressUpdate.objects.create(task=self.task, employee=self.employee, progress=20)
        ProgressUpdate.objects.create(task=self.task, employee=teammate, progress=40)
        session = self.client.session
        session["user_id"] = self.employee.id
        session.save()

        response = self.client.get("/dashboard/")
        self.assertContains(response, "Team Progress")
        self.assertContains(response, "Teammate")
        self.assertContains(response, "40%")

    def test_pending_employee_cannot_log_in(self):
        pending = Register.objects.create(
            name="Pending Employee",
            email="pending@example.com",
            phone="9876543211",
            password="unused",
            status="Pending",
        )
        response = self.client.post("/login/", {"email": pending.email, "password": "anything"})
        self.assertContains(response, "waiting for administrator approval")
        self.assertNotIn("user_id", self.client.session)

    def test_admin_report_download_is_a_pdf(self):
        session = self.client.session
        session["admin"] = "admin@gmail.com"
        session.save()

        response = self.client.get("/admin/reports/pdf/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn("attachment", response["Content-Disposition"])
        self.assertTrue(response.content.startswith(b"%PDF-1.4"))

    def test_admin_dashboard_includes_all_requested_counters(self):
        Register.objects.create(
            name="Inactive Employee",
            email="inactive@example.com",
            phone="9876543212",
            password="unused",
            status="Inactive",
        )
        Task.objects.create(
            title="Pending task",
            description="Dashboard test task",
            assigned_to=self.employee,
            deadline=date.today() + timedelta(days=7),
            status="Pending",
        )
        Task.objects.create(
            title="In progress task",
            description="Dashboard test task",
            assigned_to=self.employee,
            deadline=date.today() + timedelta(days=7),
            status="In Progress",
        )
        session = self.client.session
        session["admin"] = "admin@gmail.com"
        session.save()

        response = self.client.get("/admin/dashboard/")
        self.assertContains(response, "Pending Works")
        self.assertContains(response, "In Progress Works")
        self.assertContains(response, "Inactive Employees")

    def test_admin_dashboard_counts_pending_file_reviews(self):
        update = ProgressUpdate.objects.create(task=self.task, employee=self.employee, progress=20)
        TaskFile.objects.create(
            task=self.task,
            employee=self.employee,
            progress_update=update,
            file="task_files/review-me.zip",
            review_status="Pending",
        )
        session = self.client.session
        session["admin"] = "admin@gmail.com"
        session.save()

        response = self.client.get("/admin/dashboard/")
        self.assertEqual(response.context["pending_file_reviews"], 1)
        self.assertContains(response, "Pending File Reviews")

    def test_dashboard_counter_links_and_pending_employee_filter(self):
        pending = Register.objects.create(
            name="Pending Employee",
            email="pending-filter@example.com",
            phone="9876543222",
            password="unused",
            status="Pending",
        )
        overdue = Task.objects.create(
            title="Overdue task",
            description="Dashboard link test",
            assigned_to=self.employee,
            deadline=date.today() - timedelta(days=1),
            status="Overdue",
        )
        ExtensionRequest.objects.create(
            task=overdue,
            employee=self.employee,
            requested_deadline=date.today() + timedelta(days=2),
            reason="Need more time",
        )
        session = self.client.session
        session["admin"] = "admin@gmail.com"
        session.save()

        dashboard = self.client.get("/admin/dashboard/")
        self.assertContains(dashboard, '/admin/employees/?status=Pending')
        self.assertContains(dashboard, '/admin/tasks/?status=Overdue')
        self.assertContains(dashboard, '/admin/extensions/')

        employees = self.client.get("/admin/employees/?status=Pending")
        self.assertContains(employees, pending.name)
        self.assertNotContains(employees, self.employee.name)
        self.assertContains(employees, "pending-employee-dot")

    def test_employee_management_displays_designation(self):
        self.employee.designation = "Software Engineer"
        self.employee.save(update_fields=["designation"])
        session = self.client.session
        session["admin"] = "admin@gmail.com"
        session.save()

        response = self.client.get("/admin/employees/")
        self.assertContains(response, "Designation")
        self.assertContains(response, "Software Engineer")

    def test_registration_has_password_toggles_and_rejects_photos_over_15_mb(self):
        response = self.client.get("/register/")
        self.assertContains(response, 'data-target="password"')
        self.assertContains(response, 'data-target="confirmPassword"')

        oversized_photo = SimpleUploadedFile(
            "large.png",
            b"x" * (15 * 1024 * 1024 + 1),
            content_type="image/png",
        )
        response = self.client.post("/register/", {
            "name": "Large Photo",
            "email": "large-photo@example.com",
            "phone": "9876543214",
            "password": "Strong#123",
            "confirm_password": "Strong#123",
            "profile_photo": oversized_photo,
        })
        self.assertContains(response, "Profile photo must be smaller than 15 MB.")
