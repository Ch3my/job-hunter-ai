import sqlite3
import tkinter as tk
from tkinter import ttk
import threading
from tkinter import messagebox
import webbrowser

from db_operations import check_table_exists, create_table, select_jobs, truncate_table, update_job_status
from job_hunt import job_hunt

class JobDatabaseGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Job Database Navigator")
        self.master.geometry("800x800")

        create_table()
        self.create_widgets()
        self.create_menu()
        self.load_jobs()

    def create_menu(self):
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Htas", menu=file_menu)
        file_menu.add_command(label="Vaciar DB", command=self.call_vaciar_db)

    def call_vaciar_db(self):
        # Show a confirmation dialog
        confirm = messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres vaciar la tabla de trabajos? Esta acción no se puede deshacer.")
        if confirm:
            success, message = truncate_table()
            if success:
                messagebox.showinfo("Éxito", message)
                # If you have any UI elements that display job data, refresh them here
                self.refresh_jobs()  # Assuming you have this method to refresh the job list in the UI
            else:
                messagebox.showerror("Error", message)
        else:
            messagebox.showinfo("Cancelado", "La operación ha sido cancelada.")
    
    def open_url(self):
        url = self.url_var.get()
        if url:
            webbrowser.open(url)
    
    def create_widgets(self):
        # Create a frame to hold the Treeview and scrollbar
        tree_frame = ttk.Frame(self.master)
        tree_frame.pack(pady=10, padx=10, expand=True, fill='both')

        # Create the Treeview with a smaller height to encourage scrolling
        self.tree = ttk.Treeview(tree_frame, columns=('Title', 'Company', 'Applied', "Created At"), show='headings', height=10)
        self.tree.heading('Title', text='Title')
        self.tree.heading('Company', text='Company')
        self.tree.heading('Applied', text='Applied')
        self.tree.heading('Created At', text='Created At')

        self.tree.column('Title', width=300)  # Wider column for Title
        self.tree.column('Applied', width=100)
        
        # Create the scrollbar
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        
        # Configure the Treeview to use the scrollbar
        self.tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # Grid layout for Treeview and scrollbar
        self.tree.grid(row=0, column=0, sticky='nsew')
        tree_scrollbar.grid(row=0, column=1, sticky='ns')

        # Configure the grid
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        self.tree.bind('<<TreeviewSelect>>', self.item_selected)

        # Job Details
        self.details_frame = ttk.LabelFrame(self.master, text='Job Details')
        self.details_frame.pack(pady=10, padx=10, fill='x')

        self.details_frame.columnconfigure(1, weight=1)

        self.title_var = tk.StringVar()
        self.company_var = tk.StringVar()
        self.url_var = tk.StringVar()
        self.applied_var = tk.StringVar()

        ttk.Label(self.details_frame, text='Title:').grid(row=0, column=0, sticky='e', padx=5, pady=2)
        ttk.Entry(self.details_frame, textvariable=self.title_var, state='readonly', width=50).grid(row=0, column=1, padx=5, pady=2, sticky="we")

        ttk.Label(self.details_frame, text='Company:').grid(row=1, column=0, sticky='e', padx=5, pady=2)
        ttk.Entry(self.details_frame, textvariable=self.company_var, state='readonly', width=50).grid(row=1, column=1, padx=5, pady=2, sticky="we")

        ttk.Label(self.details_frame, text='URL:').grid(row=2, column=0, sticky='e', padx=5, pady=2)
        ttk.Entry(self.details_frame, textvariable=self.url_var, state='readonly', width=50).grid(row=2, column=1, padx=5, pady=2, sticky="we")
        
        self.open_url_button = ttk.Button(self.details_frame, text="Visit Site", command=self.open_url)
        self.open_url_button.grid(row=2, column=2, padx=5, pady=2)

        ttk.Label(self.details_frame, text='Applied:').grid(row=3, column=0, sticky='e', padx=5, pady=2)
        self.applied_combo = ttk.Combobox(self.details_frame, textvariable=self.applied_var, values=['Not applied', 'Applied', 'Discarded'])
        self.applied_combo.grid(row=3, column=1, padx=5, pady=2, sticky="w")
        self.applied_combo.bind('<<ComboboxSelected>>', self.update_applied_status)

        # Description
        self.description_frame = ttk.LabelFrame(self.master, text='Job Description')
        self.description_frame.pack(pady=10, padx=10, expand=True, fill='both')

        # Create a frame to hold the Text widget and scrollbar
        text_frame = ttk.Frame(self.description_frame)
        text_frame.pack(expand=True, fill='both', padx=5, pady=5)

        # Create the Text widget
        self.description_text = tk.Text(text_frame, wrap=tk.WORD, height=10)
        self.description_text.pack(side='left', expand=True, fill='both')

        # Create the scrollbar
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=self.description_text.yview)
        scrollbar.pack(side='right', fill='y')

        # Configure the Text widget to use the scrollbar
        self.description_text.config(yscrollcommand=scrollbar.set)

        # New button for threaded operation
        self.thread_button = ttk.Button(self.master, text="Hunt!", command=self.start_threaded_operation)
        self.thread_button.pack(pady=10)

    def load_jobs(self):
        # Clear existing items in the treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        table_exists = check_table_exists()

        if table_exists:
            rows = select_jobs()
            for row in rows:
                self.tree.insert('', 'end', values=row)
        else:
            print("The 'jobs' table doesn't exist. Please make sure you've run your job scraping script first.")

    def item_selected(self, event):
        for selected_item in self.tree.selection():
            item = self.tree.item(selected_item)
            record = item['values']
            self.title_var.set(record[0])
            self.company_var.set(record[1])
            self.applied_var.set(record[2])

            # Fetch additional details
            self.cursor.execute("SELECT description, joburl FROM jobs WHERE title=? AND company=?", (record[0], record[1]))
            details = self.cursor.fetchone()
            if details:
                self.description_text.delete('1.0', tk.END)
                self.description_text.insert(tk.END, details[0])
                self.url_var.set(details[1])

    def update_applied_status(self, event):
        selected_item = self.tree.selection()[0]
        item = self.tree.item(selected_item)
        record = item['values']
        new_status = self.applied_var.get()

        update_job_status(new_status, record[0], record[1])

        # Update treeview
        self.tree.item(selected_item, values=(record[0], record[1], new_status, record[3]))

    def start_threaded_operation(self):
        self.thread_button.config(state='disabled')  # Disable the button while the operation is running
        thread = threading.Thread(target=self.run_job_hunt)
        thread.start()

    def run_job_hunt(self):
        job_hunt()
        self.master.after(0, self.refresh_jobs)  # Schedule job refresh on the main thread

    def refresh_jobs(self):
        self.load_jobs()  # Reload jobs from the database
        self.thread_button.config(state='normal')  # Re-enable the button
        # print("Job hunt completed and jobs refreshed!")

if __name__ == "__main__":
    root = tk.Tk()
    app = JobDatabaseGUI(root)
    root.mainloop()