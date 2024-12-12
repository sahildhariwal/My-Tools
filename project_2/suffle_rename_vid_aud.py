import os
import tkinter as tk
from tkinter import filedialog, messagebox
import random


def rename_files_sequentially(file_list, target_dir):
    """Rename files sequentially."""
    for index, file in enumerate(file_list, start=1):
        file_ext = os.path.splitext(file)[1]
        new_name = f"file{index}{file_ext}"
        src = os.path.join(target_dir, file)
        dst = os.path.join(target_dir, new_name)
        os.rename(src, dst)


def rename_files_shuffled(file_list, target_dir):
    """Rename files randomly."""
    shuffled_names = random.sample(file_list, len(file_list))
    for index, file in enumerate(shuffled_names, start=1):
        file_ext = os.path.splitext(file)[1]
        new_name = f"file{index}{file_ext}"
        src = os.path.join(target_dir, file)
        dst = os.path.join(target_dir, new_name)
        os.rename(src, dst)


class FileRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Batch File Renamer")
        self.root.geometry("500x300")

        # Input Directory
        tk.Label(root, text="Select Input Directory").pack(pady=5)
        self.directory_var = tk.StringVar()
        tk.Entry(root, textvariable=self.directory_var, width=50).pack(pady=5)
        tk.Button(root, text="Select Directory", command=self.select_directory).pack(pady=5)

        # Shuffle Option
        self.shuffle_var = tk.BooleanVar()
        tk.Checkbutton(root, text="Shuffle Files", variable=self.shuffle_var).pack(pady=5)

        # Rename Button
        tk.Button(root, text="Rename Files", command=self.rename_files).pack(pady=10)

        # Status Label
        self.status_label = tk.Label(root, text="", wraplength=400, justify="left")
        self.status_label.pack(pady=10)

    def select_directory(self):
        """Allow user to select the directory."""
        directory = filedialog.askdirectory(title="Select Directory")
        if directory:
            self.directory_var.set(directory)

    def rename_files(self):
        """Rename files based on shuffle or sequential logic."""
        directory = self.directory_var.get()
        if not directory:
            messagebox.showerror("Error", "Please select a directory first.")
            return

        try:
            # Get files in the directory
            files = [
                f for f in os.listdir(directory)
                if f.lower().endswith((".mp4", ".mp3", ".avi", ".mkv", ".mov"))
            ]
            if not files:
                messagebox.showerror("Error", "No supported media files found in the directory.")
                return

            if self.shuffle_var.get():
                rename_files_shuffled(files, directory)
                self.status_label.config(
                    text=f"Files renamed randomly in shuffled order. Total: {len(files)}"
                )
            else:
                rename_files_sequentially(files, directory)
                self.status_label.config(
                    text=f"Files renamed sequentially. Total: {len(files)}"
                )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to rename files: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = FileRenamerApp(root)
    root.mainloop()
