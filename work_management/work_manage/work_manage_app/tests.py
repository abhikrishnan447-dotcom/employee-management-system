from datetime import date, timedelta

from django.test import TestCase

from .models import ProgressUpdate, Register, Task, TaskFile
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
        self.assertContains(response, "50% overall work completed")

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
