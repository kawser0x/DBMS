import mysql.connector
import customtkinter as ctk
import tkinter.messagebox as tkmb
from tkinter import END
import sys
import json
import os

SESSION_FILE = "user_session.json"
BIN_FILE = "recycle_bin.json"

def get_db_connection(parent=None):
    """Establishes connection, showing errors over the specific parent window."""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="password",
            database="dbms_news"
        )
        return conn
    except mysql.connector.Error as err:
        tkmb.showerror("Database Error", f"Error connecting to MySQL:\n{err}", parent=parent)
        return None

def db_execute(query, params=(), fetch=False, parent=None):
    conn = get_db_connection(parent=parent)
    if not conn: return None
    
    cursor = conn.cursor()
    result = None
    try:
        cursor.execute(query, params)
        if fetch:
            result = cursor.fetchall()
        else:
            conn.commit()
    except mysql.connector.Error as err:
        tkmb.showerror("SQL Error", f"Operation failed:\n{err}", parent=parent)
    finally:
        cursor.close()
        conn.close()
    return result

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))
    window.geometry(f'{width}x{height}+{x}+{y}')

def save_session(author_id, author_name):
    data = {"id": author_id, "name": author_name}
    try:
        with open(SESSION_FILE, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Failed to save session: {e}")

def load_session():
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, 'r') as f:
                return json.load(f)
        except:
            return None
    return None

def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

THEME = {
    "BG": "#0a192f",          
    "FG": "#e6f1ff",          
    "CARD_BG": "#112240",     
    "BORDER": "#233554",      
    "BTN_CREATE": "#64ffda",  
    "BTN_READ": "#2196F3",    
    "BTN_UPDATE": "#ff9f1c",  
    "BTN_DELETE": "#ff5252",  
    "BTN_LOGOUT": "#9c27b0",  
    "BTN_EXIT": "#607d8b",    
    "HOVER_GENERIC": "#1d3557"
}

class DashboardWindow(ctk.CTkToplevel):
    def __init__(self, author_data, login_instance):
        super().__init__()
        self.author_id = author_data[0]
        self.author_name = author_data[1]
        self.login_instance = login_instance 
        
        self.recycle_bin = [] 
        self.load_bin() 
        
        self.title(f"Dashboard - {self.author_name}")
        center_window(self, 550, 720)
        self.configure(fg_color=THEME["BG"])
        
        self.lift()
        self.focus_force()
        
        self.lbl_title = ctk.CTkLabel(self, text=f"Welcome, {self.author_name}", 
                                      font=("Arial", 24, "bold"), text_color=THEME["FG"])
        self.lbl_title.pack(pady=(30, 20))

        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=10)

        self.btn_create = ctk.CTkButton(self.btn_frame, text="✚ Create Article", 
                                        fg_color=THEME["BTN_CREATE"], text_color="black", hover_color="#b2fef7",
                                        width=280, height=45, font=("Arial", 15, "bold"),
                                        command=self.open_create_article_form)
        self.btn_create.pack(pady=8)

        self.btn_read = ctk.CTkButton(self.btn_frame, text="👀 Read All Articles", 
                                      fg_color=THEME["BTN_READ"], text_color="white", hover_color="#42a5f5",
                                      width=280, height=45, font=("Arial", 15, "bold"),
                                      command=lambda: self.open_manage_window(show_only_mine=False))
        self.btn_read.pack(pady=8)

        self.btn_manage = ctk.CTkButton(self.btn_frame, text="✏️ Manage My Articles", 
                                        fg_color=THEME["BTN_UPDATE"], text_color="black", hover_color="#ffb74d",
                                        width=280, height=45, font=("Arial", 15, "bold"),
                                        command=lambda: self.open_manage_window(show_only_mine=True))
        self.btn_manage.pack(pady=8)
        
        self.btn_cats = ctk.CTkButton(self.btn_frame, text="⚙️ Manage Categories", 
                                        fg_color=THEME["CARD_BG"], text_color="white", hover_color=THEME["BORDER"],
                                        width=280, height=45, font=("Arial", 15, "bold"),
                                        command=self.open_create_category_form)
        self.btn_cats.pack(pady=8)

        self.btn_recycle = ctk.CTkButton(self.btn_frame, text="♻️ Recycle Bin", 
                                        fg_color="#37474f", text_color="white", hover_color="#455a64",
                                        width=280, height=45, font=("Arial", 15, "bold"),
                                        command=self.open_recycle_bin_window)
        self.btn_recycle.pack(pady=8)

        ctk.CTkFrame(self, height=2, fg_color=THEME["BORDER"]).pack(fill="x", padx=50, pady=20)

        self.btn_logout = ctk.CTkButton(self, text="Log Out", 
                                      fg_color=THEME["BTN_LOGOUT"], hover_color="#ab47bc",
                                      width=280, height=40, font=("Arial", 14, "bold"),
                                      command=self.perform_logout)
        self.btn_logout.pack(pady=5)

        self.btn_exit = ctk.CTkButton(self, text="Exit Program", 
                                      fg_color=THEME["BTN_EXIT"], hover_color="#78909c",
                                      width=280, height=40, font=("Arial", 14, "bold"),
                                      command=self.quit_program)
        self.btn_exit.pack(pady=5)

        self.protocol("WM_DELETE_WINDOW", self.quit_program)

    def save_bin(self):
        try:
            with open(BIN_FILE, 'w') as f:
                json.dump(self.recycle_bin, f)
        except Exception as e:
            print(f"Error saving bin: {e}")

    def load_bin(self):
        if os.path.exists(BIN_FILE):
            try:
                with open(BIN_FILE, 'r') as f:
                    self.recycle_bin = json.load(f)
            except:
                self.recycle_bin = []

    def perform_logout(self):
        """Closes dashboard, clears session AND DELETES recycle bin data"""
        self.recycle_bin.clear() 
        if os.path.exists(BIN_FILE):
            os.remove(BIN_FILE) 
        
        clear_session() 
        self.destroy()
        self.login_instance.deiconify() 
        self.login_instance.clear_inputs() 

    def quit_program(self):
        tkmb.showinfo("Goodbye", "Goodbye! Come again soon. 👋", parent=self)
        self.master.destroy() 
        sys.exit()


    def open_recycle_bin_window(self):
        win = ctk.CTkToplevel(self)
        win.title("Recycle Bin")
        center_window(win, 600, 500)
        win.configure(fg_color=THEME["BG"])
        win.attributes("-topmost", True)
        win.lift()
        win.focus_force()
        win.grab_set()

        ctk.CTkLabel(win, text=f"Recycle Bin ({len(self.recycle_bin)} Items)", font=("Arial", 20, "bold"), text_color=THEME["FG"]).pack(pady=10)
        ctk.CTkLabel(win, text="Items persist until you Log Out.", font=("Arial", 12), text_color="gray").pack(pady=(0, 10))

        scroll = ctk.CTkScrollableFrame(win, width=560, height=350, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=5)

        def refresh_bin_view():
            for widget in scroll.winfo_children():
                widget.destroy()
            
            ctk.CTkLabel(win, text=f"Recycle Bin ({len(self.recycle_bin)} Items)", font=("Arial", 20, "bold"), text_color=THEME["FG"]).pack_forget() 

            if not self.recycle_bin:
                ctk.CTkLabel(scroll, text="Bin is empty.", text_color="gray").pack(pady=20)
                return

            for index, item in enumerate(reversed(self.recycle_bin)):
                original_index = len(self.recycle_bin) - 1 - index
                title, content, auth_id, cat_id, cat_name = item
                
                card = ctk.CTkFrame(scroll, border_color="#546e7a", border_width=1, fg_color=THEME["CARD_BG"])
                card.pack(fill="x", pady=5, padx=5)
                
                info_frame = ctk.CTkFrame(card, fg_color="transparent")
                info_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
                
                ctk.CTkLabel(info_frame, text=f"📂 {cat_name}", text_color="gray", font=("Arial", 10, "bold")).pack(anchor="w")
                ctk.CTkLabel(info_frame, text=title, font=("Arial", 14, "bold"), text_color="white").pack(anchor="w")

                action_frame = ctk.CTkFrame(card, fg_color="transparent")
                action_frame.pack(side="right", padx=10)

                ctk.CTkButton(action_frame, text="Restore", width=60, height=24,
                             fg_color=THEME["BTN_CREATE"], text_color="black",
                             command=lambda idx=original_index: restore_item(idx)).pack(side="right", padx=2)
                
                ctk.CTkButton(action_frame, text="❌", width=30, height=24,
                             fg_color=THEME["BTN_DELETE"],
                             command=lambda idx=original_index: delete_forever(idx)).pack(side="right", padx=2)

        def restore_item(index):
            try:
                item = self.recycle_bin[index]
                sql = "INSERT INTO Articles (title, content, author_id, category_id, is_published) VALUES (%s, %s, %s, %s, TRUE)"
                db_execute(sql, (item[0], item[1], item[2], item[3]), parent=win)
                
                self.recycle_bin.pop(index)
                self.save_bin() 
                refresh_bin_view()
                tkmb.showinfo("Restored", "Article restored successfully!", parent=win)
            except Exception as e:
                tkmb.showerror("Error", f"Could not restore: {e}", parent=win)

        def delete_forever(index):
            if tkmb.askyesno("Delete Forever", "Remove this item permanently?", parent=win):
                self.recycle_bin.pop(index)
                self.save_bin() 
                refresh_bin_view()

        refresh_bin_view()
        ctk.CTkButton(win, text="Exit", fg_color=THEME["BTN_EXIT"], command=win.destroy).pack(pady=10)

    def open_create_category_form(self):
        form = ctk.CTkToplevel(self)
        form.title("New Category")
        center_window(form, 400, 250)
        form.configure(fg_color=THEME["BG"])
        form.attributes("-topmost", True)
        form.lift()
        form.focus_force()
        form.grab_set() 

        ctk.CTkLabel(form, text="📂 New Category", font=("Arial", 18, "bold"), text_color=THEME["FG"]).pack(pady=10)
        entry_cat = ctk.CTkEntry(form, placeholder_text="Category Name", width=250, fg_color=THEME["CARD_BG"], border_color=THEME["BORDER"], text_color="white")
        entry_cat.pack(pady=20)

        def save_cat():
            cat = entry_cat.get()
            if cat:
                db_execute("INSERT INTO Categories (category_name) VALUES (%s)", (cat,), parent=form)
                tkmb.showinfo("Success", f"Category '{cat}' added!", parent=form)
                form.destroy()
            else:
                tkmb.showwarning("Missing Data", "Category Name is required.", parent=form)

        ctk.CTkButton(form, text="Save Category", fg_color=THEME["BTN_CREATE"], text_color="black", hover_color=THEME["HOVER_GENERIC"], command=save_cat).pack(pady=10)
        ctk.CTkButton(form, text="Close", fg_color=THEME["BTN_EXIT"], hover_color=THEME["HOVER_GENERIC"], command=form.destroy).pack(pady=5)

    def open_create_article_form(self):
        cats_raw = db_execute("SELECT category_id, category_name FROM Categories", fetch=True, parent=self)
        if not cats_raw:
            tkmb.showwarning("Requirement", "No Categories found. Please create a Category first.", parent=self)
            return
        cat_map = {name: cid for cid, name in cats_raw}

        form = ctk.CTkToplevel(self)
        form.title("New Article")
        center_window(form, 450, 500)
        form.configure(fg_color=THEME["BG"])
        form.attributes("-topmost", True)
        form.lift()
        form.focus_force()
        form.grab_set()

        ctk.CTkLabel(form, text="📝 New Article", font=("Arial", 18, "bold"), text_color=THEME["FG"]).pack(pady=10)

        ctk.CTkLabel(form, text=f"Posting as: {self.author_name}", font=("Arial", 14, "bold"), text_color=THEME["BTN_CREATE"]).pack(pady=5)

        entry_title = ctk.CTkEntry(form, placeholder_text="Article Title", width=300, fg_color=THEME["CARD_BG"], border_color=THEME["BORDER"], text_color="white")
        entry_title.pack(pady=10)

        ctk.CTkLabel(form, text="Select Category:", text_color="gray").pack(pady=(5,0))
        combo_cat = ctk.CTkOptionMenu(form, values=list(cat_map.keys()), width=300, fg_color=THEME["BTN_READ"], button_color=THEME["BTN_READ"])
        combo_cat.pack(pady=5)

        ctk.CTkLabel(form, text="Content:", text_color="gray").pack(pady=(5,0))
        entry_content = ctk.CTkTextbox(form, width=300, height=120, fg_color=THEME["CARD_BG"], border_color=THEME["BORDER"], text_color="white")
        entry_content.pack(pady=5)

        def save_article():
            title = entry_title.get()
            content = entry_content.get("1.0", END).strip()
            sel_cat_name = combo_cat.get()
            cat_id = cat_map.get(sel_cat_name)

            if title and content and cat_id:
                sql = "INSERT INTO Articles (title, content, author_id, category_id, is_published) VALUES (%s, %s, %s, %s, TRUE)"
                db_execute(sql, (title, content, self.author_id, cat_id), parent=form)
                tkmb.showinfo("Success", "Article Published!", parent=form)
                form.destroy()
            else:
                tkmb.showwarning("Error", "All fields are required.", parent=form)

        def clear_form():
            entry_title.delete(0, END)
            entry_content.delete("1.0", END)
            combo_cat.set(list(cat_map.keys())[0])

        ctk.CTkButton(form, text="Publish Article", fg_color=THEME["BTN_CREATE"], text_color="black", hover_color=THEME["HOVER_GENERIC"], command=save_article).pack(pady=10)
        ctk.CTkButton(form, text="Clear", fg_color=THEME["BTN_EXIT"], hover_color=THEME["HOVER_GENERIC"], width=100, command=clear_form).pack(pady=5)
        ctk.CTkButton(form, text="Close", fg_color=THEME["BTN_EXIT"], hover_color=THEME["HOVER_GENERIC"], width=100, command=form.destroy).pack(pady=5)

    def open_full_article_window(self, article_id):
        sql = """
            SELECT A.title, A.content, A.publication_date, T1.name, T2.category_name 
            FROM Articles A 
            JOIN Authors T1 ON A.author_id = T1.author_id 
            JOIN Categories T2 ON A.category_id = T2.category_id 
            WHERE A.article_id = %s
        """
        data = db_execute(sql, (article_id,), fetch=True, parent=self)
        if not data:
            tkmb.showerror("Error", "Could not fetch article data.", parent=self)
            return

        title, content, date, author, category = data[0]
        date_str = str(date)
        if hasattr(date, 'strftime'):
            date_str = date.strftime('%Y-%m-%d %H:%M')

        read_win = ctk.CTkToplevel(self)
        read_win.title(f"Reading: {title}")
        center_window(read_win, 500, 600)
        read_win.configure(fg_color=THEME["BG"])
        read_win.attributes("-topmost", True)
        read_win.lift()
        read_win.focus_force()
        read_win.grab_set()

        header_frame = ctk.CTkFrame(read_win, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(header_frame, text=f"📂 {category}", text_color=THEME["BTN_READ"]).pack(anchor="w")
        ctk.CTkLabel(header_frame, text=title, font=("Arial", 22, "bold"), text_color=THEME["FG"], wraplength=460).pack(anchor="w", pady=(5,5))
        ctk.CTkLabel(header_frame, text=f"By {author}  |  {date_str}", text_color="gray").pack(anchor="w")

        text_area = ctk.CTkTextbox(read_win, wrap="word", width=460, height=400, fg_color=THEME["CARD_BG"], text_color="white", border_color=THEME["BORDER"])
        text_area.pack(padx=20, pady=10, fill="both", expand=True)
        text_area.insert("0.0", content)
        text_area.configure(state="disabled")

        ctk.CTkButton(read_win, text="Close", fg_color=THEME["BTN_EXIT"], hover_color=THEME["HOVER_GENERIC"], command=read_win.destroy).pack(pady=20)

    def open_manage_window(self, show_only_mine=False):
        view = ctk.CTkToplevel(self)
        title_text = "My Articles" if show_only_mine else "All Articles"
        view.title(title_text)
        center_window(view, 750, 600)
        view.configure(fg_color=THEME["BG"])
        view.attributes("-topmost", True)
        view.lift()
        view.focus_force()
        view.grab_set()

        cat_data = db_execute("SELECT category_name FROM Categories ORDER BY category_name", fetch=True, parent=view)
        cat_options = ["All"]
        if cat_data:
            cat_options.extend([r[0] for r in cat_data])

        filter_frame = ctk.CTkFrame(view, fg_color="transparent")
        filter_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(filter_frame, text="Filter by Category:", text_color="gray").pack(side="left", padx=5)

        combo_cat_search = ctk.CTkComboBox(filter_frame, values=cat_options, width=200,
                                           fg_color=THEME["CARD_BG"], border_color=THEME["BORDER"], text_color="white",
                                           button_color=THEME["BTN_READ"], button_hover_color=THEME["HOVER_GENERIC"])
        combo_cat_search.pack(side="left", padx=(0, 10))
        combo_cat_search.set("All")
        
        scroll = ctk.CTkScrollableFrame(view, width=730, height=450, fg_color="transparent")
        scroll.pack(side="top", fill="both", expand=True, padx=10, pady=(0, 10))

        def delete_card(aid, title):
            if tkmb.askyesno("Confirm Delete", f"Move to Recycle Bin?\n\n'{title}'", parent=view):
                sql_backup = """
                    SELECT title, content, author_id, category_id, 
                    (SELECT category_name FROM Categories WHERE category_id = Articles.category_id)
                    FROM Articles WHERE article_id = %s
                """
                data = db_execute(sql_backup, (aid,), fetch=True, parent=view)
                if data:
                    self.recycle_bin.append(data[0])
                    self.save_bin()
                    db_execute("DELETE FROM Articles WHERE article_id=%s", (aid,), parent=view)
                    refresh_data()
                    tkmb.showinfo("Moved to Bin", "Article moved to Recycle Bin.", parent=view)

        def update_card(aid):
            self.open_direct_update_form(aid, on_close_callback=refresh_data)

        def refresh_data(category_name=None):
            if category_name is None:
                category_name = combo_cat_search.get()

            for widget in scroll.winfo_children():
                widget.destroy()

            sql_base = """
                SELECT A.article_id, A.title, A.publication_date, T1.name, T2.category_name, A.author_id
                FROM Articles A
                INNER JOIN Authors T1 ON A.author_id = T1.author_id
                INNER JOIN Categories T2 ON A.category_id = T2.category_id
            """
            conditions = ["A.is_published = TRUE"]
            params = []

            if show_only_mine:
                conditions.append("A.author_id = %s")
                params.append(self.author_id)

            if category_name and category_name != "All":
                conditions.append("T2.category_name = %s")
                params.append(category_name)

            sql = sql_base + " WHERE " + " AND ".join(conditions) + " ORDER BY A.publication_date DESC"

            try:
                rows = db_execute(sql, tuple(params), fetch=True, parent=view)
            except Exception as e:
                tkmb.showerror("Query Error", f"Error fetching data:\n{e}", parent=view)
                return

            ctk.CTkLabel(scroll, text=f"--- Results: {len(rows)} ---", font=("Arial", 14, "bold"), text_color="gray").pack(pady=10)

            if not rows:
                ctk.CTkLabel(scroll, text="No articles found.", text_color="gray").pack(pady=20)
                return

            for row in rows:
                aid, title, date_obj, author, category, auth_id = row
                date_str = str(date_obj)
                if hasattr(date_obj, 'strftime'): date_str = date_obj.strftime('%Y-%m-%d %H:%M')
                
                is_mine = (auth_id == self.author_id)
                border_col = THEME["BTN_CREATE"] if is_mine else THEME["BORDER"]

                card = ctk.CTkFrame(scroll, border_color=border_col, border_width=1, fg_color=THEME["CARD_BG"])
                card.pack(fill="x", pady=5, padx=5)
                
                info_frame = ctk.CTkFrame(card, fg_color="transparent")
                info_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

                header_text = f"📂 {category}  |  📅 {date_str}"
                if is_mine: header_text += "  (YOU)"
                
                ctk.CTkLabel(info_frame, text=header_text, text_color=THEME["BTN_READ"], font=("Arial", 11, "bold")).pack(anchor="w")
                ctk.CTkLabel(info_frame, text=title, font=("Arial", 16, "bold"), text_color="white").pack(anchor="w")
                ctk.CTkLabel(info_frame, text=f"✍️ {author}", text_color="silver", font=("Arial", 11)).pack(anchor="w")

                action_frame = ctk.CTkFrame(card, fg_color="transparent")
                action_frame.pack(side="right", padx=10, pady=5)

                ctk.CTkButton(action_frame, text="📖 Read", width=70, height=24,
                             fg_color=THEME["BTN_EXIT"], hover_color=THEME["HOVER_GENERIC"],
                             command=lambda i=aid: self.open_full_article_window(i)).pack(side="right", padx=2)

                if is_mine:
                    ctk.CTkButton(action_frame, text="🗑️", width=35, height=24,
                                 fg_color=THEME["BTN_DELETE"], hover_color="#ff8a80",
                                 command=lambda i=aid, t=title: delete_card(i, t)).pack(side="right", padx=2)
                    
                    ctk.CTkButton(action_frame, text="✏️", width=35, height=24,
                                 fg_color=THEME["BTN_UPDATE"], text_color="black", hover_color="#ffe082",
                                 command=lambda i=aid: update_card(i)).pack(side="right", padx=2)

        btn_search = ctk.CTkButton(filter_frame, text="🔍 Filter", width=80, 
                                   fg_color=THEME["BTN_READ"], hover_color=THEME["HOVER_GENERIC"],
                                   command=lambda: refresh_data())
        btn_search.pack(side="left", padx=5)

        btn_all = ctk.CTkButton(filter_frame, text="Show All", width=80, fg_color=THEME["BTN_EXIT"], hover_color=THEME["HOVER_GENERIC"],
                                command=lambda: [combo_cat_search.set("All"), refresh_data()])
        btn_all.pack(side="left", padx=5)

        ctk.CTkButton(view, text="Exit", fg_color=THEME["BTN_EXIT"], hover_color=THEME["HOVER_GENERIC"], command=view.destroy).pack(side="bottom", pady=10)
        refresh_data()

    def open_direct_update_form(self, art_id, on_close_callback=None):
        data = db_execute("SELECT title, content FROM Articles WHERE article_id=%s", (art_id,), fetch=True, parent=self)
        if not data: return
        old_title, old_content = data[0]
        
        form = ctk.CTkToplevel(self)
        form.title(f"Edit Article")
        center_window(form, 450, 550)
        form.configure(fg_color=THEME["BG"])
        form.attributes("-topmost", True)
        form.lift()
        form.focus_force()
        form.grab_set()
        
        ctk.CTkLabel(form, text="Edit Article", font=("Arial", 18, "bold"), text_color=THEME["FG"]).pack(pady=10)

        ctk.CTkLabel(form, text="Title:", text_color="gray").pack(pady=(5, 0))
        entry_title = ctk.CTkEntry(form, width=300, fg_color=THEME["CARD_BG"], border_color=THEME["BORDER"], text_color="white")
        entry_title.pack(pady=5)
        entry_title.insert(0, old_title)
        
        ctk.CTkLabel(form, text="Content:", text_color="gray").pack(pady=(5, 0))
        entry_content = ctk.CTkTextbox(form, width=300, height=200, fg_color=THEME["CARD_BG"], border_color=THEME["BORDER"], text_color="white")
        entry_content.pack(pady=5)
        entry_content.insert("0.0", old_content)

        def update():
            t = entry_title.get()
            b = entry_content.get("1.0", END).strip()
            db_execute("UPDATE Articles SET title=%s, content=%s WHERE article_id=%s", (t, b, art_id), parent=form)
            tkmb.showinfo("Success", "Article updated.", parent=form)
            form.destroy()
            if on_close_callback: on_close_callback()

        ctk.CTkButton(form, text="Save Changes", fg_color=THEME["BTN_UPDATE"], text_color="black", hover_color=THEME["HOVER_GENERIC"], command=update).pack(pady=10)
        ctk.CTkButton(form, text="Cancel", fg_color=THEME["BTN_EXIT"], hover_color=THEME["HOVER_GENERIC"], command=form.destroy).pack(pady=5)

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Author Access Portal")
        center_window(self, 380, 450)
        self.resizable(False, False)
        self.configure(fg_color=THEME["BG"])
        self.lift()
        self.focus_force()
        
        self.login_frame = ctk.CTkFrame(self, fg_color=THEME["BG"])
        self.login_frame.pack(pady=20, padx=40, fill="both", expand=True)

        ctk.CTkLabel(self.login_frame, text="✍️ AUTHOR LOGIN", font=ctk.CTkFont(size=24, weight="bold"), text_color=THEME["FG"]).pack(pady=(10, 20))

        self.username_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Author Name", width=250, height=35, fg_color=THEME["CARD_BG"], border_color=THEME["BORDER"], text_color="white")
        self.username_entry.pack(pady=10)
        
        self.password_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Password", show="*", width=250, height=35, fg_color=THEME["CARD_BG"], border_color=THEME["BORDER"], text_color="white")
        self.password_entry.pack(pady=10)
        
        session = load_session()
        if session:
            data = db_execute("SELECT author_id, name FROM Authors WHERE author_id=%s", (session['id'],), fetch=True, parent=self)
            if data:
                self.withdraw()
                dash = DashboardWindow(author_data=data[0], login_instance=self) 
                dash.protocol("WM_DELETE_WINDOW", dash.quit_program) 
            else:
                clear_session() 

        ctk.CTkButton(self.login_frame, text="Log In", command=self.attempt_login, width=250, height=40, 
                      fg_color=THEME["BTN_CREATE"], text_color="black", hover_color=THEME["HOVER_GENERIC"]).pack(pady=10)
        
        ctk.CTkButton(self.login_frame, text="Register New Author", command=self.open_register, width=250, height=35,
                      fg_color=THEME["BTN_READ"], hover_color=THEME["HOVER_GENERIC"]).pack(pady=5)

        ctk.CTkButton(self.login_frame, text="Exit", command=self.close_app, width=250, height=35,
                      fg_color=THEME["BTN_EXIT"], hover_color=THEME["HOVER_GENERIC"]).pack(pady=5)
        
        self.status_label = ctk.CTkLabel(self.login_frame, text="", text_color=THEME["BTN_DELETE"])
        self.status_label.pack(pady=5)

    def clear_inputs(self):
        self.username_entry.delete(0, END)
        self.password_entry.delete(0, END)
        self.status_label.configure(text="")

    def attempt_login(self):
        u = self.username_entry.get().strip()
        p = self.password_entry.get().strip() 

        data = db_execute("SELECT author_id, name FROM Authors WHERE name=%s AND email=%s", (u, p), fetch=True, parent=self)
        
        if data:
            save_session(data[0][0], data[0][1]) 
            self.withdraw()
            dash = DashboardWindow(author_data=data[0], login_instance=self) 
            dash.protocol("WM_DELETE_WINDOW", dash.quit_program) 
            dash.mainloop()
        else:
            self.status_label.configure(text="Invalid Name or Email.")

    def open_register(self):
        reg = ctk.CTkToplevel(self)
        reg.title("Register Author")
        center_window(reg, 400, 350)
        reg.configure(fg_color=THEME["BG"])
        reg.attributes("-topmost", True)
        reg.lift()
        reg.focus_force()
        reg.grab_set()

        ctk.CTkLabel(reg, text="👤 New Author", font=("Arial", 18, "bold"), text_color=THEME["FG"]).pack(pady=10)

        r_name = ctk.CTkEntry(reg, placeholder_text="Name", width=250, fg_color=THEME["CARD_BG"], border_color=THEME["BORDER"], text_color="white")
        r_name.pack(pady=10)
        
        r_email = ctk.CTkEntry(reg, placeholder_text="Email", width=250, fg_color=THEME["CARD_BG"], border_color=THEME["BORDER"], text_color="white")
        r_email.pack(pady=10)
        
        r_bio = ctk.CTkEntry(reg, placeholder_text="Bio (Optional)", width=250, fg_color=THEME["CARD_BG"], border_color=THEME["BORDER"], text_color="white")
        r_bio.pack(pady=10)

        def save():
            n = r_name.get()
            e = r_email.get()
            b = r_bio.get()
            if n and e:
                db_execute("INSERT INTO Authors (name, email, bio) VALUES (%s, %s, %s)", (n, e, b), parent=reg)
                tkmb.showinfo("Success", "Registered!", parent=reg)
                if tkmb.askyesno("Login Now?", f"Do you want to log in as '{n}' now?", parent=reg):
                    # Auto Login Logic
                    self.username_entry.delete(0, END)
                    self.username_entry.insert(0, n)
                    self.password_entry.delete(0, END)
                    self.password_entry.insert(0, e)
                    reg.destroy()
                    self.attempt_login()
                else:
                    reg.destroy()
            else:
                tkmb.showwarning("Error", "Name and Email required.", parent=reg)

        ctk.CTkButton(reg, text="Sign Up", fg_color=THEME["BTN_CREATE"], text_color="black", hover_color=THEME["HOVER_GENERIC"], command=save).pack(pady=15)

    def close_app(self):
        tkmb.showinfo("Goodbye", "Goodbye! Come again soon. 👋", parent=self)
        self.destroy()
        sys.exit()

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    app = LoginWindow()
    app.mainloop()
