import mysql.connector
from mysql.connector import Error

def get_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",       # your MySQL username
            password="ADITI",  # your MySQL password
            database="expense_tracker"      # your DB name
        )
        return conn
    except Error as e:
        import tkinter.messagebox as messagebox
        messagebox.showerror("DB Connection Error", str(e))
        return None
