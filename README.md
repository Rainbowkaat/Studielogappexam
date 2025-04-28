# Studielogappexam
Examsprojekt
```markdown
# StudieLog

En simpel notat-applikation lavet i Python.

## GitHub Brugernavn

Rainbowkaat

## Krav

Denne applikation har brug for følgende biblioteker, som findes i mappen `requirements`:

* **mysql-connector-python**: For at forbinde til og arbejde med MySQL databasen.
* **tkinter**: Pythons standard værktøj til at lave brugergrænser (GUI).
* **matplotlib**: For at vise matematiske formler i noter.
* **Pillow (PIL)**: For at håndtere billeder i noter.
* **ttkbootstrap**: Et moderne tema til Tkinter, som får appen til at se bedre ud.

Du kan installere disse ved at bruge `pip`:

```bash
pip install -r requirements/requirements.txt
```

## Installation

1.  **Klon repositoryet:**
    ```bash
    git clone [https://github.com/Rainbowkaat/StudieLog.git](https://github.com/Rainbowkaat/StudieLog.git)
    cd StudieLog
    ```

2.  **Installer de nødvendige ting:**
    Gå til mappen `StudieLog` og kør:
    ```bash
    pip install -r requirements/requirements.txt
    ```

3.  **Opsæt MySQL databasen:**
    * Sørg for at du har MySQL installeret og kører.
    * Lav en database der hedder `StudieLogApp`.
    * Lav en bruger der hedder `Studielog_user` med kodeordet `Rubi3!SQL_2025` og giv den tilladelse til `StudieLogApp` databasen.

## Brug

For at starte appen, kør filen `note.py`:

```bash
python note.py
```

Appen kan bruges til at:

* **Lav Mapper:** Hold dine noter organiserede i forskellige mapper.
* **Slet Mapper:** Fjern mapper du ikke skal bruge mere.
* **Skift Farve på Mapper:** Gør dine mapper personlige med farver.
* **Lav Noter:** Skriv dine tanker og ideer ned i mapperne.
* **Se Noter:** Kig på de noter der er i en mappe.
* **Gem Noter:** Gem enkelte noter som `.txt` filer.
* **Flyt Noter:** Put noter fra en mappe til en anden.
* **Vis Formler:** Se matematiske formler (LaTeX) i dine noter.
* **Indsæt Billeder:** Se billedfiler i appen (men de er ikke direkte i noten).
* **Ændre Skrift:** Vælg skrifttype, størrelse og stil til dine noter.

Når du starter appen, kommer der en kort besked på dansk, der siger at du kan begynde at skrive noter.


