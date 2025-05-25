import tkinter as tk
from tkinter import filedialog, ttk
import getpass
from .config import SOFTWARE_QUEUES
from .client_config import IP, PORT
from .client import *
import pandas as pd

USER_ID = getpass.getuser()

def your_function(ip, port, user, queue_name):
    return f"Submitted job to {ip}:{port} as {user} in queue {queue_name}"

def run_gui():
    def process_inputs():
        ip = ip_entry.get()
        port = port_entry.get()
        user = user_entry.get()
        selection = dropdown_var.get()
        result = your_function(ip, port, user, selection)
        output_label.config(text=f"{result}")

    root = tk.Tk()
    root.title("Jobs Queue Server GUI")
    root.geometry("1000x700")

    # === Layout configuration ===
    # Ensure the grid rows and columns expand properly
    root.columnconfigure(1, weight=1)  # Text widget column
    root.columnconfigure(2, weight=1)  # Text widget column


    # === LEFT COLUMN: Configuration Inputs (clean, uniform vertical spacing) ===
    form_pady = (5,0)  # uniform vertical space

    # IP
    tk.Label(root, text="IP:").grid(row=1, column=0, sticky="w", padx=20, pady=form_pady)
    ip_entry = tk.Entry(root)
    ip_entry.insert(0, IP)
    ip_entry.grid(row=1, column=0, sticky="e", padx=100, pady=form_pady)

    # Port
    tk.Label(root, text="Port:").grid(row=2, column=0, sticky="w", padx=20, pady=form_pady)
    port_entry = tk.Entry(root)
    port_entry.insert(0, PORT)
    port_entry.grid(row=2, column=0, sticky="e", padx=100, pady=form_pady)

    # User
    tk.Label(root, text="User:").grid(row=3, column=0, sticky="w", padx=20, pady=form_pady)
    user_entry = tk.Entry(root)
    user_entry.insert(0, USER_ID)
    user_entry.grid(row=3, column=0, sticky="e", padx=100, pady=form_pady)

    # Queue
    tk.Label(root, text="Queue:").grid(row=4, column=0, sticky="w", padx=20, pady=form_pady)
    dropdown_var = tk.StringVar(value=SOFTWARE_QUEUES[0])
    dropdown = ttk.Combobox(root, textvariable=dropdown_var, width=17)
    dropdown['values'] = SOFTWARE_QUEUES
    dropdown.grid(row=4, column=0, sticky="e", padx=100, pady=form_pady)

    # === RIGHT COLUMN: File Selection & List ===

    # === Variables to hold paths ===
    script_path = None
    additional_files = []

    # === Right-side Text Area with Scrollbars ===
    # === Frame to hold Text + Scrollbars ===
    text_frame = tk.Frame(root, width=60, height=20)
    text_frame.grid(row=1, column=1, rowspan=4, sticky="nsew", padx=(10, 0), pady=(5, 0))
    text_frame.grid_propagate(False)    
    text_frame.config(width=800, height=200)
    text_frame.columnconfigure(0, weight=1)
    text_frame.rowconfigure(0, weight=1)

    # === Text Widget ===
    file_display = tk.Text(text_frame, wrap="none")
    file_display.grid(row=0, column=0, sticky="nsew")

    # === Scrollbars ===
    scrollbar_y = tk.Scrollbar(text_frame, orient="vertical", command=file_display.yview)
    scrollbar_y.grid(row=0, column=1, sticky="ns")

    scrollbar_x = tk.Scrollbar(text_frame, orient="horizontal", command=file_display.xview)
    scrollbar_x.grid(row=1, column=0, sticky="ew")


    file_display.config(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

    # === Text styling tag ===
    file_display.tag_configure("script", foreground="red")

    # === Functions ===
    def update_display():
        file_display.delete("1.0", tk.END) 
        if script_path:
            file_display.insert(tk.END, f"[SCRIPT] {script_path}\n", "script")
        for f in additional_files:
            file_display.insert(tk.END, f"[SUPPORT FILE] {f}\n")

    def select_script():
        nonlocal script_path
        path = filedialog.askopenfilename(title="Select script", filetypes=[("Python files", "*.py"), ("All files", "*.*")])
        if path:
            script_path = path
            update_display()

    def select_files():
        files = filedialog.askopenfilenames(title="Select additional files")
        nonlocal additional_files
        additional_files = files
        update_display()

    # === Buttons ===
    tk.Button(root, text="Select Script", command=select_script).grid(row=0, column=1, sticky="w", padx=10, pady=5)
    tk.Button(root, text="Select Additional Files", command=select_files).grid(row=0, column=1, sticky="w", padx=100, pady=5)


    # === RUN Button and Output ===
    tk.Button(root, text="Run", command=process_inputs, width=40, height=3).grid(row=6, column=0, columnspan=2, pady=20)
    output_label = tk.Label(root, text="", wraplength=800, justify="left")
    output_label.grid(row=7, column=0, columnspan=2, pady=0, padx=10, sticky="")

    ######################
    # Job Status Section #
    ######################
    separator = tk.Frame(root, height=2, bd=1, relief="sunken", bg="gray")
    separator.grid(row=10, column=0, columnspan=3, sticky="ew", padx=10, pady=10)

    def update_table():
        
        # Example DataFrame (replace this with yours)
        df = get_all_jobs()
        df = df[columns]  # Ensure df has the correct columns

        # Filter DataFrame based on user input
        user_filter = user_var.get()
        status_filer = status_var.get()
        queue_filter = queue_var.get()

        if user_filter != "all":
            df = df[df['user_id'] == user_filter]
        if status_filer != "all":
            df = df[df['status'] == status_filer]
        if queue_filter != "all":
            df = df[df['queue_name'] == queue_filter]

        # Clear old columns and rows
        table.delete(*table.get_children())
        table["columns"] = columns
        for col in columns:
            table.heading(col, text=col)
            if col == 'created_at' or col == 'updated_at':
                table.column(col, width=150, anchor="center")
            elif col == 'user_id' or col == 'queue_name' or col == 'status':
                table.column(col, width=30, anchor="center")
            else:
                table.column(col, width=80, anchor="center")

        # Insert new rows
        for _, row in df.iterrows():
            status = row["status"]
            table.insert("", "end", values=list(row), tags=(status,))

    try:
        start_df = get_all_jobs()
    except:
        start_df = pd.DataFrame(columns=['job_id', 'user_id', 'status', 'queue_name', 'created_at', 'updated_at'])
    # === Treeview (DataFrame display) ===
    table_frame = tk.Frame(root)
    table_frame.grid(row=11, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)
    table_frame.columnconfigure(0, weight=1)
    table_frame.columnconfigure(1, weight=1)
    table_frame.columnconfigure(2, weight=1)
    table_frame.columnconfigure(3, weight=1)
    table_frame.rowconfigure(0, weight=1)

    # Dropdown for user filter
    tk.Label(table_frame, text="User:").grid(row=0, column=0, sticky="w", padx=5, pady=(5, 2))
    user_var = tk.StringVar(value="all")
    user_dropdown = ttk.Combobox(table_frame, textvariable=user_var, values=["all"] + [user for user in start_df['user_id'].unique()], state="readonly")
    user_dropdown.grid(row=0, column=0, sticky="w", padx=50, pady=(5, 2))

    # Dropdown for status filter
    tk.Label(table_frame, text="Status:").grid(row=0, column=1, sticky="w", padx=5, pady=(5, 2))
    status_var = tk.StringVar(value="all")
    status_dropdown = ttk.Combobox(table_frame, textvariable=status_var, values=["all", "queued", "running", "completed", "interrupted", "never started"], state="readonly")
    status_dropdown.grid(row=0, column=1, sticky="w", padx=50, pady=(5, 2))

    # Dropdown for queue filter
    tk.Label(table_frame, text="Queue:").grid(row=0, column=2, sticky="w", padx=5, pady=(5, 2))
    queue_var = tk.StringVar(value="all")
    queue_dropdown = ttk.Combobox(table_frame, textvariable=queue_var, values=["all"] + SOFTWARE_QUEUES, state="readonly")
    queue_dropdown.grid(row=0, column=2, sticky="w", padx=50, pady=(5, 2))

    columns = ['job_id',  'user_id', 'status', 'queue_name', 'created_at', 'updated_at'] # Replace with your real columns
    table = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
    table.tag_configure("completed", background="#89f653")       # light green
    table.tag_configure("running", background="#f5e967")    # light yellow
    table.tag_configure("queued", background="#fcb25d")     # light red
    table.tag_configure("interrupted", background="#ec5f5f")     # light red
    table.tag_configure("never started", background="#ec5f5f")     # light red
    table.tag_configure("failed", background="#ec5f5f")     # light red
    for col in columns:
        table.heading(col, text=col)
        if col == 'created_at' or col == 'updated_at':
            table.column(col, width=150, anchor="center")
        elif col == 'user_id' or col == 'queue_name':
            table.column(col, width=40, anchor="center")
        else:
            table.column(col, width=80, anchor="center")
    
    table.grid(row=2, column=0, columnspan=4, sticky="nsew", pady=(40, 0))

    # Scrollbars
    scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview,)
    scroll_y.grid(row=2, column=4, sticky="ns", pady=(40, 0))
    table.config(yscrollcommand=scroll_y.set)

    scroll_x = ttk.Scrollbar(table_frame, orient="horizontal", command=table.xview)
    scroll_x.grid(row=3, column=0, columnspan=4, sticky="ew")
    table.config(xscrollcommand=scroll_x.set)



    # === Refresh Button ===
    refresh_button = tk.Button(root, text="Refresh Jobs", command=update_table)
    refresh_button.grid(row=12, column=0, columnspan=3, pady=(0, 20))
    try:
        update_table()
    except:
        print("Error loading initial job data. Please ensure the server is running or check the right IP and PORT are set in user_config.py")
    root.mainloop()

if __name__ == "__main__":
    run_gui()
