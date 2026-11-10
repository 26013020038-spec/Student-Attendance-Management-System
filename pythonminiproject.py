
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import date

# Database connection
conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()

# Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    roll_no TEXT PRIMARY KEY,
    name TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no TEXT,
    attendance_date TEXT,
    status TEXT,
    UNIQUE(roll_no, attendance_date)
)
""")

conn.commit()


# Add student
def add_student():
    roll = roll_entry.get().strip()
    name = name_entry.get().strip()

    if not roll or not name:
        messagebox.showwarning("Warning", "Enter all details")
        return

    try:
        cursor.execute(
            "INSERT INTO students VALUES (?, ?)",
            (roll, name)
        )
        conn.commit()
        messagebox.showinfo("Success", "Student added successfully")
        roll_entry.delete(0, tk.END)
        name_entry.delete(0, tk.END)
        load_students()

    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Roll number already exists")


# Load students
def load_students():
    for item in student_table.get_children():
        student_table.delete(item)

    cursor.execute("SELECT * FROM students ORDER BY roll_no")

    for row in cursor.fetchall():
        student_table.insert("", tk.END, values=row)

    attendance_student["values"] = [
        f"{row[0]} - {row[1]}"
        for row in cursor.execute(
            "SELECT roll_no, name FROM students ORDER BY roll_no"
        ).fetchall()
    ]


# Mark attendance
def mark_attendance():
    selected = attendance_student.get()
    status = attendance_status.get()

    if not selected:
        messagebox.showwarning("Warning", "Select a student")
        return

    roll = selected.split(" - ")[0]
    today = date.today().isoformat()

    cursor.execute("""
        INSERT INTO attendance
        (roll_no, attendance_date, status)
        VALUES (?, ?, ?)
        ON CONFLICT(roll_no, attendance_date)
        DO UPDATE SET status = excluded.status
    """, (roll, today, status))

    conn.commit()
    messagebox.showinfo("Success", "Attendance saved successfully")
    view_attendance()


# View attendance
def view_attendance():
    for item in attendance_table.get_children():
        attendance_table.delete(item)

    cursor.execute("""
        SELECT s.roll_no, s.name, a.attendance_date, a.status
        FROM attendance a
        JOIN students s ON a.roll_no = s.roll_no
        ORDER BY a.attendance_date DESC, s.roll_no
    """)

    for row in cursor.fetchall():
        attendance_table.insert("", tk.END, values=row)


# Calculate attendance percentage
def attendance_percentage():
    selected = attendance_student.get()

    if not selected:
        messagebox.showwarning("Warning", "Select a student")
        return

    roll = selected.split(" - ")[0]

    cursor.execute("""
        SELECT
            COUNT(*),
            SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END)
        FROM attendance
        WHERE roll_no = ?
    """, (roll,))

    total, present = cursor.fetchone()
    total = total or 0
    present = present or 0

    if total == 0:
        percentage = 0
    else:
        percentage = (present / total) * 100

    messagebox.showinfo(
        "Attendance Percentage",
        f"Total Classes: {total}\n"
        f"Present: {present}\n"
        f"Absent: {total-present}\n"
        f"Attendance: {percentage:.2f}%"
    )


# Main window
root = tk.Tk()
root.title("Student Attendance Management System")
root.geometry("850x650")
root.configure(bg="#eef2f7")

title = tk.Label(
    root,
    text="STUDENT ATTENDANCE MANAGEMENT SYSTEM",
    font=("Arial", 18, "bold"),
    bg="#eef2f7",
    fg="#17365d"
)
title.pack(pady=15)


# Student registration
register_frame = tk.LabelFrame(
    root, text="Student Registration",
    font=("Arial", 11, "bold"),
    bg="#eef2f7", padx=10, pady=10
)
register_frame.pack(fill="x", padx=20, pady=5)

tk.Label(register_frame, text="Roll Number:", bg="#eef2f7").grid(row=0, column=0, padx=5)
roll_entry = tk.Entry(register_frame)
roll_entry.grid(row=0, column=1, padx=5)

tk.Label(register_frame, text="Student Name:", bg="#eef2f7").grid(row=0, column=2, padx=5)
name_entry = tk.Entry(register_frame)
name_entry.grid(row=0, column=3, padx=5)

tk.Button(
    register_frame, text="Add Student",
    command=add_student, bg="#2563eb", fg="white"
).grid(row=0, column=4, padx=10)


# Student list
student_frame = tk.LabelFrame(
    root, text="Registered Students",
    font=("Arial", 11, "bold"),
    bg="#eef2f7"
)
student_frame.pack(fill="both", padx=20, pady=5)

student_table = ttk.Treeview(
    student_frame, columns=("roll", "name"),
    show="headings", height=5
)
student_table.heading("roll", text="Roll Number")
student_table.heading("name", text="Student Name")
student_table.pack(fill="both", padx=10, pady=10)


# Attendance section
attendance_frame = tk.LabelFrame(
    root, text="Mark Attendance",
    font=("Arial", 11, "bold"),
    bg="#eef2f7", padx=10, pady=10
)
attendance_frame.pack(fill="x", padx=20, pady=5)

attendance_student = ttk.Combobox(
    attendance_frame, state="readonly", width=30
)
attendance_student.grid(row=0, column=0, padx=10)

attendance_status = ttk.Combobox(
    attendance_frame,
    values=["Present", "Absent"],
    state="readonly",
    width=15
)
attendance_status.set("Present")
attendance_status.grid(row=0, column=1, padx=10)

tk.Button(
    attendance_frame, text="Save Attendance",
    command=mark_attendance, bg="#16a34a", fg="white"
).grid(row=0, column=2, padx=10)

tk.Button(
    attendance_frame, text="Calculate Percentage",
    command=attendance_percentage, bg="#7c3aed", fg="white"
).grid(row=1, column=0, columnspan=3, pady=10)


# Attendance records
records_frame = tk.LabelFrame(
    root, text="Attendance Records",
    font=("Arial", 11, "bold"),
    bg="#eef2f7"
)
records_frame.pack(fill="both", expand=True, padx=20, pady=5)

attendance_table = ttk.Treeview(
    records_frame,
    columns=("roll", "name", "date", "status"),
    show="headings"
)

for col, heading in [
    ("roll", "Roll Number"),
    ("name", "Student Name"),
    ("date", "Date"),
    ("status", "Status")
]:
    attendance_table.heading(col, text=heading)
    attendance_table.column(col, width=150)

attendance_table.pack(fill="both", expand=True, padx=10, pady=10)

# Initial data loading
load_students()
view_attendance()

root.mainloop()

conn.close()
