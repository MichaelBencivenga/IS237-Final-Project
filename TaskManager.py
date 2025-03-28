import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

TASKS_FILENAME = "tasks.json"

def open_add_task_window():
    # create new window for task input
    add_window = tk.Toplevel(root)
    add_window.title("Add New Task")

    label = ttk.Label(add_window, text="Enter the new task:")
    label.grid(row=0, column=0, padx=10, pady=10)

    # entry widget for the new task
    new_task_entry = ttk.Entry(add_window, width=40)
    new_task_entry.grid(row=1, column=0, padx=10, pady=10)
    new_task_entry.focus()

    # function to add new task input and close the window
    def confirm_add():
        task = new_task_entry.get()
        if task:
            task_listbox.insert(tk.END, task)
            add_window.destroy()
        else:
            messagebox.showwarning("Input Error", "Please enter a task.")

    # button to confirm adding new task
    confirm_button = ttk.Button(add_window, text="Add New Task", command=confirm_add)
    confirm_button.grid(row=2, column=0, padx=10, pady=10)

def remove_task():
    selection = task_listbox.curselection()
    if selection:
        task_listbox.delete(selection[0])
    else:
        messagebox.showinfo("Remove Task", "No task is selected.")

# load tasks from json and add to listbox
def load_tasks():
    if os.path.exists(TASKS_FILENAME):
        try:
            with open(TASKS_FILENAME, "r")  as file:
                tasks = json.load(file)
                for task in tasks:
                    task_listbox.insert(tk.END, task)
        except json.JSONDecodeError:
            messagebox.showerror("Load Error", "Tasks file not found.")

# save tasks from listbox to json
def save_tasks():
    tasks = task_listbox.get(0, tk.END)
    with open(TASKS_FILENAME, "w") as file:
        json.dump(tasks, file)

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

# add button that calls add_task when clicked
add_button = tk.Button(main_frame, text="Add New Task", command=open_add_task_window, bg="green", fg="white")
add_button.grid(row=0, column=0, padx=10, pady=10)

# remove button that calls remove_task when clicked
remove_button = tk.Button(main_frame, text="Remove Selected Task", command=remove_task, bg="red", fg="white")
remove_button.grid(row=0, column=1, padx=10, pady=10)

# create listbox to display tasks
task_listbox = tk.Listbox(main_frame, width=50, height=10)
task_listbox.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

# loads tasks from file if there is one when app starts
load_tasks()

# run the tkinter event loop
root.mainloop()