import tkinter as tk
from tkinter import ttk, messagebox
from db.db_connection import get_connection
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

class Dashboard:
    def __init__(self, root, user_id):
        self.root = root
        self.user_id = user_id
        self.root.title("Expense Tracker - Dashboard")
        self.root.geometry("1000x750")

        # ----- UI Elements -----
        tk.Label(root, text="Expense Tracker Dashboard", font=("Arial", 16, "bold")).pack(pady=10)

        # Expense Table (top)
        table_frame = tk.Frame(root)
        table_frame.pack(fill="x", padx=10)

        self.tree = ttk.Treeview(table_frame, columns=("id", "category", "amount", "date", "description"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col.title())
            self.tree.column(col, width=120, anchor="center")
        self.tree.pack(side="left", fill="x", expand=True)

        table_hscroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=table_hscroll.set)
        table_hscroll.pack(side="bottom", fill="x")

        # Filters and Controls
        filter_frame = tk.Frame(root)
        filter_frame.pack(pady=8)

        tk.Label(filter_frame, text="From (YYYY-MM-DD):").grid(row=0, column=0, padx=5)
        self.from_entry = tk.Entry(filter_frame, width=15)
        self.from_entry.grid(row=0, column=1)

        tk.Label(filter_frame, text="To (YYYY-MM-DD):").grid(row=0, column=2, padx=5)
        self.to_entry = tk.Entry(filter_frame, width=15)
        self.to_entry.grid(row=0, column=3)

        tk.Button(filter_frame, text="Apply Filter", bg="orange", command=self.apply_filter).grid(row=0, column=4, padx=6)
        tk.Button(filter_frame, text="Clear Filter", bg="lightgray", command=self.load_expenses).grid(row=0, column=5, padx=6)
        tk.Button(filter_frame, text="Refresh Dashboard", bg="#4CAF50", fg="white", command=self.load_expenses).grid(row=0, column=6, padx=6)

        # Add Expense Section
        add_frame = tk.Frame(root)
        add_frame.pack(pady=5, fill="x")

        tk.Label(add_frame, text="Category:").grid(row=0, column=0, padx=5)
        self.category_cb = ttk.Combobox(add_frame, values=[], width=18)
        self.category_cb.grid(row=0, column=1)

        tk.Label(add_frame, text="Amount:").grid(row=0, column=2, padx=5)
        self.amount_entry = tk.Entry(add_frame, width=12)
        self.amount_entry.grid(row=0, column=3)

        tk.Label(add_frame, text="Date (YYYY-MM-DD):").grid(row=0, column=4, padx=5)
        self.date_entry = tk.Entry(add_frame, width=14)
        self.date_entry.grid(row=0, column=5)

        tk.Label(add_frame, text="Description:").grid(row=0, column=6, padx=5)
        self.desc_entry = tk.Entry(add_frame, width=25)
        self.desc_entry.grid(row=0, column=7)

        tk.Button(add_frame, text="Add Expense", bg="#2196F3", fg="white", command=self.add_expense).grid(row=0, column=8, padx=6)
        tk.Button(add_frame, text="Delete Selected", bg="red", fg="white", command=self.delete_selected).grid(row=0, column=9, padx=6)
        tk.Button(add_frame, text="Manage Categories", bg="brown", fg="white", command=self.manage_categories).grid(row=0, column=10, padx=6)

        # Summary Label (total)
        self.summary_label = tk.Label(root, text="", font=("Arial", 10))
        self.summary_label.pack(pady=6)

        # ----------------------- Scrollable Frame -----------------------
        container = tk.Frame(root)
        container.pack(fill="both", expand=True, padx=10, pady=5)

        self.canvas = tk.Canvas(container)
        vscroll = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vscroll.set)

        vscroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.scrollable_frame.columnconfigure(0, weight=1)

        # Chart frames
        self.bar_frame = tk.Frame(self.scrollable_frame)
        self.bar_frame.grid(row=0, column=0, pady=10, sticky="n")
        self.pie_frame = tk.Frame(self.scrollable_frame)
        self.pie_frame.grid(row=1, column=0, pady=10, sticky="n")
        self.summary_table_frame = tk.Frame(self.scrollable_frame)
        self.summary_table_frame.grid(row=2, column=0, pady=10, sticky="n")

        self.load_categories()
        self.load_expenses()
        self._bind_mousewheel()

    # ----------------------- Utilities -----------------------
    def _bind_mousewheel(self):
        def _on_mousewheel(event):
            if event.delta:
                self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            elif event.num == 4:
                self.canvas.yview_scroll(-3, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(3, "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        self.canvas.bind_all("<Button-4>", _on_mousewheel)
        self.canvas.bind_all("<Button-5>", _on_mousewheel)

    # ----------------------- CATEGORY MANAGEMENT -----------------------
    def manage_categories(self):
        win = tk.Toplevel(self.root)
        win.title("Manage Categories")
        win.geometry("350x400")
        container = tk.Frame(win)
        container.pack(fill="both", expand=True)
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas)
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Label(scrollable, text="Existing Categories:", font=("Arial", 10, "bold")).pack(pady=5)
        listbox = tk.Listbox(scrollable, selectmode="extended", height=10)
        listbox.pack(fill="both", expand=True, padx=10)
        for cat in self.category_cb["values"]:
            listbox.insert("end", cat)

        tk.Label(scrollable, text="New Category:").pack(pady=5)
        new_cat = tk.Entry(scrollable)
        new_cat.pack()

        def add_cat():
            name = new_cat.get().strip()
            if not name:
                messagebox.showerror("Error", "Category name cannot be empty")
                return
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO category (category_name) VALUES (%s)", (name,))
            conn.commit()
            conn.close()
            self.load_categories()
            messagebox.showinfo("Success", f"Category '{name}' added successfully")
            win.destroy()

        def delete_cat():
            selected = listbox.curselection()
            if not selected:
                messagebox.showwarning("No selection", "Select at least one category to delete")
                return
            cats_to_delete = [listbox.get(i) for i in selected]
            confirm = messagebox.askyesno("Confirm Delete", f"Delete selected categories?\n\n{', '.join(cats_to_delete)}")
            if not confirm:
                return
            conn = get_connection()
            cursor = conn.cursor()
            for cat in cats_to_delete:
                cursor.execute("SELECT COUNT(*) FROM expense e JOIN category c ON e.category_id=c.category_id WHERE c.category_name=%s",(cat,))
                if cursor.fetchone()[0] > 0:
                    messagebox.showwarning("Blocked", f"Cannot delete '{cat}' — linked expenses exist.")
                    continue
                cursor.execute("DELETE FROM category WHERE category_name=%s", (cat,))
            conn.commit()
            conn.close()
            self.load_categories()
            messagebox.showinfo("Deleted", "Selected category(ies) deleted successfully")
            win.destroy()

        tk.Button(scrollable, text="Add Category", bg="#2196F3", fg="white", command=add_cat).pack(pady=5)
        tk.Button(scrollable, text="Delete Selected", bg="red", fg="white", command=delete_cat).pack(pady=5)

    # ----------------------- DATE FILTER -----------------------
    def apply_filter(self):
        from_date = self.from_entry.get().strip()
        to_date = self.to_entry.get().strip()
        if not from_date or not to_date:
            messagebox.showerror("Error", "Both From and To dates are required.")
            return
        try:
            from_dt = datetime.strptime(from_date, "%Y-%m-%d")
            to_dt = datetime.strptime(to_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
            return
        if from_dt > to_dt:
            messagebox.showerror("Error", "From date cannot be later than To date.")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.expense_id, c.category_name, e.amount, e.date, e.description
            FROM expense e
            JOIN category c ON e.category_id = c.category_id
            WHERE e.user_id=%s AND e.date BETWEEN %s AND %s
            ORDER BY e.date DESC
        """, (self.user_id, from_date, to_date))
        rows = cursor.fetchall()
        conn.close()
        self.tree.delete(*self.tree.get_children())
        for r in rows:
            self.tree.insert("", "end", values=r)
        self.update_summary_and_charts(rows)

    # ----------------------- CRUD -----------------------
    def add_expense(self):
        cat = self.category_cb.get().strip()
        amt = self.amount_entry.get().strip()
        date = self.date_entry.get().strip()
        desc = self.desc_entry.get().strip()
        if not cat or not amt or not date:
            messagebox.showerror("Error", "Category, Amount, and Date are required")
            return
        try:
            float(amt)
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid amount or date format")
            return
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT category_id FROM category WHERE category_name=%s", (cat,))
        cat_id = cursor.fetchone()
        if not cat_id:
            messagebox.showerror("Error", "Invalid category")
            conn.close()
            return
        cursor.execute("INSERT INTO expense (user_id, category_id, amount, date, description) VALUES (%s, %s, %s, %s, %s)",
                       (self.user_id, cat_id[0], amt, date, desc))
        conn.commit()
        conn.close()
        self.load_expenses()
        messagebox.showinfo("Success", "Expense added successfully")

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select at least one record to delete")
            return
        confirm = messagebox.askyesno("Confirm Delete", "Delete selected expense(s)?")
        if not confirm:
            return
        conn = get_connection()
        cursor = conn.cursor()
        for sel in selected:
            cursor.execute("DELETE FROM expense WHERE expense_id=%s", (self.tree.item(sel)["values"][0],))
        conn.commit()
        conn.close()
        self.load_expenses()
        messagebox.showinfo("Deleted", "Selected expense(s) deleted")

    # ----------------------- LOADERS -----------------------
    def load_categories(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT category_name FROM category")
        cats = [row[0] for row in cursor.fetchall()]
        conn.close()
        self.category_cb["values"] = cats

    def load_expenses(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.expense_id, c.category_name, e.amount, e.date, e.description
            FROM expense e
            JOIN category c ON e.category_id = c.category_id
            WHERE e.user_id=%s
            ORDER BY e.date DESC
        """, (self.user_id,))
        rows = cursor.fetchall()
        conn.close()
        self.tree.delete(*self.tree.get_children())
        for r in rows:
            self.tree.insert("", "end", values=r)
        self.update_summary_and_charts(rows)

    # ----------------------- SUMMARY & CHART -----------------------
    def update_summary_and_charts(self, rows):
        total = sum([float(r[2]) for r in rows]) if rows else 0
        self.summary_label.config(text=f"Total Expenses: ₹{total:.2f}")

        # Clear previous
        for widget in self.bar_frame.winfo_children():
            widget.destroy()
        for widget in self.pie_frame.winfo_children():
            widget.destroy()
        for widget in self.summary_table_frame.winfo_children():
            widget.destroy()

        if not rows:
            tk.Label(self.bar_frame, text="No expenses to display", font=("Arial", 10)).pack()
            return

        # Per-category aggregation
        data = {}
        for r in rows:
            cat, amt = r[1], float(r[2])
            if cat not in data:
                data[cat] = []
            data[cat].append(amt)
        categories = list(data.keys())
        totals = [sum(data[c]) for c in categories]
        avgs = [sum(data[c])/len(data[c]) for c in categories]
        mins = [min(data[c]) for c in categories]
        maxs = [max(data[c]) for c in categories]

        # ----------- Bar Chart -----------
        fig_bar, ax_bar = plt.subplots(figsize=(6,4))
        ax_bar.bar(categories, totals, color=plt.cm.tab20.colors[:len(categories)])
        ax_bar.set_xlabel("Category")
        ax_bar.set_ylabel("Total Amount (₹)")
        ax_bar.set_title("Expenses by Category (Total)")
        fig_bar.tight_layout()
        canvas_bar = FigureCanvasTkAgg(fig_bar, master=self.bar_frame)
        canvas_bar.draw()
        canvas_bar.get_tk_widget().pack(anchor="center")

        # ----------- Pie Chart -----------
        explode = [0.05 if t==max(totals) else 0 for t in totals]
        fig_pie, ax_pie = plt.subplots(figsize=(6,4))
        colors = plt.cm.tab20.colors[:len(categories)]
        ax_pie.pie(
            totals,
            labels=[f"{c} ({t:.0f})" for c,t in zip(categories,totals)],
            autopct="%1.1f%%",
            startangle=140,
            explode=explode,
            shadow=True,
            colors=colors
        )
        ax_pie.axis("equal")
        ax_pie.set_title("Category Distribution (Percent & Absolute ₹)")
        ax_pie.legend(categories, title="Categories", bbox_to_anchor=(1.05,1))
        fig_pie.tight_layout()
        canvas_pie = FigureCanvasTkAgg(fig_pie, master=self.pie_frame)
        canvas_pie.draw()
        canvas_pie.get_tk_widget().pack(anchor="center")

        # ----------- Summary Table -----------
        tk.Label(self.summary_table_frame, text="Expense Summary by Category", font=("Arial", 12, "bold")).pack(pady=6)
        cols = ("category","total","average","min","max")
        summary_tree = ttk.Treeview(self.summary_table_frame, columns=cols, show="headings", height=8)
        for c in cols:
            summary_tree.heading(c, text=c.title())
            summary_tree.column(c, width=120, anchor="center")
        summary_tree.column("category", width=240, anchor="center")
        summary_tree.pack(pady=4)

        # Insert per-category data
        for i, cat in enumerate(categories):
            summary_tree.insert("", "end", values=(
                cat, f"{totals[i]:.2f}", f"{avgs[i]:.2f}", f"{mins[i]:.2f}", f"{maxs[i]:.2f}"
            ))

        # Overall row
        overall_total = sum(totals)
        overall_avg = sum(avgs)/len(avgs) if avgs else 0
        summary_tree.insert("", "end", values=("Overall", f"{overall_total:.2f}", f"{overall_avg:.2f}", "", ""))

        # Highlight max total
        for item in summary_tree.get_children():
            val = float(summary_tree.item(item)["values"][1])
            if val == max(totals):
                summary_tree.item(item, tags=("highlight",))
        summary_tree.tag_configure("highlight", background="#ffcccc")
