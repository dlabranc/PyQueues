import tkinter as tk
from tkinter import filedialog, ttk
import getpass
from .config import SOFTWARE_QUEUES
from .client_config import IP, PORT
from .client import *
import pandas as pd
import time

USER_ID = getpass.getuser()

def submission_and_update(ip, port, user, queue_name):

    return f"Submitted job to {ip}:{port} as {user} in queue {queue_name}"

def run_gui():
    def process_inputs():
        ip = ip_entry.get()
        port = port_entry.get()
        user = user_entry.get()
        queue_name = dropdown_var.get()
        

        if not ip or not port or not user:
            output_label.config(text="Error: IP, Port, and User fields cannot be empty.")
            return
        if not queue_name:
            output_label.config(text="Error: Queue field cannot be empty.")
            return
        
        if not script_paths:
            output_label.config(text="Error: No scripts selected.")
            return

        for script in script_paths:
            if not script.endswith('.py'):
                output_label.config(text=f"Error: {script} is not a Python script.")
                continue
            submit_job(script, queue_name, additional_files, user_id=user, server_url=f"http://{ip}:{port}")
            time.sleep(0.1)  # Small delay to ensure the job is processed
            
        # Update the job status table
        try:
            update_table()
        except Exception as e:
            output_label.config(text=f"Error updating job table: {e}")
            return

        result = f"Submitted job to {ip}:{port} as {user} in queue {queue_name}"
        output_label.config(text=f"{result}")

    root = tk.Tk()
    root.title("Jobs Queue Server GUI")
    root.geometry("1400x750+0+0")

    # === Layout configuration ===
    # Ensure the grid rows and columns expand properly
    root.columnconfigure(1, weight=1)  # Text widget column
    root.columnconfigure(2, weight=1)  # Text widget column


    # === LEFT COLUMN: Configuration Inputs (clean, uniform vertical spacing) ===
    form_pady = (10,10)  # uniform vertical space

    # === Frame for left-side inputs ===
    left_frame = tk.Frame(root)
    left_frame.grid(row=0, column=0, rowspan=5, sticky="nsew", padx=10, pady=10)
    left_frame.columnconfigure(0, weight=1)  # Make the left column expand
    left_frame.rowconfigure(0, weight=1)  # Make the left row expand

    # IP
    tk.Label(left_frame, text="IP:").grid(row=0, column=0, sticky="w", padx=20, pady=form_pady)
    ip_entry = tk.Entry(left_frame)
    ip_entry.insert(0, IP)
    ip_entry.grid(row=0, column=0, sticky="e", padx=100, pady=form_pady)

    # Port
    tk.Label(left_frame, text="Port:").grid(row=1, column=0, sticky="w", padx=20, pady=form_pady)
    port_entry = tk.Entry(left_frame)
    port_entry.insert(0, PORT)
    port_entry.grid(row=1, column=0, sticky="e", padx=100, pady=form_pady)

    # User
    tk.Label(left_frame, text="User:").grid(row=2, column=0, sticky="w", padx=20, pady=form_pady)
    user_entry = tk.Entry(left_frame)
    user_entry.insert(0, USER_ID)
    user_entry.grid(row=2, column=0, sticky="e", padx=100, pady=form_pady)

    # Queue
    tk.Label(left_frame, text="Queue:").grid(row=3, column=0, sticky="w", padx=20, pady=form_pady)
    dropdown_var = tk.StringVar(value=SOFTWARE_QUEUES[0])
    dropdown = ttk.Combobox(left_frame, textvariable=dropdown_var, width=17)
    dropdown['values'] = SOFTWARE_QUEUES
    dropdown.grid(row=3, column=0, sticky="e", padx=100, pady=form_pady)

    # === RIGHT COLUMN: File Selection & List ===

    # === Variables to hold paths ===
    script_paths = []
    additional_files = []

    # === Right-side Text Area with Scrollbars ===
    # === Frame to hold Text + Scrollbars ===
    text_frame = tk.Frame(root, width=60, height=40)
    text_frame.grid(row=1, column=1, rowspan=10, columnspan=2, sticky="nsew", padx=(10, 0), pady=(5, 0))
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

    additional_files = []  # List to hold additional files selected by the user
    # === Functions ===
    def update_display():
        file_display.delete("1.0", tk.END) 
        for script in script_paths:
            file_display.insert("end", f"[SCRIPT] {script}\n", "script")
        for f in additional_files:
            file_display.insert(tk.END, f"[SUPPORT FILE] {f}\n")
        file_display.tag_configure("script", foreground="red")

    def select_scripts():
        nonlocal script_paths
        files = filedialog.askopenfilenames(
            title="Select Scripts",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        if files:
            script_paths = list(files)
            update_display()
        return
    def select_files():
        files = filedialog.askopenfilenames(title="Select Files")
        if files:
            additional_files.extend(files)
            list(set(additional_files))  # Remove duplicates
            update_display()
        return
    
    def select_folder():
        folder = filedialog.askdirectory(title="Select Folder")
        if folder:
            # Recursively walk through the folder
            for root, dirs, files in os.walk(folder):
                for file in files:
                    full_path = os.path.abspath(os.path.join(root, file))
                    additional_files.append(full_path)
            update_display()
        return

    # === Buttons ===
    tk.Button(root, text="Select Scripts", command=select_scripts).grid(row=0, column=1, sticky="w", padx=10, pady=5)
    tk.Button(root, text="Select Files", command=select_files).grid(row=0, column=1, sticky="w", padx=100, pady=5)
    tk.Button(root, text="Select Folder", command=select_folder).grid(row=0, column=1, sticky="w", padx=180, pady=5)


    # === RUN Button and Output ===
    tk.Button(text_frame, text="Run Job(s)", command=process_inputs, width=40, height=1).grid(row=10, column=0, columnspan=2, pady=7)
    output_label = tk.Label(text_frame, text="", wraplength=800, justify="left")
    output_label.grid(row=11, column=0, columnspan=3, pady=(5, 20), padx=10, sticky="")

    ######################
    # Job Status Section #
    ######################
    separator = tk.Frame(root, height=2, bd=1, relief="sunken", bg="gray")
    separator.grid(row=10, column=0, columnspan=3, sticky="ew", padx=10, pady=10)

    def update_table():
        
        # Example DataFrame (replace this with yours)
        df = get_all_jobs(server_url=f"http://{ip_entry.get()}:{port_entry.get()}")
        df = df[columns].sort_values(by='created_at', ascending=False)  # Ensure df has the correct columns

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
        start_df = get_all_jobs(server_url=f"http://{ip_entry.get()}:{port_entry.get()}")
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
    status_dropdown = ttk.Combobox(table_frame, textvariable=status_var, values=["all", "completed", "running", "queued", "interrupted", "never started", "failed"], state="readonly")
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
    
    table.grid(row=1, column=0, columnspan=4, sticky="nsew", pady=(40, 0))

    # Scrollbars
    scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview,)
    scroll_y.grid(row=1, column=4, sticky="ns", pady=(40, 0))
    table.config(yscrollcommand=scroll_y.set)

    scroll_x = ttk.Scrollbar(table_frame, orient="horizontal", command=table.xview)
    scroll_x.grid(row=3, column=0, columnspan=4, sticky="ew")
    table.config(xscrollcommand=scroll_x.set)



    # === Refresh Button ===
    refresh_button = tk.Button(table_frame, text="Refresh Jobs", command=update_table)
    refresh_button.grid(row=0, column=3, pady=(5, 2))
    try:
        update_table()
    except:
        print("Error loading initial job data. Please ensure the server is running or check the right IP and PORT are set in user_config.py")

    ############
    # Download #
    ############

    def download_selected_jobs():
        download_display.delete("1.0", tk.END) 

        selected_items = table.selection()
        if not selected_items:
            print("No jobs selected.")
            download_display.insert(tk.END, 'No Jobs Selected')
            return

        # Ask for folder to save results
        folder = work_folder_var.get()
        if not folder:
            folder = filedialog.askdirectory(title="Select Download Folder")
            if not folder:
                return  # user canceled

        count = 0
        
        for item_id in selected_items:
            row = table.item(item_id)["values"]
            job_id = row[0]  # adjust index to match JobID column
            filename = f"{folder}/{job_id}_log.txt"
            download_job_log(job_id, save_as=filename, server_url=f"http://{ip_entry.get()}:{port_entry.get()}")
            if row[2] != "completed":
                print(f"Job {job_id} is not completed. Skipping download.")
                download_display.insert(tk.END, f"{job_id} : Download failed!\n", "fail")
                continue
            count += 1
            filename = f"{folder}/{job_id}_results.zip"
            download_job_results(job_id, save_as=filename)
            download_display.insert(tk.END, f"{job_id} : Download successfull!\n", "success")

        print(f"Downloaded {count}/{len(selected_items)} job(s) to {folder}")
        download_display.insert(tk.END, f"Downloaded {count}/{len(selected_items)} job(s) to {folder}\n")
        download_display.tag_configure("fail", foreground="red")
        download_display.tag_configure("success", foreground="green")



    root.rowconfigure(12, weight=1)

    # === Download Frame ===
    download_frame = tk.Frame(root, width=500, height=550)
    download_frame.grid(row=12, column=0, columnspan=2, sticky="nsew", padx=10, pady=0)
    download_frame.columnconfigure(0, weight=1)
    download_frame.columnconfigure(1, weight=1)  # Needed for right-aligned text box
    download_frame.rowconfigure(0, weight=0)
    download_frame.rowconfigure(1, weight=0)
    download_frame.rowconfigure(2, weight=0)
    download_frame.rowconfigure(3, weight=1)  # For the text box

    # === Download instruction label ===
    tk.Label(download_frame, text="Select Job(s) from above and Download Results").grid(
        row=0, column=0, columnspan=1, sticky="w", padx=10, pady=5
    )

    # === Download Button ===
    download_button = tk.Button(download_frame, text="Download Results", command=download_selected_jobs, width=20)
    download_button.grid(row=0, column=0, sticky="e", padx=300, pady=5)

    # === Folder Label and Entry ===
    tk.Label(download_frame, text="Download Folder:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
    work_folder_var = tk.StringVar()
    work_folder_entry = tk.Entry(download_frame, textvariable=work_folder_var, width=80)
    work_folder_entry.grid(row=1, column=0, sticky="w", padx=130, pady=5)

    # === Browse Button ===
    def browse_work_folder():
        folder = filedialog.askdirectory(title="Select Download Folder")
        if folder:
            work_folder_var.set(folder)

    browse_button = tk.Button(download_frame, text="Browse", command=browse_work_folder, width=20)
    browse_button.grid(row=2, column=0, sticky="w", padx=130, pady=5)

    # === Text Frame for Download Log ===
    MAX_HEIGHT = 200  # pixels
    download_text_frame = tk.Frame(download_frame, height=MAX_HEIGHT, width=700)
    download_text_frame.grid(row=0, column=1, rowspan=4, sticky="nsew", padx=10, pady=5)
    download_text_frame.grid_propagate(False)  # Prevent expansion beyond fixed size
    download_text_frame.columnconfigure(0, weight=1)
    download_text_frame.rowconfigure(0, weight=1)

    # === Text Widget ===
    download_display = tk.Text(download_text_frame, wrap="none")
    download_display.grid(row=0, column=0, sticky="nsew")

    # === Scrollbars ===
    scrollbar_y = tk.Scrollbar(download_text_frame, orient="vertical", command=download_display.yview)
    scrollbar_y.grid(row=0, column=1, sticky="ns")

    scrollbar_x = tk.Scrollbar(download_text_frame, orient="horizontal", command=download_display.xview)
    scrollbar_x.grid(row=1, column=0, sticky="ew")

    download_display.config(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
    # dw_output_label = tk.Text(download_frame, text="",  wraplength=800, justify="left")
    # dw_output_label.grid(row=2, column=1, columnspan=2, sticky="w", padx=5, pady=5)

    root.mainloop()

if __name__ == "__main__":
    run_gui()