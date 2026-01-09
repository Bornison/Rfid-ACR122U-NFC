import threading
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

import db
import rfid


DB_PATH = "cards.db"


class RFIDApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("RFID Manager - MTU Internship")
        root.geometry("900x560")

        db.init_db(DB_PATH)

        self.create_widgets()
        self.load_records()

    def create_widgets(self):
        frm_left = ttk.Frame(self.root)
        frm_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Search
        top_bar = ttk.Frame(frm_left)
        top_bar.pack(fill=tk.X)
        self.search_var = tk.StringVar()
        ttk.Entry(top_bar, textvariable=self.search_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(top_bar, text="Search", command=self.on_search).pack(side=tk.LEFT, padx=4)
        ttk.Button(top_bar, text="Refresh", command=self.load_records).pack(side=tk.LEFT)

        # Tree
        columns = ("id", "rfid_uid", "role", "name", "department", "program", "year")
        self.tree = ttk.Treeview(frm_left, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110 if col != "name" else 180)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=8)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Right pane - form
        frm_right = ttk.Frame(self.root)
        frm_right.pack(side=tk.RIGHT, fill=tk.Y, padx=8, pady=8)

        self.fields = {}
        labels = [
            ("rfid_uid", "RFID UID"), ("role", "Role (student/faculty)"), ("name", "Name"),
            ("department", "Department"), ("category", "Category"), ("program", "Program"), ("year", "Year")
        ]
        for key, label in labels:
            ttk.Label(frm_right, text=label).pack(anchor=tk.W, pady=(6, 0))
            ent = ttk.Entry(frm_right)
            ent.pack(fill=tk.X)
            self.fields[key] = ent

        ttk.Button(frm_right, text="Scan card (fill UID)", command=self.scan_card).pack(fill=tk.X, pady=6)
        ttk.Button(frm_right, text="Write Name to Card", command=self.write_to_card).pack(fill=tk.X)

        ttk.Separator(frm_right).pack(fill=tk.X, pady=8)
        ttk.Button(frm_right, text="Add New", command=self.add_new).pack(fill=tk.X, pady=4)
        ttk.Button(frm_right, text="Update Selected", command=self.update_selected).pack(fill=tk.X, pady=4)
        ttk.Button(frm_right, text="Delete Selected", command=self.delete_selected).pack(fill=tk.X, pady=4)

    def load_records(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        rows = db.list_persons(DB_PATH)
        for row in rows:
            self.tree.insert("", tk.END, values=(row["id"], row["rfid_uid"], row["role"], row["name"], row["department"], row["program"], row["year"]))

    def on_search(self):
        q = self.search_var.get().strip()
        if not q:
            self.load_records()
            return
        rows = db.search_persons(q, DB_PATH)
        for r in self.tree.get_children():
            self.tree.delete(r)
        for row in rows:
            self.tree.insert("", tk.END, values=(row["id"], row["rfid_uid"], row["role"], row["name"], row["department"], row["program"], row["year"]))

    def on_select(self, _ev):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        pid = int(vals[0])
        person = db.get_person(pid, DB_PATH)
        if not person:
            return
        for key in ("rfid_uid", "role", "name", "department", "category", "program", "year"):
            val = person.get(key) or ""
            self.fields[key].delete(0, tk.END)
            self.fields[key].insert(0, val)

    def scan_card(self):
        def job():
            self.set_busy(True)
            try:
                conn = rfid.wait_for_card(timeout=8)
                if not conn:
                    messagebox.showinfo("Scan", "No card detected (timeout)")
                    return
                uid, text = rfid.scan_card(conn)
                if uid:
                    self.fields["rfid_uid"].delete(0, tk.END)
                    self.fields["rfid_uid"].insert(0, uid)
                    messagebox.showinfo("Scan", f"UID: {uid}\nText: {text}")
                else:
                    messagebox.showwarning("Scan", "Failed to read card")
            finally:
                self.set_busy(False)

        threading.Thread(target=job, daemon=True).start()

    def write_to_card(self):
        uid = self.fields["rfid_uid"].get().strip()
        name = self.fields["name"].get().strip()
        if not uid or not name:
            messagebox.showwarning("Write", "RFID UID and Name are required to write to card")
            return

        def job():
            self.set_busy(True)
            try:
                try:
                    conn = rfid.get_reader_connection()
                    conn.connect()
                except Exception as e:
                    messagebox.showerror("Write", f"No reader available: {e}")
                    return
                ok = rfid.write_to_card_block(conn, name)
                if ok:
                    messagebox.showinfo("Write", "Name written to card (block 4)")
                else:
                    messagebox.showerror("Write", "Failed to write to card")
            finally:
                self.set_busy(False)

        threading.Thread(target=job, daemon=True).start()

    def add_new(self):
        data = {k: self.fields[k].get().strip() for k in self.fields}
        if not data.get("name"):
            messagebox.showwarning("Add", "Name is required")
            return
        try:
            db.add_person(data, DB_PATH)
            self.load_records()
            messagebox.showinfo("Add", "Record added")
        except Exception as e:
            messagebox.showerror("Add", f"Failed to add: {e}")

    def update_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Update", "Select a record first")
            return
        pid = int(self.tree.item(sel[0], "values")[0])
        data = {k: self.fields[k].get().strip() for k in self.fields}
        db.update_person(pid, data, DB_PATH)
        self.load_records()
        messagebox.showinfo("Update", "Updated")

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Delete", "Select a record first")
            return
        pid = int(self.tree.item(sel[0], "values")[0])
        if not messagebox.askyesno("Delete", "Delete selected record?"):
            return
        db.delete_person(pid, DB_PATH)
        self.load_records()

    def set_busy(self, busy: bool):
        self.root.config(cursor=("watch" if busy else ""))


def main():
    root = tk.Tk()
    app = RFIDApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
