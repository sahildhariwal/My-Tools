import os
import subprocess

def rename_videos_in_folder(folder_path, new_name="Day ", extensions=None):
    """
    Rename all video files in the specified folder.

    Args:
    folder_path (str): Path to the folder containing videos.
    new_name (str): Base name for the videos.
    extensions (list): List of video file extensions to consider. If None, defaults to common video extensions.
    """
    if extensions is None:
        extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm']

    # Ensure folder exists
    if not os.path.exists(folder_path):
        print(f"Folder '{folder_path}' does not exist.")
        return

    # Get list of video files
    video_files = [f for f in os.listdir(folder_path) if os.path.splitext(f)[1].lower() in extensions]

    if not video_files:
        print("No video files found in the folder.")
        return

    # Rename files
    renamed_files = []
    for idx, file_name in enumerate(video_files, start=1):
        old_path = os.path.join(folder_path, file_name)
        new_file_name = f"{new_name}_{idx}{os.path.splitext(file_name)[1]}"
        new_path = os.path.join(folder_path, new_file_name)

        os.rename(old_path, new_path)
        print(f"Renamed: '{file_name}' -> '{new_file_name}'")
        renamed_files.append(new_file_name)

    print("Renaming completed!")
    return renamed_files


def remove_metadata_in_place(folder_path, extensions=None):
    """
    Removes metadata from all video files in a folder and overwrites the original files.

    Args:
    folder_path (str): Path to the folder containing videos.
    extensions (list): List of video file extensions to consider. If None, defaults to common video extensions.
    """
    if extensions is None:
        extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm']

    # Ensure input folder exists
    if not os.path.exists(folder_path):
        print(f"Folder '{folder_path}' does not exist.")
        return

    # Get list of video files
    video_files = [f for f in os.listdir(folder_path) if os.path.splitext(f)[1].lower() in extensions]

    if not video_files:
        print("No video files found in the folder.")
        return

    # Process each video file
    for file_name in video_files:
        input_path = os.path.join(folder_path, file_name)
        temp_output_path = os.path.join(folder_path, f"temp_{file_name}")

        # Use FFmpeg to remove metadata
        command = [
            "ffmpeg", "-i", input_path,  # Input file
            "-map", "0",                # Copy all streams (audio, video, etc.)
            "-map_metadata", "-1",      # Remove metadata
            "-c", "copy",               # Copy codec (no re-encoding)
            temp_output_path            # Temporary output file
        ]

        try:
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            os.replace(temp_output_path, input_path)  # Replace the original file with the temp file
            print(f"Metadata removed: '{file_name}'")
        except subprocess.CalledProcessError as e:
            print(f"Error processing '{file_name}': {e}")

    print("Metadata removal completed!")


# Combined Workflow
folder_path = "C:/Users/sahil/Downloads/video tools/videos/sana"  # Path to the folder with videos

# Step 1: Rename the videos
renamed_files = rename_videos_in_folder(folder_path)

# Step 2: Remove metadata from the renamed videos in place
remove_metadata_in_place(folder_path)
