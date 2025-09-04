#!/usr/bin/env python3

import pathlib
import sys
import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import oracledb as cx_Oracle
CLIENT_LIB_DIR = pathlib.Path(__file__).resolve().parent.parent / "instantclient_23_8"
cx_Oracle.init_oracle_client(lib_dir=str(CLIENT_LIB_DIR))

#---------------------------------------------------------------------------
#  credentials to access the db
# ---------------------------------------------------------------------------
DB_USER     = "b00089586"
DB_PASSWORD = "b00089586"
DB_HOST     = "coeoracle.aus.edu"         
DB_PORT     = 1521
DB_SERVICE  = "orcl"                


def make_dsn(host, port, service):
    return cx_Oracle.makedsn(host, port, service_name=service)



def coerce(value, ora_type):
    if value == "":
        return None
    t = ora_type.upper()
    if t.startswith("NUMBER"):
        try:
            return int(value) if "." not in value else float(value)
        except ValueError:
            raise ValueError("Enter a valid number.")
    if t.startswith(("DATE", "TIMESTAMP")):
        try:
            return datetime.datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Enter date as YYYY-MM-DD.")
    return value   # VARCHAR2 / CHAR / CLOB etc.


#---------------------------------------------------------------------------
#  main GUI 
#---------------------------------------------------------------------------
class oracleGUIapp(tk.Tk):
    def __init__(self, connection):
        super().__init__()
        self.title("Car Dealership Manager")
        self.geometry("720x480")

        self.conn = connection
        self.table_meta = []      # (col_name, data_type, nullable)
        self.entries = {}         # Entry widgets by column
        self.pk_cols = []         # primary-key column names
        self.selected_pk = None   # tuple of PK values for current row

        self.make_main_screen()

    # ---------------------------------------------------------------------------MAIN UI-----------------------------------------------------------------
    def make_main_screen(self):
        container = ttk.PanedWindow(self, orient="horizontal")
        container.pack(fill="both", expand=True)

        # left: table list
        left = ttk.Frame(container, padding=10)
        tables_tree = ttk.Treeview(left, show="tree", selectmode="browse", height=20)
        tables_tree.pack(fill="y", expand=True)
        tables_tree.bind("<<TreeviewSelect>>",
                         lambda e: self.load_table(tables_tree.item(tables_tree.selection())["text"]))
        self.populate_tables(tables_tree)
        container.add(left, weight=1)

        # right: dynamic frame (form + grid)
        self.right = ttk.Frame(container, padding=10)
        container.add(self.right, weight=3)

    def populate_tables(self, tree):
        cur = self.conn.cursor()
        cur.execute("SELECT table_name FROM user_tables ORDER BY table_name")
        for (tbl,) in cur:
            tree.insert("", "end", text=tbl)
            
    def load_table(self, table_name):
        for child in self.right.winfo_children():
            child.destroy()

        cur = self.conn.cursor()
        cur.execute("""
            SELECT column_name, data_type, nullable
            FROM   user_tab_columns
            WHERE  table_name = :tbl
            ORDER BY column_id
        """, tbl=table_name.upper())
        self.table_meta = cur.fetchall()

        cur.execute("""
            SELECT cols.column_name
            FROM   user_constraints cons
            JOIN   user_cons_columns cols
                   ON cons.constraint_name = cols.constraint_name
            WHERE  cons.table_name = :tbl
              AND  cons.constraint_type = 'P'
            ORDER BY cols.position
        """, tbl=table_name.upper())
        self.pk_cols = [r[0] for r in cur]

        frm = ttk.LabelFrame(self.right, text=f"Edit {table_name}")
        frm.pack(side="top", fill="x", padx=5, pady=5)

        self.entries.clear()
        for r, (col, dtype, nullable) in enumerate(self.table_meta):
            ttk.Label(frm, text=f"{col} ({dtype})").grid(row=r, column=0, sticky="e")
            ent = ttk.Entry(frm, width=22)
            ent.grid(row=r, column=1, sticky="w")
            self.entries[col] = ent
            if nullable == "N":
                ent.configure(background="#ffd9d9")

        btn_row = len(self.table_meta)
        bframe = ttk.Frame(frm)
        bframe.grid(row=btn_row, column=0, columnspan=2, pady=5)
        ttk.Button(bframe, text="Insert",
                   command=lambda t=table_name: self.insert_row(t)).pack(side="left", padx=4)
        ttk.Button(bframe, text="Save Update",
                   command=lambda t=table_name: self.update_row(t)).pack(side="left", padx=4)
        ttk.Button(bframe, text="Delete",
                   command=lambda t=table_name: self.delete_row(t)).pack(side="left", padx=4)
        ttk.Button(bframe, text="Clear", command=self.clear_form).pack(side="left", padx=4)

        # Data grid
        grid = ttk.Treeview(self.right, show="headings", selectmode="browse")
        grid["columns"] = [col for col, *_ in self.table_meta]
        grid.pack(side="bottom", fill="both", expand=True)
        self.grid = grid

        for col, *_ in self.table_meta:
            grid.heading(col, text=col)
            grid.column(col, width=100, anchor="center")

        grid.bind("<<TreeviewSelect>>", self.on_row_select)

        self.reload_grid(table_name)


    def values_from_entries(self):
        vals = {}
        for col, dtype, nullable in self.table_meta:
            raw = self.entries[col].get()
            if nullable == "N" and raw == "":
                raise ValueError(f"{col} is mandatory.")
            vals[col] = coerce(raw, dtype)
        return vals

    def insert_row(self, table):
        try:
            vals = self.values_from_entries()
        except ValueError as e:
            messagebox.showerror("Validation error", str(e))
            return
        columns = ", ".join(vals)
        binds   = ", ".join(f":{i+1}" for i in range(len(vals)))
        sql = f"INSERT INTO {table} ({columns}) VALUES ({binds})"
        try:
            with self.conn.cursor() as c:
                c.execute(sql, list(vals.values()))
                self.conn.commit()
        except cx_Oracle.Error as e:
            messagebox.showerror("DB error", str(e))
            return
        self.reload_grid(table)
        self.clear_form()
        messagebox.showinfo("Success", "Row inserted.")

    def update_row(self, table):
        if not self.selected_pk:
            messagebox.showwarning("No row", "Select a row first.")
            return
        try:
            vals = self.values_from_entries()
        except ValueError as e:
            messagebox.showerror("Validation error", str(e))
            return
        sets  = ", ".join(f"{c}=:{i+1}" for i, c in enumerate(vals))
        where = " AND ".join(f"{pk}=:{len(vals)+i+1}" for i, pk in enumerate(self.pk_cols))
        sql   = f"UPDATE {table} SET {sets} WHERE {where}"
        try:
            with self.conn.cursor() as c:
                c.execute(sql, list(vals.values()) + list(self.selected_pk))
                self.conn.commit()
        except cx_Oracle.Error as e:
            messagebox.showerror("DB error", str(e))
            return
        self.reload_grid(table)
        messagebox.showinfo("Success", "Row updated.")

    def delete_row(self, table):
        if not self.selected_pk:
            messagebox.showwarning("No row", "Select a row first.")
            return
        if not messagebox.askyesno("Confirm", "Delete selected row?"):
            return
        where = " AND ".join(f"{pk}=:{i+1}" for i, pk in enumerate(self.pk_cols))
        sql   = f"DELETE FROM {table} WHERE {where}"
        try:
            with self.conn.cursor() as c:
                c.execute(sql, self.selected_pk)
                self.conn.commit()
        except cx_Oracle.Error as e:
            messagebox.showerror("DB error", str(e))
            return
        self.reload_grid(table)
        self.clear_form()
        messagebox.showinfo("Success", "Row deleted.")

    # ------------UI helpers---------------------------------------------------------------------------
    def clear_form(self):
        for e in self.entries.values():
            e.delete(0, "end")
        self.selected_pk = None
        self.grid.selection_remove(self.grid.selection())

    def on_row_select(self, _event):
        sel = self.grid.selection()
        if not sel:
            return
        values = self.grid.item(sel)["values"]
        for (col, *_), val in zip(self.table_meta, values):
            self.entries[col].delete(0, "end")
            self.entries[col].insert(0, val if val is not None else "")
        self.selected_pk = tuple(values[self.grid["columns"].index(pk)] for pk in self.pk_cols)

    def reload_grid(self, table):
        for row in self.grid.get_children():
            self.grid.delete(row)
        cur = self.conn.cursor()
        cur.execute(f"SELECT * FROM {table}")
        for rec in cur:
            self.grid.insert("", "end", values=list(rec))


#---------------------------------------------------------------------------
#  Launch
#---------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        dsn  = make_dsn(DB_HOST, DB_PORT, DB_SERVICE)
        conn = cx_Oracle.connect(user=DB_USER, password=DB_PASSWORD, dsn=dsn)
    except cx_Oracle.Error as err:
        messagebox.showerror("Connection failed", str(err))
        sys.exit(1)

    oracleGUIapp(conn).mainloop()
