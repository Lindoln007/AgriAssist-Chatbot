# AgriAssist - Farm Calendar Email Notifications Setup

## Email Configuration

Email notifications for farm reminders have been added to the system. Follow these steps to configure and use them:

### 1. Environment Variables Setup

Add the following to your `.env` file:

```env
# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com  # ⚠️ REQUIRED: Replace with your actual email
EMAIL_HOST_PASSWORD=your-app-password  # ⚠️ REQUIRED: Replace with your app password
DEFAULT_FROM_EMAIL=noreply@agriassist.com
```

**IMPORTANT**: The `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` fields MUST be filled in for emails to work!

**For Gmail Users:**
- Use an "App Password" instead of your regular password
- Enable 2-Factor Authentication on your Google account
- Generate an App Password: https://myaccount.google.com/apppasswords
- Use the 16-character app password in `EMAIL_HOST_PASSWORD`

**For Other Email Providers:**
- Update `EMAIL_HOST` and `EMAIL_PORT` accordingly
- Examples:
  - Outlook: `smtp-mail.outlook.com`, port `587`
  - Yahoo: `smtp.mail.yahoo.com`, port `587`
  - Custom SMTP: Use your provider's settings

### 2. Testing Email Notifications

Run the command manually to test:

```bash
python manage.py send_reminder_emails
```

This will:
- Find all reminders due today with status "pending"
- Send an email to each user with a reminder
- Display a summary of sent emails and any errors

### 3. Scheduling Daily Emails

#### Option A: Windows Task Scheduler (Recommended for Windows)

1. Open Task Scheduler
2. Create a new task:
   - **Name**: AgriAssist Daily Reminders
   - **Trigger**: Daily at 7:00 AM (or your preferred time)
   - **Action**: Start a program
     - **Program**: `python`
     - **Arguments**: `manage.py send_reminder_emails`
     - **Start in**: `E:\Projects\AgriAssistant`

#### Option B: Manual Cron Job (Linux/Mac)

Add to crontab (`crontab -e`):

```cron
0 7 * * * cd /path/to/AgriAssistant && python manage.py send_reminder_emails >> /var/log/agriassist_reminders.log 2>&1
```

#### Option C: Django-Cron (Alternative)

If you prefer a Django-based scheduler:

1. Install: `pip install django-cron`
2. Add to `INSTALLED_APPS`: `'django_cron'`
3. Create a cron job class in `reminders/cron.py`
4. Run: `python manage.py runcrons`

### 4. Email Template Customization

To customize the email content, edit:
`reminders/management/commands/send_reminder_emails.py`

Look for the `message` variable (around line 35) and modify the template.

### 5. Testing Without Sending Real Emails

For development/testing, use the console email backend:

In `settings.py`, temporarily change:
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

This will print emails to the console instead of sending them.

### 6. Troubleshooting

**No emails sent:**
- Check that users have email addresses in their profiles
- Verify `.env` file has correct credentials
- Run with `--verbosity 2` for more details:
  ```bash
  python manage.py send_reminder_emails --verbosity 2
  ```

**Authentication errors:**
- For Gmail: Ensure you're using an App Password, not your regular password
- Check that 2FA is enabled on your Google account
- Verify `EMAIL_HOST_USER` matches the account generating the App Password

**Connection errors:**
- Check firewall settings
- Verify `EMAIL_HOST` and `EMAIL_PORT` are correct
- Try `EMAIL_USE_TLS=False` and `EMAIL_USE_SSL=True` with port 465

### 7. Production Recommendations

- Use a dedicated email service (SendGrid, Mailgun, AWS SES) for better deliverability
- Set up proper SPF, DKIM, and DMARC records for your domain
- Monitor email sending logs
- Implement rate limiting if you have many users
- Consider using a task queue (Celery) for large-scale deployments

---

## File Structure

```
AgriAssistant/
├── reminders/
│   ├── management/
│   │   ├── __init__.py
│   │   └── commands/
│   │       ├── __init__.py
│   │       └── send_reminder_emails.py  # Email sending command
│   ├── models.py  # FarmReminder model
│   └── views.py
├── AgriAssistant/
│   └── settings.py  # Email configuration added
└── .env  # Email credentials (create this)
```

## Quick Start

1. Add email credentials to `.env`
2. Test: `python manage.py send_reminder_emails`
3. Schedule with Task Scheduler or cron
4. Done! Users will receive daily emails for reminders due today.

---

## Multiple Reminders Per Day

The reminder system now supports scheduling multiple reminders on the same day at different times:

- When creating a reminder, you can now specify both a **date** and a **time**
- This allows you to set multiple reminders for the same day (e.g., "Irrigation - Tomatoes" at 8:00 AM and "Fertilizing - Maize" at 2:00 PM)
- The time field defaults to 8:00 AM if not specified
- Reminders are sorted by date and time in the calendar view
- Email notifications include the scheduled time for each reminder

**Example Use Cases:**
- Morning and evening feeding schedules for livestock
- Multiple irrigation sessions throughout the day
- Staggered planting times for different crops on the same day

