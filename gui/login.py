import tkinter as tk
from tkinter import messagebox
from db.db_connection import get_connection
from gui.dashboard import Dashboard

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker - Login")
        self.root.geometry("400x250")
        self.root.resizable(False, False)

        tk.Label(root, text="Login", font=("Arial", 16, "bold")).pack(pady=10)

        tk.Label(root, text="Username").pack(pady=5)
        self.username_entry = tk.Entry(root)
        self.username_entry.pack()

        tk.Label(root, text="Password").pack(pady=5)
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack()

        tk.Button(root, text="Login", command=self.login, bg="#2196F3", fg="white").pack(pady=15)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Enter both username and password")
            return

        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM Users WHERE username=%s AND password=%s", (username, password))
                result = cursor.fetchone()
                cursor.close()
                conn.close()

                if result:
                    self.root.destroy()
                    root_dash = tk.Tk()
                    Dashboard(root_dash, user_id=result[0])
                    root_dash.mainloop()
                else:
                    messagebox.showerror("Login Failed", "Invalid username or password")
            except Exception as e:
                messagebox.showerror("DB Error", str(e))
