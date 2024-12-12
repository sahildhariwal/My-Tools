import os
import ctypes
import win32api
import win32security
import win32file

# Define function to unblock files
def unblock_file(file_path):
    """Unblocks a single file by removing the 'mark of the web.'"""
    try:
        # Remove the Zone.Identifier stream
        zone_identifier_path = file_path + ":Zone.Identifier"
        if os.path.exists(zone_identifier_path):
            os.remove(zone_identifier_path)
            print(f"Unblocked: {file_path}")
        else:
            print(f"File is not blocked: {file_path}")
    except Exception as e:
        print(f"Error unblocking file {file_path}: {e}")


def unblock_videos_in_directory(directory):
    """Unblocks all video files in the given directory and its subdirectories."""
    video_extensions = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"}

    for root, _, files in os.walk(directory):
        for file in files:
            if os.path.splitext(file)[1].lower() in video_extensions:
                file_path = os.path.join(root, file)
                unblock_file(file_path)


if __name__ == "__main__":
    directory_to_unblock = input("Enter the directory containing video files to unblock: ").strip()

    if os.path.exists(directory_to_unblock):
        print("Starting to unblock video files...")
        unblock_videos_in_directory(directory_to_unblock)
        print("Unblocking complete.")
    else:
        print("Error: The specified directory does not exist.")
