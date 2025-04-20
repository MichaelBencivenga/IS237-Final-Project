import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

TASKS_FILENAME = "tasks.json"
tasks_data = []

# returns formatted string for display **desc optional**
def format_task(task):
    description = task.get("description", "")
    base = f"{task['name']} | Deadline: {task['deadline']} | Priority: {task['priority']}"
    if " " in task['deadline']:
        countdown = get_countdown(task['deadline'])
        base += f" | Countdown: {countdown}"
    if description:
        base += f" | Desc: {description}"
    return base

# helper function to parse deadline string into a datetime object
def parse_deadline(deadline_str):
    now = datetime.now()
    if " " in deadline_str:
        try:
            # parse deadline with time (mm/dd hh:mm am/pm)
            dt = datetime.strptime(deadline_str, "%m/%d %I:%M %p")
            dt = dt.replace(year=now.year)
            return dt
        except Exception:
            return None

    else:
        try:
            # if only date provided deadline defaults to 11:59:59pm
            dt =  datetime.strptime(deadline_str, "%m/%d")
            dt = dt.replace(year=now.year, hour=23, minute=59, second=59)
            return dt
        except Exception:
            return None

# returns countdown string (hh:mm:ss) until the deadline, "Expired" if passed
def get_countdown(deadline_str):
    dt = parse_deadline(deadline_str)
    if dt is None:
        return ""
    now = datetime.now()
    diff = dt - now
    if diff.total_seconds() < 0:
        return "Expired"
    seconds = int(diff.total_seconds())
    if seconds >= 86400:  # greater than or equal to 24 hours
        days = seconds // 86400
        seconds %= 86400
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{days}d {hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

# refresh listbox based on tasks_data
def update_listbox():
    # save current selection
    selected_indices = task_listbox.curselection()

    # clear listbox and repopulate
    task_listbox.delete(0, tk.END)
    for task in tasks_data:
        task_listbox.insert(tk.END, format_task(task))

    # restore previous selection
    for index in selected_indices:
        if index < task_listbox.size():
            task_listbox.selection_set(index)

# updates countdown timers for all tasks every second
# may have to change if performance is bad
def update_timers():
    update_listbox()
    root.after(1000, update_timers)

# function to sort tasks based on selected criterion
def sort_tasks():
    criterion = sort_var.get()
    if criterion == "Task Name":
        tasks_data.sort(key=lambda t: t["name"].lower())
    elif criterion == "Deadline":
        tasks_data.sort(key=lambda t: parse_deadline(t["deadline"]))
    elif criterion == "Priority":
        # custom order: High -> Medium -> Low
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        tasks_data.sort(key=lambda t: priority_order.get(t["priority"], 99))
    # refresh listbox with sorted tasks
    task_listbox.delete(0, tk.END)
    for task in tasks_data:
        task_listbox.insert(tk.END, format_task(task))

# create new window for task input
def open_add_task_window():
    add_window = tk.Toplevel(root)
    add_window.title("Add New Task")

    # task name input field
    name_label = ttk.Label(add_window, text="Task Name:")
    name_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
    name_entry = ttk.Entry(add_window, width=40)
    name_entry.grid(row=0, column=1, padx=10, pady=5)
    name_entry.focus()

    # deadline date input field (expects mm/dd)
    date_label = ttk.Label(add_window, text="Deadline Date (mm/dd):")
    date_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
    date_entry = ttk.Entry(add_window, width=40)
    date_entry.grid(row=1, column=1, padx=10, pady=5)

    # deadline time input field (optional, expects hh:mm)
    time_label = ttk.Label(add_window, text="Deadline Time (optional, hh:mm):")
    time_label.grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)

    # create subframe for time entry and am/pm selection
    time_frame = ttk.Frame(add_window)
    time_frame.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

    time_entry = ttk.Entry(time_frame, width=21)
    time_entry.grid(row=0, column=0, padx=(0, 5), pady=5)

    period_label = ttk.Label(time_frame, text="AM/PM:")
    period_label.grid(row=0, column=1, padx=(0, 5), pady=5, sticky=tk.W)

    period_var = tk.StringVar(time_frame)
    period_var.set("AM")
    period_menu = ttk.Combobox(time_frame, textvariable=period_var,
                               values=["AM", "PM"], state="readonly", width=5)
    period_menu.grid(row=0, column=2, padx=(0, 5), pady=5, sticky=tk.W)

    # priority selection
    priority_label = ttk.Label(add_window, text="Priority:")
    priority_label.grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
    priority_var = tk.StringVar(add_window)
    priority_var.set("Low")  # default value set to low
    priority_menu = ttk.Combobox(add_window, textvariable=priority_var,
                                 values=["Low", "Medium", "High"], state="readonly")
    priority_menu.grid(row=3, column=1, padx=10, pady=5)
    priority_menu.current(0) # default value set to low

    # description input field
    desc_label = ttk.Label(add_window, text="Description (optional):")
    desc_label.grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
    desc_text = tk.Text(add_window, width=30, height=4)
    desc_text.grid(row=4, column=1, padx=10, pady=5)

    # function to add new task input and close the window
    def confirm_add():
        # gather data from all entry points
        name = name_entry.get().strip()
        date_input = date_entry.get().strip()
        time_input = time_entry.get().strip()
        period = period_var.get().strip()
        priority = priority_var.get().strip()
        description = desc_text.get("1.0", tk.END).strip()

        # ensure task at least has name
        if not name:
            messagebox.showwarning("Input Error", "Please enter a task name.")
            return

        # validate the time if provided (expects 12-hour format hh:mm with am/pm)
        if time_input:
            try:
                # parse time using period
                parsed_time = datetime.strptime(time_input + " " + period, "%I:%M %p")
                # format time string
                normalized_time = parsed_time.strftime("%I:%M %p")
                deadline = f"{date_input} {normalized_time}"
            except ValueError:
                messagebox.showwarning("Input Error","Deadline time should be in HH:MM format with a valid AM/PM selection.")
                return
        else:
            deadline = date_input

        # create task dictionary
        task = {
            "name": name,
            "deadline": deadline,
            "priority": priority,
            "description": description
        }

        tasks_data.append(task)  # save task to global list
        task_listbox.insert(tk.END, format_task(task))  # insert formatted task into listbox
        add_window.destroy()  # close add task window

    # button to confirm adding the task
    confirm_button = ttk.Button(add_window, text="Add Task", command=confirm_add)
    confirm_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

def open_edit_task_window():
    selection = task_listbox.curselection()
    if not selection:
        messagebox.showinfo("Edit Task", "Please select a task to edit.")
        return

    index = selection[0]
    task = tasks_data[index]

    edit_window = tk.Toplevel(root)
    edit_window.title("Edit Task")

    # Task Name
    ttk.Label(edit_window, text="Task Name:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
    name_entry = ttk.Entry(edit_window, width=40)
    name_entry.grid(row=0, column=1, padx=10, pady=5)
    name_entry.insert(0, task.get("name", ""))
    name_entry.focus()

    # Deadline Date & Time
    ttk.Label(edit_window, text="Deadline Date (mm/dd):").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
    date_entry = ttk.Entry(edit_window, width=40)
    date_entry.grid(row=1, column=1, padx=10, pady=5)

    ttk.Label(edit_window, text="Deadline Time (optional, hh:mm):").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
    time_frame = ttk.Frame(edit_window)
    time_frame.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)
    time_entry = ttk.Entry(time_frame, width=21)
    time_entry.grid(row=0, column=0, padx=(0, 5), pady=5)
    ttk.Label(time_frame, text="AM/PM:").grid(row=0, column=1, padx=(0, 5), pady=5, sticky=tk.W)
    period_var = tk.StringVar(time_frame)
    period_var.set("AM")
    period_menu = ttk.Combobox(time_frame, textvariable=period_var, values=["AM", "PM"], state="readonly", width=5)
    period_menu.grid(row=0, column=2, padx=(0, 5), pady=5, sticky=tk.W)

    # Prepopulate date and time fields
    deadline = task.get("deadline", "")
    if " " in deadline:
        try:
            date_part, time_part = deadline.split(" ", 1)
            date_entry.insert(0, date_part)
            # Expecting the time format "hh:mm AM/PM"
            try:
                time_split = time_part.split(" ")
                if len(time_split) == 2:
                    time_val, period_val = time_split
                    time_entry.insert(0, time_val)
                    period_var.set(period_val)
                else:
                    time_entry.insert(0, time_part)
            except Exception:
                time_entry.insert(0, "")
        except Exception:
            date_entry.insert(0, deadline)
    else:
        date_entry.insert(0, deadline)

    # Priority
    ttk.Label(edit_window, text="Priority:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
    priority_var = tk.StringVar(edit_window)
    priority_var.set(task.get("priority", "Low"))
    priority_menu = ttk.Combobox(edit_window, textvariable=priority_var, values=["Low", "Medium", "High"], state="readonly")
    priority_menu.grid(row=3, column=1, padx=10, pady=5)

    # Description
    ttk.Label(edit_window, text="Description (optional):").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
    desc_text = tk.Text(edit_window, width=30, height=4)
    desc_text.grid(row=4, column=1, padx=10, pady=5)
    desc_text.insert("1.0", task.get("description", ""))

    def confirm_edit():
        new_name = name_entry.get().strip()
        new_date = date_entry.get().strip()
        new_time = time_entry.get().strip()
        new_period = period_var.get().strip()
        new_priority = priority_var.get().strip()
        new_description = desc_text.get("1.0", tk.END).strip()

        if not new_name:
            messagebox.showwarning("Input Error", "Please enter a task name.")
            return

        if new_time:
            try:
                parsed_time = datetime.strptime(new_time + " " + new_period, "%I:%M %p")
                normalized_time = parsed_time.strftime("%I:%M %p")
                new_deadline = f"{new_date} {normalized_time}"
            except ValueError:
                messagebox.showwarning("Input Error", "Deadline time should be in HH:MM format with a valid AM/PM selection.")
                return
        else:
            new_deadline = new_date

        updated_task = {
            "name": new_name,
            "deadline": new_deadline,
            "priority": new_priority,
            "description": new_description
        }
        tasks_data[index] = updated_task
        update_listbox()
        edit_window.destroy()

    ttk.Button(edit_window, text="Save Changes", command=confirm_edit).grid(row=5, column=0, columnspan=2, padx=10, pady=10)

def remove_task():
    selection = task_listbox.curselection()
    if selection:
        index = selection[0]
        task_listbox.delete(index)
        del tasks_data[index]
    else:
        messagebox.showinfo("Remove Task", "No task is selected.")

# load tasks from json and add to listbox
def load_tasks():
    global tasks_data
    if os.path.exists(TASKS_FILENAME):
        try:
            with open(TASKS_FILENAME, "r")  as file:
                tasks_data = json.load(file)
                for task in tasks_data:
                    task_listbox.insert(tk.END, format_task(task))
        except json.JSONDecodeError:
            messagebox.showerror("Load Error", "Tasks file not found.")

# save tasks to json
def save_tasks():
    with open(TASKS_FILENAME, "w") as file:
        json.dump(tasks_data, file, indent=4)

def on_closing():
    save_tasks()
    root.destroy()

# create main window
root = tk.Tk()
root.title("Task Manager")
root.protocol("WM_DELETE_WINDOW", on_closing)

# create frame to hold widgets
main_frame = ttk.Frame(root, padding="10")
main_frame.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W))

# add button, opens add task window
add_button = tk.Button(main_frame, text="Add New Task", command=open_add_task_window, bg="green", fg="white")
add_button.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

# remove button, removes selected task  NEED TO FIX LOCATION OF REMOVE
remove_button = tk.Button(main_frame, text="Remove Selected Task", command=remove_task, bg="red", fg="white")
remove_button.grid(row=0, column=1, padx=10, pady=10)

# edit button, opens edit task window
edit_button = tk.Button(main_frame, text="Edit Selected Task", command=open_edit_task_window, bg="orange", fg="white")
edit_button.grid(row=0, column=2, padx=10, pady=10)

# create listbox to display tasks
task_listbox = tk.Listbox(main_frame, width=80, height=10)
task_listbox.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

# sorting controls
sort_label = ttk.Label(main_frame, text="Sort by:")
sort_label.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)

sort_options = ["Task Name", "Deadline", "Priority"]
sort_var = tk.StringVar()
sort_var.set(sort_options[0])
sort_menu = ttk.Combobox(main_frame, textvariable=sort_var, values=sort_options, state="readonly")
sort_menu.grid(row=2, column=0, padx=(70, 10), pady=5, sticky=tk.W)

sort_button = tk.Button(main_frame, text="Sort Tasks", command=sort_tasks, bg="blue", fg="white")
sort_button.grid(row=2, column=2, padx=10, pady=10, sticky=tk.E)

# loads tasks from file if there is one when app starts
load_tasks()

# call made for live countdown
update_timers()

# run the tkinter event loop
root.mainloop()