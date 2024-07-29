"""
Information
---------------------------------------------------------------------
Name        : status.py
Location    : ~/server

Description
---------------------------------------------------------------------
Contains the static variables for classifying the status of
orchestration server job-runs.
"""

SCHEDULED: str = '📅 Scheduled'
LATE: str = '⏳ Late'
PENDING: str = '🔜 Pending'
RUNNING: str = '🏃 Running'
RETRYING: str = '🔁 Retrying'
PAUSED: str = '⏸️ Paused'
CANCELLED: str = '⚪ Cancelled'
SUCCEEDED: str = '✅ Succeeded'
FAILED: str = '⛔ Failed'
CRASHED: str = '💥 Crashed'
