"""
admin_logs_viewer.py
===================

Admin-only GUI to view all activity logs from MongoDB.
Displays logs in a read-only table with ability to refresh.

Author: Ahmed Bouali
"""

import FreeSimpleGUI as sg
from datetime import datetime
from db.mongo import get_db

# ============================================================
# FETCH LOGS FROM MONGODB
# ============================================================
def fetch_all_logs():
    """
    Fetch all logs from MongoDB collection "logs".
    Returns a list of rows suitable for GUI Table.

    Each row format:
        [username, timestamp, test_method, file_path]
    """

    logs_list = []
    try:
        db = get_db()
        collection = db["logs"]  # ensure the collection name matches your logging

        cursor = collection.find().sort("timestamp", -1)  # latest logs first

        for log in cursor:
            username = log.get("username", "UNKNOWN")
            test_method = log.get("method", "UNKNOWN")  # 'method' field in logs
            file_path = log.get("target_file", "UNKNOWN")  # match logging schema
            timestamp = log.get("timestamp")

            # Format timestamp nicely
            if isinstance(timestamp, datetime):
                timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            else:
                timestamp_str = "N/A"

            logs_list.append([username, timestamp_str, test_method, file_path])

        return logs_list

    except Exception as e:
        raise RuntimeError(f"Failed to fetch logs: {e}")


# ============================================================
# ADMIN LOGS VIEWER GUI
# ============================================================
def admin_logs_viewer():
    """
    Opens a GUI window for admins to view all logs.
    Provides:
    - Read-only table
    - Refresh button
    - Close button
    """

    sg.theme("DarkBlue3")

    # -----------------------------
    # Table headers
    # -----------------------------
    table_headings = ["Username", "Date / Time", "Test Method", "Target File"]

    # -----------------------------
    # GUI layout
    # -----------------------------
    layout = [
        [sg.Text("Admin Logs Viewer", font=("Arial", 16, "bold"))],
        [sg.HorizontalSeparator()],
        [
            sg.Table(
                values=[],  # initially empty
                headings=table_headings,
                key="-LOG_TABLE-",
                auto_size_columns=False,
                col_widths=[15, 20, 20, 45],
                justification="left",
                num_rows=15,
                enable_events=False,  # read-only
                alternating_row_color="#1f2933",
                expand_x=True,
                expand_y=True
            )
        ],
        [sg.HorizontalSeparator()],
        [
            sg.Push(),
            sg.Button("Refresh", key="-REFRESH-"),
            sg.Button("Close")
        ]
    ]

    window = sg.Window(
        "Logs - Admin Panel",
        layout,
        finalize=True,
        resizable=True,
        element_justification="center"
    )

    # -----------------------------
    # Initial load
    # -----------------------------
    try:
        logs = fetch_all_logs()
        window["-LOG_TABLE-"].update(values=logs)
    except Exception as e:
        sg.popup_error(f"Failed to load logs:\n{e}")

    # ============================================================
    # Event loop
    # ============================================================
    while True:
        event, _ = window.read(timeout=100)

        if event in (sg.WINDOW_CLOSED, "Close"):
            break

        if event == "-REFRESH-":
            try:
                logs = fetch_all_logs()
                window["-LOG_TABLE-"].update(values=logs)
            except Exception as e:
                sg.popup_error(f"Failed to refresh logs:\n{e}")

    window.close()


# ============================================================
# TEST RUN
# ============================================================
if __name__ == "__main__":
    admin_logs_viewer()
