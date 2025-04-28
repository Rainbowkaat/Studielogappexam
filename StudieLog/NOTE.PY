import os
import mysql.connector
from tkinter import *
from tkinter import ttk, messagebox, filedialog, colorchooser
from tkinter.font import Font
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image
import time
import threading

# Connect to MySQL database
def connect_to_db():
    return mysql.connector.connect(
        host='localhost',
        user='Studielog_user',
        password='Rubi3!SQL_2025',
        database='StudieLogApp'
    )

db = connect_to_db()
cursor = db.cursor()

# Create necessary tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS folders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    color VARCHAR(7) DEFAULT '#FFFFFF'
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    folder_id INT,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    FOREIGN KEY (folder_id) REFERENCES folders(id) ON DELETE CASCADE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS reminders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    due_date DATE NOT NULL
)
""")

# Functions
def create_folder():
    name = folder_name_entry.get()
    if name:
        color = "#FFFFFF"  # Default color
        cursor.execute("INSERT INTO folders (name, color) VALUES (%s, %s)", (name, color))
        db.commit()
        folder_name_entry.delete(0, 'end')
        refresh_folders()
        status_label.config(text=f"Folder '{name}' created.")

def delete_folder():
    try:
        selected = folder_listbox.get(folder_listbox.curselection())
        folder_id = int(selected.split(":")[0])
        cursor.execute("DELETE FROM folders WHERE id = %s", (folder_id,))
        db.commit()
        refresh_folders()
        status_label.config(text=f"Folder with ID {folder_id} deleted.")
    except Exception as e:
        messagebox.showerror("Error", "Please select a folder to delete.")

def refresh_folders():
    folder_listbox.delete(0, 'end')
    cursor.execute("SELECT id, name, color FROM folders")
    for folder_id, name, color in cursor.fetchall():
        folder_listbox.insert('end', f"{folder_id}: {name}")
        # Keep the background color from the database
        # folder_listbox.itemconfig('end', {'bg': color})

def create_note():
    try:
        selected = folder_listbox.get(folder_listbox.curselection())
        folder_id = int(selected.split(":")[0])
        title = note_title_entry.get()
        content = note_content_text.get("1.0", "end-1c")
        if title and content:
            cursor.execute("INSERT INTO notes (folder_id, title, content) VALUES (%s, %s, %s)", (folder_id, title, content))
            db.commit()
            note_title_entry.delete(0, 'end')
            note_content_text.delete("1.0", 'end')
            status_label.config(text=f"Note '{title}' created in folder ID {folder_id}.")
    except Exception as e:
        messagebox.showerror("Error", "Please select a folder to create a note.")

def list_notes():
    try:
        selected = folder_listbox.get(folder_listbox.curselection())
        folder_id = int(selected.split(":")[0])
        cursor.execute("SELECT * FROM notes WHERE folder_id = %s", (folder_id,))
        notes_listbox.delete(0, 'end')
        for note in cursor.fetchall():
            notes_listbox.insert('end', f"{note[0]}: {note[1]}")
    except Exception as e:
        messagebox.showerror("Error", "Please select a folder to list notes.")

def export_note():
    try:
        selected_note = notes_listbox.get(notes_listbox.curselection())
        note_id = int(selected_note.split(":")[0])
        cursor.execute("SELECT title, content FROM notes WHERE id = %s", (note_id,))
        note = cursor.fetchone()
        if note:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
            if file_path:
                with open(file_path, "w") as file:
                    file.write(f"Title: {note[0]}\n\n{note[1]}")
                status_label.config(text=f"Note '{note[0]}' exported successfully.")
    except Exception as e:
        messagebox.showerror("Error", "Please select a note to export.")

def move_note():
    try:
        selected_note = notes_listbox.get(notes_listbox.curselection())
        note_id = int(selected_note.split(":")[0])
        selected_folder = folder_listbox.get(folder_listbox.curselection())
        folder_id = int(selected_folder.split(":")[0])
        cursor.execute("UPDATE notes SET folder_id = %s WHERE id = %s", (folder_id, note_id))
        db.commit()
        list_notes()
        status_label.config(text=f"Note moved to folder ID {folder_id}.")
    except Exception as e:
        messagebox.showerror("Error", "Please select a note and a folder to move.")

def change_folder_color():
    try:
        selected = folder_listbox.get(folder_listbox.curselection())
        folder_id = int(selected.split(":")[0])
        color_code = colorchooser.askcolor(title="Choose Folder Color")[1]
        if color_code:
            cursor.execute("UPDATE folders SET color = %s WHERE id = %s", (color_code, folder_id))
            db.commit()
            refresh_folders()
            status_label.config(text=f"Folder color updated to {color_code}.")
    except Exception as e:
        messagebox.showerror("Error", "Please select a folder to change its color.")

def render_equation():
    equation = note_content_text.get("1.0", "end-1c")
    if equation:
        try:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, f"${equation}$", fontsize=20, ha='center', va='center')
            ax.axis('off')
            buf = BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            img = Image.open(buf)
            img.show()
            buf.close()
        except Exception as e:
            messagebox.showerror("Error", "Invalid equation syntax.")

def insert_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
    if file_path:
        try:
            img = Image.open(file_path)
            img.show()
        except Exception as e:
            messagebox.showerror("Error", "Could not open the image.")

def change_font():
    selected_font = font_var.get()
    selected_size = font_size_var.get()
    selected_style = font_style_var.get()
    font_config = f"{selected_font} {selected_size} {selected_style}"
    note_content_text.config(font=font_config)

def style_button(button, color):
    button.configure(bootstyle=color, padding=5)

# GUI Setup
app = tb.Window(themename="flatly")  # Set light theme to "flatly"
app.title("Study Notes App")
app.geometry("1200x900")
try:
    app.iconphoto(False, PhotoImage(file="Media/StudieLog_Logo.png"))  # Replace with the path to your icon
except TclError:
    print("Icon file not found.")

# Welcome Popup
def show_welcome_popup():
    messagebox.showinfo(
        "Velkommen til StudieLog!",
        "Tag noter og organiser dine studier her. Start med at skrive dine noter."
    )

# Font Selection
font_var = StringVar(value="Arial")
font_size_var = StringVar(value="12")
font_style_var = StringVar(value="normal")

font_frame = tb.LabelFrame(app, text="Font Settings", padding=10, bootstyle=INFO)
font_frame.pack(fill=X, padx=10, pady=5)

font_menu = ttk.Combobox(font_frame, textvariable=font_var, values=["Arial", "Courier", "Times", "Helvetica"])
font_menu.pack(side=LEFT, padx=5)

font_size_menu = ttk.Combobox(font_frame, textvariable=font_size_var, values=[str(i) for i in range(8, 32)])
font_size_menu.pack(side=LEFT, padx=5)

font_style_menu = ttk.Combobox(font_frame, textvariable=font_style_var, values=["normal", "bold", "italic", "underline"])
font_style_menu.pack(side=LEFT, padx=5)

apply_font_button = tb.Button(font_frame, text="Apply Font", command=change_font, bootstyle=SUCCESS)
style_button(apply_font_button, color="success") # Changed button color
apply_font_button.pack(side=LEFT, padx=5)

# Folder Section
folder_frame = tb.LabelFrame(app, text="Folders", padding=10, bootstyle=PRIMARY)
folder_frame.pack(side=LEFT, fill=Y, padx=10, pady=10)

folder_name_entry = tb.Entry(folder_frame, width=30)
folder_name_entry.pack(pady=5)

create_folder_button = tb.Button(folder_frame, text="Create Folder", command=create_folder, bootstyle="primary") # Changed button color
style_button(create_folder_button, color="primary")
create_folder_button.pack(pady=5)

delete_folder_button = tb.Button(folder_frame, text="Delete Folder", command=delete_folder, bootstyle="danger") # Changed button color
style_button(delete_folder_button, color="danger")
delete_folder_button.pack(pady=5)

change_color_button = tb.Button(folder_frame, text="Change Folder Color", command=change_folder_color, bootstyle="info") # Changed button color
style_button(change_color_button, color="info")
change_color_button.pack(pady=5)

folder_listbox = Listbox(folder_frame, width=40, height=10)
folder_listbox.pack(pady=5)
refresh_folders_button = tb.Button(folder_frame, text="Refresh Folders", command=refresh_folders, bootstyle="info") # Changed button color
style_button(refresh_folders_button, color="info")
refresh_folders_button.pack(pady=5)

# Notes Section
notes_frame = tb.LabelFrame(app, text="Notes", padding=10, bootstyle=INFO)
notes_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)

note_title_entry = tb.Entry(notes_frame, width=40)
note_title_entry.pack(pady=5)

note_content_text = Text(notes_frame, width=40, height=10, wrap=WORD, font=("Arial", 12))
note_content_text.pack(pady=5)

create_note_button = tb.Button(notes_frame, text="Create Note", command=create_note, bootstyle="success") # Changed button color
style_button(create_note_button, color="success")
create_note_button.pack(pady=5)

list_notes_button = tb.Button(notes_frame, text="List Notes", command=list_notes, bootstyle="info") # Changed button color
style_button(list_notes_button, color="info")
list_notes_button.pack(pady=5)

export_note_button = tb.Button(notes_frame, text="Export Note", command=export_note, bootstyle="info") # Changed button color
style_button(export_note_button, color="info")
export_note_button.pack(pady=5)

move_note_button = tb.Button(notes_frame, text="Move Note", command=move_note, bootstyle="info") # Changed button color
style_button(move_note_button, color="info")
move_note_button.pack(pady=5)

notes_listbox = Listbox(notes_frame, width=40, height=10)
notes_listbox.pack(pady=5)

status_label = Label(app, text="Welcome!", anchor=W, font=("Arial", 10), relief=SUNKEN, height=2)
status_label.pack(side=BOTTOM, fill=X)

# Show welcome popup when the app starts
app.after(100, show_welcome_popup)

app.mainloop()