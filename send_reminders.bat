@echo off
REM AgriAssist - Send Daily Reminder Emails
REM This script is run by Windows Task Scheduler

cd /d E:\Projects\AgriAssistant
E:\Projects\AgriAssistant\venv\Scripts\python.exe manage.py send_reminder_emails >> logs\reminder_emails.log 2>&1
