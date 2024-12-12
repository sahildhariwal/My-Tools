import os

def rename_videos_in_folder(folder_path, new_name="Day", extensions=None):
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
    for idx, file_name in enumerate(video_files, start=1):
        old_path = os.path.join(folder_path, file_name)
        new_file_name = f"{new_name}_{idx}{os.path.splitext(file_name)[1]}"
        new_path = os.path.join(folder_path, new_file_name)

        os.rename(old_path, new_path)
        print(f"Renamed: '{file_name}' -> '{new_file_name}'")

    print("Renaming completed!")

# Example usage:
# Replace 'your_folder_path_here' with the path to the folder containing your videos.
folder_path = "C:/Users/sahil/Downloads/video tools/videos/sana"
rename_videos_in_folder(folder_path)
