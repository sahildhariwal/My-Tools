import os
import subprocess
from textwrap import wrap
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.config import change_settings

# Configure ImageMagick binary path
change_settings({"IMAGEMAGICK_BINARY": r"C:/Program Files/ImageMagick/magick.exe"})

def add_padding_and_text(
    input_folder,
    output_folder,
    text_file,
    padding,
    heading_font="Arial",
    heading_font_size=50,
    heading_color="red",
    heading_position_offset=0,
    text_font="Arial",
    text_font_size=40,
    text_color="black",
    text_position_offset=20,
    heading="Video Heading",
):
    """
    Add padding and overlay text at the top of videos with adjustable text properties.

    Args:
        input_folder (str): Path to the folder containing input videos.
        output_folder (str): Path to the folder for saving processed videos.
        text_file (str): Path to the text file containing overlay text lines.
        padding (dict): Padding for top, bottom, left, and right as fractions of video dimensions.
        heading_font (str): Font family for the heading.
        heading_font_size (int): Font size for the heading.
        heading_color (str): Color for the heading text.
        heading_position_offset (int): Vertical adjustment for the heading in pixels.
        text_font (str): Font family for the wrapped text.
        text_font_size (int): Font size for the wrapped text.
        text_color (str): Color for the wrapped text.
        text_position_offset (int): Vertical adjustment for the wrapped text in pixels.
        heading (str): Static heading text to display above the video.
    """
    with open(text_file, "r", encoding="utf-8") as file:
        text_lines = file.readlines()

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for index, filename in enumerate(os.listdir(input_folder)):
        if filename.endswith((".mp4", ".avi", ".mkv", ".mov")):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, f"{filename}")
            print(f"\n[INFO] Processing video: {filename} ({index + 1}/{len(os.listdir(input_folder))})")

            video = VideoFileClip(input_path)
            width, height = video.size
            top_padding = int(height * padding['top'])
            bottom_padding = int(height * padding['bottom'])
            side_padding = int(width * padding['left'])

            print(f"  [STEP 2] Calculated padding sizes - Top: {top_padding}px, Bottom: {bottom_padding}px, Side Padding: {side_padding}px")

            # Create a blank area above the video for text
            text_height = heading_font_size * 3  # Approximate height for heading and text
            padded_video = video.margin(top=top_padding + text_height, bottom=bottom_padding, left=side_padding, right=side_padding, color=(255, 255, 255))

            # Get the text for this video
            text = text_lines[index].strip() if index < len(text_lines) else "No Text Available"
            wrapped_text = "\n".join(wrap(text, width=50))  # Wrap text at word boundaries
            print(f"  [STEP 4] Selected text for overlay:\n{wrapped_text}")

            # Create heading text clip with manual adjustment
            heading_clip = TextClip(
                heading, fontsize=heading_font_size, color=heading_color, font=heading_font, size=(width, None)
            )
            heading_clip = heading_clip.set_duration(video.duration).set_position(
                ("center", top_padding // 2 - heading_font_size + heading_position_offset)
            )

            # Create wrapped text clip (placed below heading)
            text_clip = TextClip(
                wrapped_text, fontsize=text_font_size, color=text_color, font=text_font, size=(width - 40, None)
            )
            text_clip = text_clip.set_duration(video.duration).set_position(
                ("center", top_padding // 2 + heading_font_size + text_position_offset)
            )

            # Combine the text clips and video
            final_video = CompositeVideoClip([padded_video, heading_clip, text_clip])

            print(f"  [STEP 6] Writing processed video to: {output_path}")
            final_video.write_videofile(output_path, codec='libx264', audio_codec='aac')

            print(f"[SUCCESS] Video processed and saved as: {output_path}")

    print("\n[COMPLETED] All videos have been processed!")


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

    video_files = [f for f in os.listdir(folder_path) if os.path.splitext(f)[1].lower() in extensions]

    for idx, file_name in enumerate(video_files, start=1):
        old_path = os.path.join(folder_path, file_name)
        new_file_name = f"{new_name}_{idx}{os.path.splitext(file_name)[1]}"
        new_path = os.path.join(folder_path, new_file_name)

        os.rename(old_path, new_path)
        print(f"Renamed: '{file_name}' -> '{new_file_name}'")

    print("Renaming completed!")


def remove_metadata_in_place(folder_path, extensions=None):
    """
    Removes metadata from all video files in a folder and overwrites the original files.

    Args:
    folder_path (str): Path to the folder containing videos.
    extensions (list): List of video file extensions to consider. If None, defaults to common video extensions.
    """
    if extensions is None:
        extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm']

    video_files = [f for f in os.listdir(folder_path) if os.path.splitext(f)[1].lower() in extensions]

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

        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.replace(temp_output_path, input_path)
        print(f"Metadata removed: '{file_name}'")

    print("Metadata removal completed!")


# Combined Workflow
folder_path = "C:/Users/sahil/Downloads/video tools/output set 1"
text_file = "C:/Users/sahil/Downloads/video tools/text line/english.txt"

# Step 1: Add padding and text to videos
add_padding_and_text(
    input_folder="C:/Users/sahil/Downloads/video tools/videos/input",
    output_folder=folder_path,
    text_file=text_file,
    padding={'top': 0.1, 'bottom': 0.05, 'left': 0.05, 'right': 0.05},
    heading_font="Comic-Sans-MS",
    heading_font_size=30,
    heading_color="blue",
    heading_position_offset=-40,
    text_font="Comic-Sans-MS",
    text_font_size=20,
    text_color="black",
    text_position_offset=40,
    heading="Did You Know?"
)

# Step 2: Rename the videos
rename_videos_in_folder(folder_path)

# Step 3: Remove metadata from the renamed videos
remove_metadata_in_place(folder_path)
