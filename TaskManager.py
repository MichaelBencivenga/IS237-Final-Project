import tkinter as tk

# create main window
root = tk.Tk()
root.title("Task Manager Hello World")

# create a label widget
label = tk.Label(root, text="Hello World")
label.pack()

# run the tkinter event loop
root.mainloop()