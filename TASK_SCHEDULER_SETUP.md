# Windows Task Scheduler Setup Guide
## Automatic Daily Reminder Emails for AgriAssist

This guide will help you set up Windows Task Scheduler to automatically send reminder emails every day.

---

## Quick Setup (5 minutes)

### Step 1: Open Task Scheduler

1. Press `Windows + R` to open Run dialog
2. Type: `taskschd.msc`
3. Press Enter

### Step 2: Create a New Task

1. In Task Scheduler, click **"Create Basic Task..."** in the right panel
2. **Name**: `AgriAssist Daily Reminders`
3. **Description**: `Sends email notifications for farm reminders due today`
4. Click **Next**

### Step 3: Set the Trigger (When to Run)

1. Select **"Daily"**
2. Click **Next**
3. **Start date**: Today's date
4. **Start time**: `07:00:00 AM` (or your preferred time)
   - Recommended times: 6:00 AM, 7:00 AM, or 8:00 AM
   - This is when farmers typically start their day
5. **Recur every**: `1 days`
6. Click **Next**

### Step 4: Set the Action (What to Run)

1. Select **"Start a program"**
2. Click **Next**
3. **Program/script**: Browse and select:
   ```
   E:\Projects\AgriAssistant\send_reminders.bat
   ```
   OR manually type:
   ```
   E:\Projects\AgriAssistant\send_reminders.bat
   ```
4. Leave **"Add arguments"** and **"Start in"** blank
5. Click **Next**

### Step 5: Review and Finish

1. Review your settings:
   - Name: AgriAssist Daily Reminders
   - Trigger: Daily at 7:00 AM
   - Action: Run send_reminders.bat
2. Check the box: **"Open the Properties dialog for this task when I click Finish"**
3. Click **Finish**

### Step 6: Configure Advanced Settings

A properties dialog will open. Configure these settings:

#### General Tab:
- ✅ Check: **"Run whether user is logged on or not"**
- ✅ Check: **"Run with highest privileges"**
- **Configure for**: Windows 10 (or your Windows version)

#### Conditions Tab:
- ❌ Uncheck: **"Start the task only if the computer is on AC power"**
  - This ensures it runs even on battery power
- ❌ Uncheck: **"Stop if the computer switches to battery power"**

#### Settings Tab:
- ✅ Check: **"Allow task to be run on demand"**
- ✅ Check: **"Run task as soon as possible after a scheduled start is missed"**
  - This ensures emails are sent even if the computer was off
- **If the task fails, restart every**: `10 minutes`
- **Attempt to restart up to**: `3 times`

Click **OK** to save.

---

## Testing the Task

### Test 1: Run Manually

1. In Task Scheduler, find your task: **AgriAssist Daily Reminders**
2. Right-click → **Run**
3. Check the **Last Run Result** column
   - Should show: `The operation completed successfully. (0x0)`
4. Check your email (mbayaasante@gmail.com) for reminder emails

### Test 2: Check the Log File

1. Open: `E:\Projects\AgriAssistant\logs\reminder_emails.log`
2. You should see output like:
   ```
   Sent reminder to mbayaasante@gmail.com for: Planting - Maize
   === Summary ===
   Total due reminders: X
   Emails sent: X
   Errors: 0
   ```

---

## Alternative: Run Multiple Times Per Day

If you want to send reminders multiple times per day (e.g., morning and evening):

### Option A: Create Multiple Tasks

1. Create a second task: **AgriAssist Evening Reminders**
2. Set trigger time to: `06:00:00 PM`
3. Use the same batch file: `send_reminders.bat`

### Option B: Modify the Trigger

1. Open your task properties
2. Go to **Triggers** tab
3. Click **New** to add additional triggers
4. Add triggers for different times:
   - 7:00 AM (morning)
   - 12:00 PM (midday)
   - 6:00 PM (evening)

---

## Troubleshooting

### Task doesn't run:

1. **Check Task History**:
   - In Task Scheduler, select your task
   - Click **History** tab (bottom panel)
   - Look for errors

2. **Test the batch file manually**:
   - Double-click: `E:\Projects\AgriAssistant\send_reminders.bat`
   - Check if it runs without errors

3. **Check permissions**:
   - Make sure the task is set to **"Run with highest privileges"**

### No emails are sent:

1. **Check the log file**:
   - Open: `E:\Projects\AgriAssistant\logs\reminder_emails.log`
   - Look for error messages

2. **Verify email credentials**:
   - Open: `E:\Projects\AgriAssistant\.env`
   - Ensure `EMAIL_HOST_PASSWORD` is filled in

3. **Test manually**:
   ```bash
   cd E:\Projects\AgriAssistant
   venv\Scripts\activate
   python manage.py send_reminder_emails
   ```

### Computer is off at scheduled time:

- The task will run when the computer turns on (if you enabled "Run task as soon as possible after a scheduled start is missed")
- Consider leaving your computer on or using a server for production

---

## What Happens Now?

✅ Every day at 7:00 AM (or your chosen time):
1. Windows Task Scheduler will run the batch file
2. The batch file will activate your Python environment
3. Django will check for reminders due today
4. Emails will be sent to users with pending reminders
5. Results will be logged to `logs\reminder_emails.log`

✅ You can check the log file anytime to see:
- How many emails were sent
- Which reminders were processed
- Any errors that occurred

---

## Files Created

- `E:\Projects\AgriAssistant\send_reminders.bat` - The batch file that runs the command
- `E:\Projects\AgriAssistant\logs\` - Directory for log files
- `E:\Projects\AgriAssistant\logs\reminder_emails.log` - Log of all email sending activity

---

## Next Steps

1. ✅ Follow the setup steps above
2. ✅ Test the task by running it manually
3. ✅ Check your email to confirm it works
4. ✅ Wait until tomorrow at 7:00 AM to see it run automatically
5. ✅ Check the log file to verify it ran successfully

---

## Need Help?

If you encounter any issues:
1. Check the log file: `logs\reminder_emails.log`
2. Check Task Scheduler History
3. Test the batch file manually by double-clicking it
4. Verify your email credentials in `.env`

**Your reminder system is now fully automated!** 🎉
