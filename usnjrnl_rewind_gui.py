import tkinter as tk
from tkinter import filedialog, messagebox
import os
import time
from usnjrnl_rewind import rewind

class USNRewindGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("USNJRNL Rewind GUI")
        self.root.geometry("600x400")

        # Variable to store directory path
        self.input_dir_path = tk.StringVar()
        self.output_path = tk.StringVar()

        # Create GUI elements
        self.create_widgets()

    def create_widgets(self):
        # Input directory path
        tk.Label(self.root, text="Input Directory:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        tk.Entry(self.root, textvariable=self.input_dir_path, width=50).grid(row=0, column=1, padx=10, pady=5)
        tk.Button(self.root, text="Browse", command=self.browse_input_dir).grid(row=0, column=2, padx=10, pady=5)

        # Output folder input
        tk.Label(self.root, text="Output Folder:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        tk.Entry(self.root, textvariable=self.output_path, width=50).grid(row=1, column=1, padx=10, pady=5)
        tk.Button(self.root, text="Browse", command=self.browse_output_folder).grid(row=1, column=2, padx=10, pady=5)

        # Run button
        tk.Button(self.root, text="Run", command=self.run_rewind, bg="green", fg="white").grid(row=2, column=1, pady=10)

        # Log output
        tk.Label(self.root, text="Logs:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.log_text = tk.Text(self.root, width=70, height=15, state="disabled")
        self.log_text.grid(row=4, column=0, columnspan=3, padx=10, pady=5)

    def browse_input_dir(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.input_dir_path.set(folder_path)

    def browse_output_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.output_path.set(folder_path)

    def log_message(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.config(state="disabled")
        self.log_text.see(tk.END)

    def find_mft_and_usnjrnl_files(self, directory):
        mft_files = []
        usnjrnl_files = []

        for root, _, files in os.walk(directory):
            for file in files:
                if "$MFT_Output" in file:
                    mft_files.append(os.path.join(root, file))
                elif "$J_Output" in file:
                    usnjrnl_files.append(os.path.join(root, file))

        return mft_files, usnjrnl_files

    def pair_files(self, mft_files, usnjrnl_files):
        paired_files = []

        # Pair based on timestamps (or file names if consistent)
        mft_files.sort(key=os.path.getmtime)
        usnjrnl_files.sort(key=os.path.getmtime)

        for mft_file, usnjrnl_file in zip(mft_files, usnjrnl_files):
            paired_files.append((mft_file, usnjrnl_file))

        return paired_files

    def run_rewind(self):
        input_dir = self.input_dir_path.get()
        output_folder = self.output_path.get()

        if not os.path.exists(input_dir):
            messagebox.showerror("Error", "Invalid input directory path.")
            return

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        self.log_message("Searching for MFT and USNJRNL files...")
        mft_files, usnjrnl_files = self.find_mft_and_usnjrnl_files(input_dir)

        if not mft_files or not usnjrnl_files:
            messagebox.showerror("Error", "No matching MFT or USNJRNL files found.")
            return

        self.log_message(f"Found {len(mft_files)} MFT files and {len(usnjrnl_files)} USNJRNL files.")

        paired_files = self.pair_files(mft_files, usnjrnl_files)
        self.log_message(f"Paired {len(paired_files)} MFT and USNJRNL files.")

        self.log_message("Starting USNJRNL rewind process...")
        start_time = time.time()

        try:
            for i, (mft_file, usnjrnl_file) in enumerate(paired_files):
                pair_output_folder = os.path.join(output_folder, f"Pair_{i + 1}")
                os.makedirs(pair_output_folder, exist_ok=True)
                self.log_message(f"Processing pair {i + 1}:\n  MFT: {mft_file}\n  USNJRNL: {usnjrnl_file}\n  Output: {pair_output_folder}")
                rewind(pair_output_folder, mft_file, usnjrnl_file)

            self.log_message("USNJRNL rewind completed successfully.")
        except Exception as e:
            self.log_message(f"Error during processing: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")

        end_time = time.time()
        elapsed_time = end_time - start_time
        self.log_message(f"Process completed in {elapsed_time:.2f} seconds.")

if __name__ == "__main__":
    root = tk.Tk()
    app = USNRewindGUI(root)
    root.mainloop()
