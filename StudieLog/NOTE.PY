import os
import mysql.connector
from tkinter import *
from tkinter import ttk, messagebox, filedialog, colorchooser
from tkinter.font import Font
import ttkbootstrap as tb
from ttkbootstrap.constants import *

# --- Database Forbindelse ---
def connect_to_db():
    """
    Opretter en forbindelse til MySQL-databasen.
    VIGTIGT: Tjek at MySQL serveren kører, og at login-oplysningerne er korrekte!
    """
    try:
        return mysql.connector.connect(
            host='localhost',
            user='Studielog_user',
            password='Rubi3!SQL_2025',
            database='StudieLogApp'
        )
    except mysql.connector.Error as err:
        messagebox.showerror("Database Forbindelsesfejl", f"Kunne ikke oprette forbindelse til databasen: {err}\n\nTjek MySQL serveren og dine login-oplysninger.")
        raise

# Opret databaseforbindelse og cursor
try:
    db = connect_to_db()
    cursor = db.cursor()
except Exception as e:
    print(f"KRITISK FEJL: Appen kunne ikke starte pga. databasefejl: {e}")
    exit()

# --- Database Skema --- updatee
# Tidligere indeholdt dette afsnit DROP TABLE og CREATE TABLE statements.
# Disse er fjernet, da databasens skema nu forventes at være oprettet
# via et separat MySQL script (f.eks. i MySQL Workbench) EEN GANG.
# Appen skal kun forbinde sig til den eksisterende database, ikke oprette den ved hver opstart.


# --- Applikationsfunktioner ---

def create_folder():
    """Opretter en ny mappe i databasen baseret på brugerinput."""
    name = folder_name_entry.get().strip()
    if name:
        color = "#6365E8" # Standardfarve
        try:
            # SQL INSERT-kommando for at tilføje en ny mappe til 'folders'-tabellen
            cursor.execute("INSERT INTO folders (name, color) VALUES (%s, %s)", (name, color))
            db.commit() # Gem ændringerne permanent i databasen
            folder_name_entry.delete(0, 'end') # Ryd inputfeltet
            refresh_folders() # Opdater mappelisten i GUI'en
            status_label.config(text=f"Mappe '{name}' oprettet.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Fejl", f"Fejl ved oprettelse af mappe: {err}\n\nTjek din databaseforbindelse.")
    else:
        messagebox.showwarning("Input Fejl", "Mappenavn må ikke være tomt.")

def delete_folder():
    """Sletter den valgte mappe og alle tilhørende noter fra databasen."""
    try:
        selected = folder_listbox.get(folder_listbox.curselection()) # Få valgt mappe fra listen
        folder_id = int(selected.split(":")[0]) # Udtræk mappe-ID'et
        # Bekræft sletning med brugeren
        if messagebox.askyesno("Bekræft Sletning", f"Er du sikker på, at du vil slette mappe ID {folder_id}? Alle noter i denne mappe vil også blive slettet."):
            try:
                # SQL DELETE-kommando for at slette mappen
                # ON DELETE CASCADE i databasen sørger for at slette tilhørende noter automatisk
                cursor.execute("DELETE FROM folders WHERE id = %s", (folder_id,))
                db.commit() # Gem ændringerne permanent
                refresh_folders() # Opdater mappelisten
                status_label.config(text=f"Mappe med ID {folder_id} slettet.")
                notes_listbox.delete(0, 'end') # Ryd notelisten, da mappen og dens noter er væk
            except mysql.connector.Error as err:
                messagebox.showerror("Database Fejl", f"Fejl ved sletning af mappe: {err}")
    except TclError:
        messagebox.showerror("Fejl", "Vælg venligst en mappe, du vil slette.")
    except Exception as e:
        messagebox.showerror("Fejl", f"Der opstod en uventet fejl: {e}")

def refresh_folders():
    """Opdaterer listen over mapper vist i mappelisten."""
    folder_listbox.delete(0, 'end') # Ryd den nuværende liste
    try:
        # SQL SELECT-kommando for at hente alle mapper
        cursor.execute("SELECT id, name, color FROM folders")
        # Gå igennem alle fundne mapper og indsæt dem i listbox'en
        for folder_id, name, color in cursor.fetchall():
            folder_listbox.insert('end', f"{folder_id}: {name}")
    except mysql.connector.Error as err:
        messagebox.showerror("Database Fejl", f"Fejl ved opdatering af mapper: {err}")

def create_note():
    """Opretter en ny note inden for den valgte mappe."""
    try:
        selected_folder = folder_listbox.get(folder_listbox.curselection()) # Få valgt mappe
        folder_id = int(selected_folder.split(":")[0]) # Udtræk mappe-ID

        title = note_title_entry.get().strip() # Få notetitel fra inputfelt
        content = note_content_text.get("1.0", "end-1c").strip() # Få noteindhold fra tekstfelt

        # Inputvalidering: Tjek om titel eller indhold er tomme
        if not title:
            messagebox.showwarning("Input Fejl", "Notetitel må ikke være tom.")
            return
        if not content:
            messagebox.showwarning("Input Fejl", "Noteindhold må ikke være tom.")
            return

        try:
            # SQL INSERT-kommando for at tilføje en ny note
            cursor.execute("INSERT INTO notes (folder_id, title, content) VALUES (%s, %s, %s)", (folder_id, title, content))
            db.commit() # Gem ændringerne permanent
            note_title_entry.delete(0, 'end') # Ryd inputfelter
            note_content_text.delete("1.0", 'end')
            list_notes() # Opdater notelisten for den valgte mappe
            status_label.config(text=f"Note '{title}' oprettet i mappe ID {folder_id}.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Fejl", f"Fejl ved oprettelse af note: {err}")
    except TclError:
        messagebox.showerror("Fejl", "Vælg venligst en mappe for at oprette en note.")
    except Exception as e:
        messagebox.showerror("Fejl", f"Der opstod en uventet fejl: {e}")

def list_notes():
    """Viser alle noter for den aktuelt valgte mappe i notelisten."""
    try:
        selected_folder = folder_listbox.get(folder_listbox.curselection()) # Få valgt mappe
        folder_id = int(selected_folder.split(":")[0]) # Udtræk mappe-ID
        notes_listbox.delete(0, 'end') # Ryd notelisten

        try:
            # SQL SELECT-kommando for at hente noter kun for den valgte mappe
            cursor.execute("SELECT id, title FROM notes WHERE folder_id = %s", (folder_id,))
            # Gå igennem fundne noter og indsæt dem i listbox'en
            for note_id, title in cursor.fetchall():
                notes_listbox.insert('end', f"{note_id}: {title}")
            status_label.config(text=f"Noter i mappe ID {folder_id} vist.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Fejl", f"Fejl ved visning af noter: {err}")
    except TclError:
        messagebox.showerror("Fejl", "Vælg venligst en mappe for at se noter.")
    except Exception as e:
        messagebox.showerror("Fejl", f"Der opstod en uventet fejl: {e}")

def export_note():
    """Eksporterer indholdet af den valgte note til en .txt-fil."""
    try:
        selected_note = notes_listbox.get(notes_listbox.curselection()) # Få valgt note
        note_id = int(selected_note.split(":")[0]) # Udtræk note-ID
        try:
            # SQL SELECT-kommando for at hente noteindhold
            cursor.execute("SELECT title, content FROM notes WHERE id = %s", (note_id,))
            note = cursor.fetchone() # Hent en enkelt note
            if note:
                # Åbn filgem-dialog for brugeren
                file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Tekstfiler", "*.txt"), ("Alle filer", "*.*")])
                if file_path:
                    # Skriv noteindhold til filen
                    with open(file_path, "w", encoding="utf-8") as file:
                        file.write(f"Titel: {note[0]}\n\nIndhold:\n{note[1]}")
                    status_label.config(text=f"Note '{note[0]}' eksporteret med succes.")
                else:
                    status_label.config(text="Eksport annulleret.")
            else:
                messagebox.showwarning("Note Ikke Fundet", "Den valgte note kunne ikke findes i databasen.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Fejl", f"Fejl ved hentning af note til eksport: {err}")
    except TclError:
        messagebox.showerror("Fejl", "Vælg venligst en note, du vil eksportere.")
    except Exception as e:
        messagebox.showerror("Fejl", f"Der opstod en uventet fejl: {e}")

def move_note():
    """Flytter den valgte note til en anden mappe."""
    try:
        selected_note_info = notes_listbox.get(notes_listbox.curselection()) # Få info om valgt note
        note_id = int(selected_note_info.split(":")[0]) # Udtræk note-ID

        selected_folder_info = folder_listbox.get(folder_listbox.curselection()) # Få info om ny mappe
        new_folder_id = int(selected_folder_info.split(":")[0]) # Udtræk ID for ny mappe

        try:
            # SQL UPDATE-kommando for at ændre 'folder_id' for noten
            cursor.execute("UPDATE notes SET folder_id = %s WHERE id = %s", (new_folder_id, note_id))
            db.commit() # Gem ændringerne permanent
            list_notes() # Opdater notelisten for den nuværende mappe (noten er nu flyttet væk fra den)
            status_label.config(text=f"Note flyttet til mappe ID {new_folder_id}.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Fejl", f"Fejl ved flytning af note: {err}")
    except TclError:
        messagebox.showerror("Fejl", "Vælg venligst en note OG en mappe for at flytte.")
    except Exception as e:
        messagebox.showerror("Fejl", f"Der opstod en uventet fejl: {e}")

def change_folder_color():
    """Giver brugeren mulighed for at vælge en farve til den valgte mappe."""
    try:
        selected = folder_listbox.get(folder_listbox.curselection()) # Få valgt mappe
        folder_id = int(selected.split(":")[0]) # Udtræk mappe-ID
        color_code = colorchooser.askcolor(title="Vælg Mappefarve")[1] # Åbn farvevælger
        if color_code: # Hvis en farve blev valgt
            try:
                # SQL UPDATE-kommando for at ændre mappens farve
                cursor.execute("UPDATE folders SET color = %s WHERE id = %s", (color_code, folder_id))
                db.commit() # Gem ændringerne permanent
                refresh_folders() # Opdater mappelisten for at vise ny farve (hvis din GUI understøtter farvevisning)
                status_label.config(text=f"Mappefarve opdateret til {color_code}.")
            except mysql.connector.Error as err:
                messagebox.showerror("Database Fejl", f"Fejl ved opdatering af mappefarve: {err}")
        else:
            status_label.config(text="Farvevalg annulleret.")
    except TclError:
        messagebox.showerror("Fejl", "Vælg venligst en mappe for at ændre dens farve.")
    except Exception as e:
        messagebox.showerror("Fejl", f"Der opstod en uventet fejl: {e}")

# Fjernet: render_equation og insert_image funktioner (da de ikke var i din oprindelige plan/kode)

def change_font():
    """Anvender den valgte skrifttype, størrelse og stil til notatets tekstområde."""
    selected_font = font_var.get()
    selected_size = font_size_var.get()
    selected_style = font_style_var.get()
    font_config = f"{selected_font} {selected_size} {selected_style}"
    note_content_text.config(font=font_config)
    status_label.config(text=f"Skrifttype ændret til {selected_font}, {selected_size}, {selected_style}.")

def style_button(button, color):
    """Anvender en ttkbootstrap stil og padding til en knap."""
    button.configure(bootstyle=color, padding=5)

    
# --- GUI Opsætning ---
app = tb.Window(themename="flatly")
app.title("StudieLog App")
app.geometry("1200x900")

# Definer StringVars for skrifttypeindstillinger
font_var = StringVar(value="Arial")
font_size_var = StringVar(value="12")
font_style_var = StringVar(value="normal")

# Velkomst Pop-up
def show_welcome_popup():
    """Viser en velkomstbesked til brugeren, når applikationen starter."""
    messagebox.showinfo(
        "Velkommen til StudieLog!",
        "Tag noter og organiser dine studier her. Start med at oprette en mappe og derefter dine noter."
    )

# Skrifttypevalg Ramme
font_frame = tb.LabelFrame(app, text="Skrifttypeindstillinger", padding=10, bootstyle=INFO)
font_frame.pack(fill=X, padx=10, pady=5)

font_menu = ttk.Combobox(font_frame, textvariable=font_var, values=["Arial", "Courier New", "Times New Roman", "Helvetica", "Verdana"])
font_menu.set("Arial")
font_menu.pack(side=LEFT, padx=5)

font_size_menu = ttk.Combobox(font_frame, textvariable=font_size_var, values=[str(i) for i in range(8, 32, 2)])
font_size_menu.set("12")
font_size_menu.pack(side=LEFT, padx=5)

font_style_menu = ttk.Combobox(font_frame, textvariable=font_style_var, values=["normal", "bold", "italic", "underline"])
font_style_menu.set("normal")
font_style_menu.pack(side=LEFT, padx=5)

apply_font_button = tb.Button(font_frame, text="Anvend Skrifttype", command=change_font, bootstyle=SUCCESS)
style_button(apply_font_button, color="success")
apply_font_button.pack(side=LEFT, padx=5)

# Mappe sektion
folder_frame = tb.LabelFrame(app, text="Mapper", padding=10, bootstyle=PRIMARY)
folder_frame.pack(side=LEFT, fill=Y, padx=10, pady=10)

folder_name_entry = tb.Entry(folder_frame, width=30)
folder_name_entry.pack(pady=5)

create_folder_button = tb.Button(folder_frame, text="Opret Mappe", command=create_folder, bootstyle="primary")
style_button(create_folder_button, color="primary")
create_folder_button.pack(pady=5)

delete_folder_button = tb.Button(folder_frame, text="Slet Mappe", command=delete_folder, bootstyle="danger")
style_button(delete_folder_button, color="danger")
delete_folder_button.pack(pady=5)

change_color_button = tb.Button(folder_frame, text="Skift Mappefarve", command=change_folder_color, bootstyle="info")
style_button(change_color_button, color="info")
change_color_button.pack(pady=5)

folder_listbox = Listbox(folder_frame, width=40, height=10, selectmode=SINGLE, exportselection=False)
folder_listbox.pack(pady=5)
refresh_folders_button = tb.Button(folder_frame, text="Opdater Mapper", command=refresh_folders, bootstyle="info")
style_button(refresh_folders_button, color="info")
refresh_folders_button.pack(pady=5)

# Notat sektion
notes_frame = tb.LabelFrame(app, text="Noter", padding=10, bootstyle=INFO)
notes_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)

note_title_entry = tb.Entry(notes_frame, width=40)
note_title_entry.pack(pady=5)

# Tilføjet en scrollbar til tekst-widgetten
note_content_scrollbar = ttk.Scrollbar(notes_frame)
note_content_scrollbar.pack(side=RIGHT, fill=Y)
note_content_text = Text(notes_frame, width=40, height=10, wrap=WORD, font=("Arial", 12),
                          yscrollcommand=note_content_scrollbar.set)
note_content_text.pack(pady=5, fill=BOTH, expand=True)
note_content_scrollbar.config(command=note_content_text.yview)


create_note_button = tb.Button(notes_frame, text="Opret Note", command=create_note, bootstyle="success")
style_button(create_note_button, color="success")
create_note_button.pack(pady=5)

list_notes_button = tb.Button(notes_frame, text="Vis Noter", command=list_notes, bootstyle="info")
style_button(list_notes_button, color="info")
list_notes_button.pack(pady=5)

export_note_button = tb.Button(notes_frame, text="Eksporter Note", command=export_note, bootstyle="info")
style_button(export_note_button, color="info")
export_note_button.pack(pady=5)

move_note_button = tb.Button(notes_frame, text="Flyt Note", command=move_note, bootstyle="info")
style_button(move_note_button, color="info")
move_note_button.pack(pady=5)


notes_listbox = Listbox(notes_frame, width=40, height=10, selectmode=SINGLE, exportselection=False)
notes_listbox.pack(pady=5, fill=BOTH, expand=True)

status_label = Label(app, text="Velkommen!", anchor=W, font=("Arial", 10), relief=SUNKEN, height=2)
status_label.pack(side=BOTTOM, fill=X)

# Vis velkomst-popup når appen starter
app.after(100, show_welcome_popup)

# Indledende opdatering af mapper, når appen starter
app.after(200, refresh_folders)

app.mainloop()

# Luk databaseforbindelsen, når appen lukker
if 'cursor' in locals() and cursor:
    cursor.close()
if 'db' in locals() and db:
    db.close()
