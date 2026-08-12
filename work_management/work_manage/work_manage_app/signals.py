from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ExtensionRequest, Message, Notification, ProgressUpdate, TaskFile


@receiver(post_save, sender=Message, dispatch_uid="worksphere_admin_message_notification")
def notify_admin_about_employee_message(sender, instance, created, **kwargs):
    if created and instance.is_admin_recipient and instance.sender_id:
        Notification.objects.create(
            recipient=None,
            title="New employee message",
            message=f"{instance.sender.name} sent a message to the administrator.",
        )


@receiver(post_save, sender=ExtensionRequest, dispatch_uid="worksphere_admin_extension_notification")
def notify_admin_about_extension_request(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient=None,
            title="New extension request",
            message=f"{instance.employee.name} requested an extension for {instance.task.title}.",
        )


@receiver(post_save, sender=ProgressUpdate, dispatch_uid="worksphere_admin_progress_notification")
def notify_admin_about_progress_update(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient=None,
            title="Employee progress updated",
            message=f"{instance.employee.name} updated progress for {instance.task.title} to {instance.progress}%.",
        )


@receiver(post_save, sender=TaskFile, dispatch_uid="worksphere_admin_file_notification")
def notify_admin_about_employee_file(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient=None,
            title="New employee file uploaded",
            message=f"{instance.employee.name} uploaded a file for {instance.task.title}.",
        )
