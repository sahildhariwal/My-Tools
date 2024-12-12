import os
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import multiprocessing
import subprocess


def extract_audio_with_gpu(video_path, output_dir):
    """Extract audio from a video file using GPU acceleration with ffmpeg."""
    try:
        video_name = os.path.basename(video_path)
        audio_name = os.path.splitext(video_name)[0] + ".mp3"
        output_path = os.path.join(output_dir, audio_name)

        # Use ffmpeg with NVIDIA's GPU acceleration (CUDA) here
        # Ensure ffmpeg has GPU/CUDA support
        command = [
            "ffmpeg",
            "-hwaccel", "cuda",  # Enable GPU hardware acceleration with CUDA
            "-i", video_path,
            "-q:a", "0",  # Set audio quality
            "-map", "a",
            output_path,
            "-y",  # Automatically overwrite output files
        ]

        # Call subprocess for GPU-based ffmpeg execution
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if os.path.exists(output_path):
            return True
        else:
            return f"GPU extraction failed for {video_name}."
    except Exception as e:
        return f"Error processing {video_path}: {e}"


def init_worker(lock_, completed_tasks_, total_tasks_, queue_):
    """Setup shared variables for multiprocessing workers."""
    global lock, completed_tasks, total_tasks, queue
    lock = lock_
    completed_tasks = completed_tasks_
    total_tasks = total_tasks_
    queue = queue_


def worker(video_path_output):
    """Worker logic for GPU-accelerated extraction."""
    video_path, output_dir = video_path_output
    result = extract_audio_with_gpu(video_path, output_dir)

    with lock:
        completed_tasks.value += 1
        progress = (completed_tasks.value / total_tasks) * 100
        queue.put((progress, result))


def process_videos(video_list, output_dir, queue):
    """Process video list using multiprocessing."""
    os.makedirs(output_dir, exist_ok=True)

    with multiprocessing.Manager() as manager:
        lock = manager.Lock()
        completed_tasks = manager.Value('i', 0)
        total_tasks = len(video_list)

        args = [(video, output_dir) for video in video_list]

        with multiprocessing.Pool(
            initializer=init_worker, initargs=(lock, completed_tasks, total_tasks, queue)
        ) as pool:
            pool.map(worker, args)


class AudioExtractorGUI:
    def __init__(self, root):
        """Initialize GUI."""
        self.root = root
        self.root.title("GPU-Based Audio Extractor")
        self.root.geometry("500x300")

        self.video_dir = tk.StringVar()
        self.output_dir = tk.StringVar()

        # UI Input Video Directory
        tk.Label(root, text="Select Video Directory:").pack(pady=5)
        tk.Entry(root, textvariable=self.video_dir, width=50).pack(pady=5)
        tk.Button(root, text="Browse", command=self.select_video_dir).pack(pady=5)

        # UI Output Directory
        tk.Label(root, text="Select Output Directory:").pack(pady=5)
        tk.Entry(root, textvariable=self.output_dir, width=50).pack(pady=5)
        tk.Button(root, text="Browse", command=self.select_output_dir).pack(pady=5)

        # Start button
        tk.Button(root, text="Start GPU Processing", command=self.start_processing).pack(pady=10)

        # Progress bar
        self.progress = tk.DoubleVar()
        tk.Label(root, text="Progress:").pack(pady=5)
        self.progress_bar = tk.Scale(
            root, variable=self.progress, orient="horizontal", length=400, from_=0, to=100
        )
        self.progress_bar.pack(pady=5)

        # Status updates
        self.status_label = tk.Label(root, text="", fg="blue", wraplength=400, justify="left")
        self.status_label.pack(pady=5)

    def select_video_dir(self):
        """Choose video directory."""
        directory = filedialog.askdirectory(title="Select Video Directory")
        if directory:
            self.video_dir.set(directory)

    def select_output_dir(self):
        """Choose output directory."""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir.set(directory)

    def start_processing(self):
        """Start processing with GPU."""
        video_dir = self.video_dir.get()
        output_dir = self.output_dir.get()

        if not video_dir or not output_dir:
            messagebox.showerror("Error", "Please select input and output directories.")
            return

        video_files = [
            os.path.join(video_dir, f)
            for f in os.listdir(video_dir)
            if f.lower().endswith((".mp4", ".avi", ".mov", ".mkv"))
        ]

        if not video_files:
            messagebox.showerror("Error", "No video files found in selected directory.")
            return

        # Status & Queue setup
        self.queue = multiprocessing.Queue()
        threading.Thread(target=self.process_videos_thread, args=(video_files, output_dir)).start()
        self.root.after(100, self.update_progress)

    def process_videos_thread(self, video_files, output_dir):
        """Handle the worker logic."""
        try:
            process_videos(video_files, output_dir, self.queue)
            self.queue.put("DONE")
        except Exception as e:
            self.queue.put(f"ERROR: {e}")

    def update_progress(self):
        """Update GUI progress from multiprocessing feedback."""
        while not self.queue.empty():
            message = self.queue.get()
            if isinstance(message, str):
                if message == "DONE":
                    self.status_label.config(text="Processing complete.")
                    self.progress.set(100)
            elif isinstance(message, tuple):
                progress, status = message
                self.progress.set(progress)
                self.status_label.config(text=status)

        self.root.after(100, self.update_progress)


# Main Application Entry
if __name__ == "__main__":
    root = tk.Tk()
    app = AudioExtractorGUI(root)
    root.mainloop()
