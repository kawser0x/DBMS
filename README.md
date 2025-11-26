# DBMS
FINAL PROJECT

📰 News Management System (GUI)

A modern, author-centric desktop application for managing news articles. Built with Python (CustomTkinter) and MySQL, featuring user authentication, session persistence, and a recycle bin safety system.

✨ Key Features

🔐 Author Authentication

Login/Register: Secure access for multiple authors.
Session Persistence: The app remembers you! Close the program and reopen it to stay logged in.
Secure Logout: Logging out clears your session and empties your local recycle bin.

📝 Content Management (CRUD)

Create: Publish articles linked automatically to your account.
Read: Browse all articles with a smart Category Filter.
Update/Delete: Edit or remove articles only if you are the author. The system protects other authors' work.

♻️ Safety Features

Recycle Bin: Deleted articles aren't lost immediately. They move to a persistent Recycle Bin.
Restore: Accidentally deleted something? Restore it with one click.
Auto-Empty: The bin is permanently cleared only when you explicitly Log Out.

🎨 Modern UI

Built with CustomTkinter for a sleek "Professional Navy" dark mode theme.
Centered windows and responsive layouts.
🗄️ Database Structure (E-R Diagram)
The system relies on a relational database connecting Authors, Categories, and Articles.

erDiagram
    AUTHORS ||--o{ ARTICLES : "writes (1:N)"
    CATEGORIES ||--o{ ARTICLES : "classifies (1:N)"

    AUTHORS {
        int author_id PK
        varchar name
        varchar email
        text bio
    }

    CATEGORIES {
        int category_id PK
        varchar category_name
    }

    ARTICLES {
        int article_id PK
        varchar title
        text content
        datetime publication_date
        int author_id FK
        int category_id FK
    }


🚀 Installation & Setup

Prerequisites

Python 3.x installed.
MySQL Server installed and running.

1. Clone the Repository

git clone [(https://github.com/kawser0x/DBMS/blob/main/README.md)](https://github.com/kawser0x/DBMS/blob/main/README.md)
cd news-management-system

2. Install Dependencies

Install the required Python libraries:
pip install mysql-connector-python customtkinter


3. Database Setup

Open your MySQL Workbench or Command Line.
Run the script provided in news_management_f.sql  to create the database and tables.

4. Configuration

Open news_gui_manager.py and update the database connection settings at the top of the file:
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password", 
    database="news_manage"
)


5. Run the App

python DBMS_Final_Project.py


📸 Usage Guide

Register: Click "Register New Author" on the login screen.
Login: Use your Name and Email (acts as password) to log in.
Create: Use the dashboard menu to add Categories and Articles.
Manage: Click "Manage My Articles" to edit or delete your content.
Recycle Bin: View deleted items by clicking the "Recycle Bin" button on the dashboard.
