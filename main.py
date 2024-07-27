import tkinter as tk
from tkinter import ttk
import threading
from tkinter import messagebox
import webbrowser
from datetime import datetime

from db_operations import check_table_exists, create_table, delete_job, get_jobs_stats, insert_job, select_jobs, select_one_job, truncate_table, update_job_status
from functions import append_to_log, open_log_file
from job_hunt import job_hunt

class JobDatabaseGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Job Database Navigator")
        self.master.geometry("1080x720")
        self.center_window()
    
        create_table()
        self.create_widgets()
        self.create_menu()
        self.load_jobs()
        self.update_stats()

    def create_menu(self):
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        # Menu with submenu
        #file_menu = tk.Menu(menubar, tearoff=0)
        #menubar.add_cascade(label="Htas", menu=file_menu)
        #file_menu.add_command(label="Vaciar DB", command=self.call_vaciar_db)

        menubar.add_command(label="Vaciar DB", command=self.call_vaciar_db)
        menubar.add_command(label="Ver Log", command=self.call_open_log)

    def call_vaciar_db(self):
        # Show a confirmation dialog
        confirm = messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres vaciar la tabla de trabajos? Esta acción no se puede deshacer.")
        if confirm:
            success, message = truncate_table()
            if success:
                self.update_status("Éxito: " + message)
                # If you have any UI elements that display job data, refresh them here
                self.refresh_jobs()  # Assuming you have this method to refresh the job list in the UI
            else:
                self.update_status("Error: " + message)
    
    def open_url(self):
        url = self.url_var.get()
        if url:
            webbrowser.open(url)

    def delete_job_fn(self):
        confirm = messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres Eliminar este trabajo? Esta acción no se puede deshacer.")
        if confirm:
            # Al haber hecho click estas variables deben estar actualizadas
            delete_job(self.title_var.get(), self.company_var.get())
            # Empty details variables
            self.reset_job_details()
            self.refresh_jobs()
            self.update_stats()
    
    def reset_job_details(self):
        self.title_var.set("")
        self.company_var.set("")
        self.url_var.set("")
        self.applied_var.set("")
        self.description_text.delete('1.0', tk.END)

    def create_widgets(self):
        # Configure the Treeview style
        style = ttk.Style()    
        style.configure("Treeview", font=('TkDefaultFont', 11))  # Adjust size as needed
        # style.configure("Treeview.Heading", font=('TkDefaultFont', 12))  # Adjust size as needed

        # Create a frame to hold the Treeview and scrollbar
        tree_frame = ttk.Frame(self.master)
        tree_frame.pack(pady=10, padx=10, expand=True, fill='both')

        self.tree = ttk.Treeview(tree_frame, columns=('Title', 'Company', 'Applied', "Created At"), show='headings', height=10)
        self.tree.heading('Title', text='Title')
        self.tree.heading('Company', text='Company')
        self.tree.heading('Applied', text='Applied')
        self.tree.heading('Created At', text='Created At')

        self.tree.column('Title', width=500)  # Wider column for Title
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

        # New frame for statistics
        self.stats_frame = ttk.Frame(self.master)
        self.stats_frame.pack(pady=(0, 5), padx=10, fill='x')

        # StringVars to hold the statistics
        self.total_jobs_var = tk.StringVar()
        self.applied_jobs_var = tk.StringVar()
        self.discarded_jobs_var = tk.StringVar()
        self.not_applied_jobs_var = tk.StringVar()

        # Labels to display the statistics
        ttk.Label(self.stats_frame, text='Total:').grid(row=0, column=0, sticky='w', padx=5, pady=2)
        ttk.Label(self.stats_frame, textvariable=self.total_jobs_var, font=("TkDefaultFont", 11)).grid(row=0, column=1, sticky='w', padx=5, pady=2)

        ttk.Label(self.stats_frame, text='Applied:').grid(row=0, column=2, sticky='w', padx=5, pady=2)
        ttk.Label(self.stats_frame, textvariable=self.applied_jobs_var, font=("TkDefaultFont", 11)).grid(row=0, column=3, sticky='w', padx=5, pady=2)

        ttk.Label(self.stats_frame, text='Discarded:').grid(row=0, column=4, sticky='w', padx=5, pady=2)
        ttk.Label(self.stats_frame, textvariable=self.discarded_jobs_var, font=("TkDefaultFont", 11)).grid(row=0, column=5, sticky='w', padx=5, pady=2)

        ttk.Label(self.stats_frame, text='Not Applied:').grid(row=0, column=6, sticky='w', padx=5, pady=2)
        ttk.Label(self.stats_frame, textvariable=self.not_applied_jobs_var, font=("TkDefaultFont", 11)).grid(row=0, column=7, sticky='w', padx=5, pady=2)

        # Job Details
        self.details_frame = ttk.LabelFrame(self.master, text='Job Details')
        self.details_frame.pack(pady=5, padx=10, fill='x')

        self.details_frame.columnconfigure(1, weight=1)

        self.title_var = tk.StringVar()
        self.company_var = tk.StringVar()
        self.url_var = tk.StringVar()
        self.applied_var = tk.StringVar()

        ttk.Label(self.details_frame, text='Title:').grid(row=0, column=0, sticky='e', padx=5, pady=2)
        ttk.Entry(self.details_frame, textvariable=self.title_var, width=50, font=('TkDefaultFont', 11)).grid(row=0, column=1, padx=5, pady=2, sticky="we")

        ttk.Label(self.details_frame, text='Company:').grid(row=0, column=2, sticky='e', padx=5, pady=2)
        ttk.Entry(self.details_frame, textvariable=self.company_var, width=50, font=('TkDefaultFont', 11)).grid(row=0, column=3, padx=5, pady=2, sticky="we")

        self.add_update_button = ttk.Button(self.details_frame, text="Add/Update Job", command=self.add_update_job)
        self.add_update_button.grid(row=0, column=4, padx=5, pady=2, sticky="e")

        ttk.Label(self.details_frame, text='URL:').grid(row=1, column=0, sticky='e', padx=5, pady=2)
        ttk.Entry(self.details_frame, textvariable=self.url_var, width=50, font=('TkDefaultFont', 11)).grid(row=1, column=1, columnspan=3, padx=5, pady=2, sticky="we")

        self.delete_job_btn = ttk.Button(self.details_frame, text="Delete Job", command=self.delete_job_fn)
        self.delete_job_btn.grid(row=1, column=4, padx=5, pady=2, sticky="e")
        
        self.open_url_button = ttk.Button(self.details_frame, text="Visit Site", command=self.open_url)
        self.open_url_button.grid(row=2, column=4, padx=5, pady=2, sticky="e")

        ttk.Label(self.details_frame, text='Applied:').grid(row=2, column=0, sticky='e', padx=5, pady=2)
        self.applied_combo = ttk.Combobox(self.details_frame, font=('TkDefaultFont', 11), textvariable=self.applied_var, values=['Not applied', 'Applied', 'Discarded'])
        self.applied_combo.grid(row=2, column=1, padx=5, pady=2, sticky="w")
        self.applied_combo.bind('<<ComboboxSelected>>', self.update_applied_status)

        # Description
        self.description_frame = ttk.LabelFrame(self.master, text='Job Description')
        self.description_frame.pack(pady=10, padx=10, expand=True, fill='both')

        # Create a frame to hold the Text widget and scrollbar
        text_frame = ttk.Frame(self.description_frame)
        text_frame.pack(expand=True, fill='both', padx=5, pady=5)

        # Create the Text widget
        self.description_text = tk.Text(text_frame, wrap=tk.WORD, height=10, font=('TkDefaultFont', 11))
        self.description_text.pack(side='left', expand=True, fill='both')

        # Create the scrollbar
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=self.description_text.yview)
        scrollbar.pack(side='right', fill='y')

        # Configure the Text widget to use the scrollbar
        self.description_text.config(yscrollcommand=scrollbar.set)

        # New button for threaded operation
        self.thread_button = ttk.Button(self.master, text="Hunt!", command=self.start_threaded_operation)
        self.thread_button.pack(pady=10)

        self.status_bar = tk.Label(self.master, text="  Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W, font=('TkDefaultFont', 10))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def call_open_log(self):
        result = open_log_file()
        if result is not True:
            self.update_status("Error al abrir el archivo de Log")    

    def update_status(self, message):
        # Siempre le pone la hora para saber cual fue el ultimo mensaje
        # En caso de que quede un mensaje antiguo ahi y no hayan actualizaciones de estado
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status_bar.config(text=f"  {current_time} - {message}")
        self.status_bar.update_idletasks()

    def add_update_job(self):
        title = self.title_var.get()
        company = self.company_var.get()
        url = self.url_var.get()
        description = self.description_text.get("1.0", tk.END).strip()
        applied = self.applied_var.get()

        if title and company:
            # Check if the job already exists
            existing_job = select_one_job(title, company)
            if existing_job:
                # Update existing job
                # NOTA. por ahora solo actualiza el estado
                success = update_job_status(applied, title, company)
                if success:
                    self.update_status("Job actualizado!")
                    self.refresh_jobs()
                    self.update_stats()
                #TODO else:
            else:
                # Insert new job
                job = {
                    'title': title,
                    'companyName': company,
                    'jobDescription': description,
                    'jobPostingUrl': url,
                    'applied': applied
                }
                success = insert_job(job)
                if success:
                    self.update_status("Job added successfully!")
                    self.refresh_jobs()
                    self.update_stats()
                else:
                    self.update_status("Failed to add job. Please try again.")
        else:
            self.update_status("Title and Company are required fields.")

    def update_stats(self):
        # Get the statistics from the get_jobs_stats function
        stats = get_jobs_stats()

        # Update the StringVars with the new statistics
        self.total_jobs_var.set(str(stats['total']))
        self.applied_jobs_var.set(str(stats['applied']))
        self.discarded_jobs_var.set(str(stats['discarded']))
        self.not_applied_jobs_var.set(str(stats['not_applied']))

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
            details = select_one_job(record[0], record[1])
            if details:
                self.description_text.delete('1.0', tk.END)
                self.description_text.insert(tk.END, details[0])
                self.url_var.set(details[1])

    def update_applied_status(self, event):
        if not self.tree.selection():
            return
        selected_item = self.tree.selection()[0]
        item = self.tree.item(selected_item)
        record = item['values']
        new_status = self.applied_var.get()

        update_job_status(new_status, record[0], record[1])
        self.update_stats()

        # Update treeview
        self.tree.item(selected_item, values=(record[0], record[1], new_status, record[3]))

    def start_threaded_operation(self):
        self.thread_button.config(state='disabled')  # Disable the button while the operation is running
        thread = threading.Thread(target=self.run_job_hunt)
        thread.start()

    def center_window(self, width=1080, height=720, taskbar_offset=40):
        # Get the screen width and height
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()

        # Calculate the x and y coordinates for the Tk root window
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2) - (taskbar_offset / 2)

        # Ensure the window doesn't go off the top of the screen
        y = max(y, 0)

        # Set the dimensions of the screen and where it is placed
        self.master.geometry('%dx%d+%d+%d' % (width, height, int(x), int(y)))

        # Make sure the window is brought to the front
        self.master.lift()
        self.master.attributes('-topmost', True)
        self.master.after_idle(self.master.attributes, '-topmost', False)

    def run_job_hunt(self):
        self.master.after(0, lambda: self.update_status("Searching Jobs..."))  # Schedule job refresh on the main thread
        try:
            job_hunt()
            self.master.after(0, self.refresh_jobs)  # Schedule job refresh on the main thread
            self.master.after(0, self.update_stats)  # Schedule job refresh on the main thread
            self.master.after(0, lambda: self.update_status("Ready"))  # Schedule job refresh on the main thread
        except Exception as e:
            self.update_status(f"An error occurred during job hunt: {str(e)}")
            append_to_log(str(e))
        finally:
             self.thread_button.config(state='normal')

    def refresh_jobs(self):
        self.load_jobs()  # Reload jobs from the database
        self.thread_button.config(state='normal')  # Re-enable the button

if __name__ == "__main__":
    root = tk.Tk()
    app = JobDatabaseGUI(root)
    root.mainloop()