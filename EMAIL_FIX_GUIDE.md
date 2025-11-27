# Email Configuration Fix

## Problem
Emails are not being sent because the `.env` file has empty values for email credentials.

## Solution

1. **Open the `.env` file** in the root of your project

2. **Update the email configuration** with your actual credentials:

### For Gmail Users (Recommended):

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-actual-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-character-app-password
DEFAULT_FROM_EMAIL=noreply@agriassist.com
```

**Steps to get Gmail App Password:**
1. Go to your Google Account: https://myaccount.google.com/
2. Enable 2-Factor Authentication if not already enabled
3. Go to https://myaccount.google.com/apppasswords
4. Select "Mail" and "Windows Computer" (or other device)
5. Click "Generate"
6. Copy the 16-character password (remove spaces)
7. Paste it into `EMAIL_HOST_PASSWORD` in your `.env` file

### For Other Email Providers:

**Outlook/Hotmail:**
```env
EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@outlook.com
EMAIL_HOST_PASSWORD=your-password
DEFAULT_FROM_EMAIL=noreply@agriassist.com
```

**Yahoo:**
```env
EMAIL_HOST=smtp.mail.yahoo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@yahoo.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@agriassist.com
```

## Testing

After updating your `.env` file:

1. **Restart your Django server** (if running)
2. **Test the email system:**
   ```bash
   python manage.py send_reminder_emails
   ```

3. **Check the output** - you should see:
   - "Sent reminder to [email]..." for each reminder
   - A summary showing emails sent successfully

## Troubleshooting

If you still get errors:

1. **Check your email and password** are correct
2. **For Gmail**: Make sure you're using an App Password, not your regular password
3. **Check your firewall** isn't blocking SMTP connections
4. **Try console backend** for testing (emails will print to console instead):
   - In `settings.py`, temporarily change:
     ```python
     EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
     ```
   - This helps verify the reminder system works without actually sending emails

## Next Steps

Once emails are working, you can schedule the command to run daily using Windows Task Scheduler (see REMINDER_EMAIL_SETUP.md for details).
