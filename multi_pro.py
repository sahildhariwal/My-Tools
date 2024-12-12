import os
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
import multiprocessing


def resize_video(video_path, output_dir, width, height):
    """
    Resizes the video to the specified dimensions using OpenCV and saves it in the given directory.
    """
    try:
        # Open video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return f"Failed to open: {video_path}"
        
        # Set up the video writer
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        video_name = os.path.basename(video_path)
        output_path = os.path.join(output_dir, video_name)

        out = cv2.VideoWriter(output_path, fourcc, cap.get(cv2.CAP_PROP_FPS), (width, height))

        while True:
            ret, frame = cap.read()
            if not ret:
                break  # End of video
            # Resize the frame
            resized_frame = cv2.resize(frame, (width, height))
            # Write resized frame
            out.write(resized_frame)

        # Release resources
        cap.release()
        out.release()
        cv2.destroyAllWindows()

        return f"Processed: {video_path}"
    except Exception as e:
        return f"Failed: {video_path}, Error: {str(e)}"


def worker_process(video_path, output_dir, width, height):
    """
    Worker function for multiprocessing to resize videos concurrently.
    """
    result = resize_video(video_path, output_dir, width, height)
    print(result)  # Log progress


class VideoResizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Frame Resizer")
        self.root.geometry("600x400")

        # Select directory
        tk.Label(root, text="Select Directory with Videos").pack(pady=5)
        self.directory_var = tk.StringVar()
        tk.Entry(root, textvariable=self.directory_var, width=50).pack(pady=5)
        tk.Button(root, text="Select Directory", command=self.select_directory).pack(pady=5)

        # Input Width & Height
        tk.Label(root, text="Enter Target Width and Height").pack(pady=5)
        self.width_var = tk.IntVar(value=640)
        self.height_var = tk.IntVar(value=480)
        tk.Entry(root, textvariable=self.width_var, width=20).pack(side=tk.LEFT, padx=5)
        tk.Entry(root, textvariable=self.height_var, width=20).pack(side=tk.LEFT, padx=5)

        # Process Button
        tk.Button(root, text="Resize Videos", command=self.start_processing).pack(pady=10)

        # Status Label
        self.status_label = tk.Label(root, text="", wraplength=500, justify="left")
        self.status_label.pack(pady=10)

    def select_directory(self):
        """Open a file dialog to select directory."""
        directory = filedialog.askdirectory(title="Select Video Directory")
        if directory:
            self.directory_var.set(directory)

    def start_processing(self):
        """Start resizing videos with multiprocessing."""
        directory = self.directory_var.get()
        if not directory:
            messagebox.showerror("Error", "Please select a directory first.")
            return

        # Validate width and height
        try:
            target_width = self.width_var.get()
            target_height = self.height_var.get()
        except ValueError:
            messagebox.showerror("Error", "Invalid width/height values.")
            return

        # Get video list
        video_files = [
            os.path.join(directory, file)
            for file in os.listdir(directory)
            if file.lower().endswith((".mp4", ".avi", ".mkv", ".mov"))
        ]
        if not video_files:
            messagebox.showerror("Error", "No supported video files found in the directory.")
            return

        # Create output directory
        output_dir = os.path.join(directory, "output")
        os.makedirs(output_dir, exist_ok=True)

        # Start multiprocessing with worker functions
        self.status_label.config(text=f"Processing {len(video_files)} videos...")
        processes = []
        for video_file in video_files:
            process = multiprocessing.Process(
                target=worker_process, args=(video_file, output_dir, target_width, target_height)
            )
            process.start()
            processes.append(process)

        # Wait for all processes to finish
        for process in processes:
            process.join()

        self.status_label.config(
            text=f"Resized {len(video_files)} videos. Output saved in {output_dir}"
        )
        messagebox.showinfo("Done", "All videos have been resized successfully.")


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoResizerApp(root)
    root.mainloop()
