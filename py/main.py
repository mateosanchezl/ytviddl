import os
import subprocess
import shutil
from pytubefix import YouTube
from pytubefix.cli import on_progress

def sanitize_filename(title: str) -> str:
    """Removes characters that are invalid for file names."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        title = title.replace(char, '')
    return title

def download_and_merge(url: str, output_path: str = '.'):
    """
    Downloads the best quality video and audio from a YouTube URL,
    merges them with ffmpeg, and cleans up temporary files.
    """
    try:
        print(f"Processing URL: {url}")
        yt = YouTube(url, on_progress_callback=on_progress)

        # 1. Get video title and create safe filename
        video_title = sanitize_filename(yt.title)
        final_filename = os.path.join(output_path, f"{video_title}.mp4")
        
        # Temporary filenames
        video_temp_file = os.path.join(output_path, "video_temp.mp4")
        audio_temp_file = os.path.join(output_path, "audio_temp.mp4")

        # 2. Get the best streams
        video_stream = yt.streams.filter(
            adaptive=True, file_extension='mp4', only_video=True
        ).order_by('resolution').desc().first()
        
        audio_stream = yt.streams.filter(
            adaptive=True, file_extension='mp4', only_audio=True
        ).order_by('abr').desc().first()

        if not video_stream or not audio_stream:
            print(f"Could not find suitable video/audio streams for {url}")
            return

        # 3. Download the streams
        print(f"Downloading video: '{yt.title}' ({video_stream.resolution})")
        video_stream.download(output_path=output_path, filename="video_temp.mp4")

        print(f"Downloading audio: '{yt.title}' ({audio_stream.abr})")
        audio_stream.download(output_path=output_path, filename="audio_temp.mp4")

        # 4. Merge using FFmpeg
        print("Merging video and audio with FFmpeg...")
        command = [
            'ffmpeg',
            '-i', video_temp_file,
            '-i', audio_temp_file,
            '-c:v', 'copy',
            '-c:a', 'copy',
            final_filename
        ]
        
        # Use subprocess.run for better error handling
        result = subprocess.run(command, check=True, capture_output=True, text=True)

        print(f"Successfully created: '{final_filename}'")

    except Exception as e:
        print(f"An error occurred while processing {url}: {e}")
        if isinstance(e, subprocess.CalledProcessError):
            print("FFmpeg Error:", e.stderr)

    finally:
        # 5. Clean up temporary files
        print("Cleaning up temporary files...")
        if os.path.exists(video_temp_file):
            os.remove(video_temp_file)
        if os.path.exists(audio_temp_file):
            os.remove(audio_temp_file)

def main():
    """Main function to run the script."""
    try:
        # Check if FFmpeg is installed and accessible
        if not shutil.which("ffmpeg"):
            print("Error: FFmpeg is not installed or not found in your system's PATH.")
            print("Please install FFmpeg to run this script.")
            return

        # Check for the urls file
        urls_file = 'links.txt'
        if not os.path.exists(urls_file):
            print(f"Error: The file '{urls_file}' was not found.")
            print("Please create it and add YouTube URLs, one per line.")
            return

        # Create an output directory for the videos
        output_dir = "./vids"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(urls_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]

        print(f"Found {len(urls)} URL(s) to process.")
        for url in urls:
            download_and_merge(url, output_path=output_dir)
            print("-" * 40)
        
        print("All downloads complete.")
        
    except KeyboardInterrupt:
        print("Interrupted by user. Exiting...")
        print("Cleaning up...")
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
            
        print("Last URL processed: ", url)
        return
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return
    


if __name__ == "__main__":
    main()