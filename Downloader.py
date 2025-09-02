#!/usr/bin/env python3

import os
import subprocess

# PREDEFINED SETTINGS - EDIT THESE VALUES
FOLDER_NAME = "downloaded_videos"  # Change to your preferred folder name
PLAYLIST_URL = "https://youtube.com/playlist?list=YOUR_PLAYLIST_ID"  # Replace with your playlist URL
RESOLUTION = "720p"  # Change to desired resolution (360p, 480p, 720p, 1080p, etc.)
PLAYBACK_SPEED = "1.0"  # Change to desired speed (1.0 for normal, 1.25 for 1.25x, etc.)

def main():
    # Create the folder if it doesn't exist
    if not os.path.exists(FOLDER_NAME):
        os.makedirs(FOLDER_NAME)

    # Download command
    download_command = [
        "yt-dlp",
        "--output", f"{FOLDER_NAME}/%(title)s.%(ext)s",
        "--format", f"bv*[ext=mp4][vcodec=h264][height<={RESOLUTION}]+ba[ext=m4a]/b[ext=mp4]",
        "--merge-output-format", "mp4",
        PLAYLIST_URL
    ]

    try:
        print("Downloading videos...")
        subprocess.run(download_command, check=True)
        print("Download completed.")
        
        # If playback speed is not default, process each video
        if PLAYBACK_SPEED != "1.0":
            speed_factor = float(PLAYBACK_SPEED)
            pts_factor = 1.0 / speed_factor
            
            print("Adjusting playback speed...")
            
            # Process each MP4 file in the folder
            for filename in os.listdir(FOLDER_NAME):
                if filename.endswith(".mp4"):
                    input_path = os.path.join(FOLDER_NAME, filename)
                    temp_path = os.path.join(FOLDER_NAME, "temp_" + filename)
                    
                    # Apply speed adjustment with ffmpeg
                    ffmpeg_command = [
                        "ffmpeg",
                        "-i", input_path,
                        "-filter:v", f"setpts={pts_factor}*PTS",
                        "-filter:a", f"atempo={speed_factor}",
                        "-c:v", "libx264",
                        "-c:a", "aac",
                        "-b:a", "128k",
                        temp_path,
                        "-y"
                    ]
                    
                    subprocess.run(ffmpeg_command, check=True)
                    
                    # Replace original with processed version
                    os.remove(input_path)
                    os.rename(temp_path, input_path)
                    
                    print(f"Processed: {filename}")
        
        print(f"Playlist downloaded successfully in '{FOLDER_NAME}' folder with playback speed {PLAYBACK_SPEED}x.")
        
    except subprocess.CalledProcessError as e:
        print("An error occurred while processing the videos.")
        print(e)
    except ValueError:
        print("Invalid playback speed value. Please enter a valid number.")

if __name__ == "__main__":
    main()
