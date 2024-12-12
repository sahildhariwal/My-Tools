import os
import subprocess

def remove_metadata(folder_path, output_folder):
    """
    Removes metadata from all video files in a folder.

    Args:
    folder_path (str): Path to the folder containing videos.
    output_folder (str): Path to the folder where processed videos will be saved.
    """
    # Ensure input folder exists
    if not os.path.exists(folder_path):
        print(f"Folder '{folder_path}' does not exist.")
        return

    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Get list of video files
    video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm']
    video_files = [f for f in os.listdir(folder_path) if os.path.splitext(f)[1].lower() in video_extensions]

    if not video_files:
        print("No video files found in the folder.")
        return

    # Process each video file
    for file_name in video_files:
        input_path = os.path.join(folder_path, file_name)
        output_path = os.path.join(output_folder, file_name)

        # Use FFmpeg to remove metadata
        command = [
            "ffmpeg", "-i", input_path,  # Input file
            "-map", "0",                # Copy all streams (audio, video, etc.)
            "-map_metadata", "-1",      # Remove metadata
            "-c", "copy",               # Copy codec (no re-encoding)
            output_path                 # Output file
        ]

        try:
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"Metadata removed: '{file_name}'")
        except subprocess.CalledProcessError as e:
            print(f"Error processing '{file_name}': {e}")

    print("Metadata removal completed!")

# Example usage
folder_path = "C:/Users/sahil/Downloads/video tools/videos/sana9_8_"  # Path to the folder with original videos
output_folder = "C:/Users/sahil/Downloads/video tools/videos/sana"   # Path to save videos without metadata
remove_metadata(folder_path, output_folder)
