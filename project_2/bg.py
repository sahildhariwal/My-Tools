import os
import subprocess
import multiprocessing
import tkinter as tk
from tkinter import filedialog, messagebox


def get_video_dimensions(video_path):
    """
    Fetch video dimensions using ffprobe to dynamically determine crop logic.
    Args:
        video_path: Path to the input video
    Returns:
        Tuple[int, int]: Actual video width and height
    """
    try:
        # ffprobe command to get video dimensions
        cmd = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height",
            "-of", "csv=p=0",
            video_path,
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        dims = result.stdout.decode('utf-8').strip().split(',')
        width, height = int(dims[0]), int(dims[1])
        print(f"Detected video dimensions for {video_path}: Width={width}, Height={height}")
        return width, height
    except Exception as e:
        print(f"Error fetching dimensions: {e}")
        return None, None


def crop_video(input_path, output_path, crop_width, crop_height, x_offset, y_offset):
    """
    Crop a single video using ffmpeg with GPU acceleration.
    Args:
        input_path: Input video file path
        output_path: Path for saving cropped video
        crop_width: Crop width (in pixels)
        crop_height: Crop height (in pixels)
        x_offset: Horizontal crop offset
        y_offset: Vertical crop offset
    """
    try:
        # Determine actual video dimensions to validate crop params
        actual_width, actual_height = get_video_dimensions(input_path)
        if not actual_width or not actual_height:
            print(f"Invalid video dimensions for {input_path}. Skipping...")
            return False

        # Ensure crop dimensions and offsets fit within video dimensions
        if crop_width + x_offset > actual_width or crop_height + y_offset > actual_height:
            print(f"Crop parameters invalid for {input_path}. Adjusting crop.")
            crop_width = min(crop_width, actual_width - x_offset)
            crop_height = min(crop_height, actual_height - y_offset)

        # FFmpeg command with GPU-based NVENC
        cmd = [
            "ffmpeg",
            "-y",
            "-i", input_path,
            "-filter:v", f"crop={crop_width}:{crop_height}:{x_offset}:{y_offset}",
            "-c:v", "h264_nvenc",  # NVENC GPU encoder
            "-c:a", "copy",
            output_path,
        ]
        print(f"Running command: {' '.join(cmd)}")
        # Run the command
        process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        
        if process.returncode != 0:
            print(f"FFmpeg failed for video: {input_path}")
            print(f"Error Output: {process.stderr.decode('utf-8')}")
            return False

        print(f"Processed and saved video: {output_path}")
        return True

    except Exception as e:
        print(f"Unexpected error processing {input_path}: {e}")
        return False


def worker(args):
    """
    Worker for multiprocessing to handle video cropping.
    Args:
        args: Tuple containing all necessary parameters
    """
    input_file, output_file, crop_width, crop_height, x_offset, y_offset = args
    success = crop_video(input_file, output_file, crop_width, crop_height, x_offset, y_offset)
    if success:
        print(f"[SUCCESS]: {os.path.basename(input_file)} cropped successfully.")
    else:
        print(f"[FAILURE]: Could not crop {os.path.basename(input_file)}")


class VideoCropApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GPU-Accelerated Bulk Video Cropper")
        self.root.geometry("700x500")

        # UI Elements
        tk.Label(root, text="Select Input Directory with Videos").pack(pady=5)
        self.input_dir_var = tk.StringVar()
        tk.Entry(root, textvariable=self.input_dir_var, width=50).pack(pady=5)
        tk.Button(root, text="Select Directory", command=self.select_directory).pack(pady=5)

        # Crop settings UI
        tk.Label(root, text="Set Crop Dimensions").pack(pady=5)

        tk.Label(root, text="Width").pack(pady=2)
        self.crop_width_var = tk.IntVar(value=1280)
        tk.Entry(root, textvariable=self.crop_width_var).pack(pady=2)

        tk.Label(root, text="Height").pack(pady=2)
        self.crop_height_var = tk.IntVar(value=720)
        tk.Entry(root, textvariable=self.crop_height_var).pack(pady=2)

        tk.Label(root, text="Horizontal Offset").pack(pady=2)
        self.x_offset_var = tk.IntVar(value=0)
        tk.Entry(root, textvariable=self.x_offset_var).pack(pady=2)

        tk.Label(root, text="Vertical Offset").pack(pady=2)
        self.y_offset_var = tk.IntVar(value=0)
        tk.Entry(root, textvariable=self.y_offset_var).pack(pady=2)

        tk.Button(root, text="Start Cropping", command=self.start_cropping).pack(pady=10)

    def select_directory(self):
        """Opens file dialog for directory selection."""
        directory = filedialog.askdirectory(title="Select Directory")
        if directory:
            self.input_dir_var.set(directory)

    def start_cropping(self):
        """Start the video cropping process using multiprocessing."""
        input_dir = self.input_dir_var.get()
        if not input_dir:
            messagebox.showerror("Error", "Please select a directory first.")
            return

        video_files = [
            os.path.join(input_dir, f)
            for f in os.listdir(input_dir)
            if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov'))
        ]

        if not video_files:
            messagebox.showerror("Error", "No valid video files found in directory.")
            return

        # Create output directory
        output_dir = os.path.join(input_dir, "cropped_videos")
        os.makedirs(output_dir, exist_ok=True)

        # Prepare arguments for worker
        args = [
            (
                video_file,
                os.path.join(output_dir, os.path.basename(video_file)),
                self.crop_width_var.get(),
                self.crop_height_var.get(),
                self.x_offset_var.get(),
                self.y_offset_var.get()
            )
            for video_file in video_files
        ]

        # Multiprocessing Pool
        with multiprocessing.Pool() as pool:
            pool.map(worker, args)

        messagebox.showinfo("Completed", "Cropping completed successfully.")


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoCropApp(root)
    root.mainloop()
