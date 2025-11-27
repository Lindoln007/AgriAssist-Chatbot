from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from reminders.models import FarmReminder
from datetime import date

class Command(BaseCommand):
    help = 'Send email notifications for reminders due today'

    def handle(self, *args, **options):
        today = date.today()
        due_reminders = FarmReminder.objects.filter(
            date=today,
            status='pending'
        ).select_related('user')

        sent_count = 0
        error_count = 0

        for reminder in due_reminders:
            user = reminder.user
            
            # Skip if user has no email
            if not user.email:
                self.stdout.write(
                    self.style.WARNING(
                        f'Skipping reminder {reminder.id}: User {user.username} has no email'
                    )
                )
                continue

            subject = f'Reminder: {reminder.activity_type} - {reminder.crop_or_livestock}'
            
            message = f"""
Hello {user.username},

This is a reminder for your farming activity scheduled for today ({today.strftime('%B %d, %Y')}):

Activity: {reminder.activity_type}
Crop/Livestock: {reminder.crop_or_livestock}
Date: {reminder.date.strftime('%B %d, %Y')}
Time: {reminder.time.strftime('%I:%M %p')}
{f'Notes: {reminder.notes}' if reminder.notes else ''}

Please log in to AgriAssist to mark this reminder as completed once you've finished the task.

Best regards,
AgriAssist Team
            """.strip()

            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                sent_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Sent reminder to {user.email} for: {reminder.activity_type} - {reminder.crop_or_livestock}'
                    )
                )
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'Failed to send email to {user.email}: {str(e)}'
                    )
                )

        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\n=== Summary ==='
                f'\nTotal due reminders: {due_reminders.count()}'
                f'\nEmails sent: {sent_count}'
                f'\nErrors: {error_count}'
            )
        )
