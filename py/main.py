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
    return title.strip()

def download_and_merge(url: str, output_path: str = '.'):
    """
    Downloads the best quality video and audio from a YouTube URL,
    merges them with ffmpeg, and cleans up temporary files.
    """
    # Initialize temp file paths to None for proper cleanup
    video_temp_file = None
    audio_temp_file = None
    
    try:
        print(f"Processing URL: {url}")
        
        # Create temporary filenames first
        video_temp_file = os.path.join(output_path, "video_temp.mp4")
        audio_temp_file = os.path.join(output_path, "audio_temp.mp4")
        
        # Try to create YouTube object with error handling
        try:
            yt = YouTube(url, on_progress_callback=on_progress)
            video_title = yt.title
        except Exception as e:
            print(f"Failed to access video information: {e}")
            # Fallback: extract video ID from URL for filename
            video_id = url.split('watch?v=')[-1].split('&')[0] if 'watch?v=' in url else 'video'
            video_title = f"video_{video_id}"
            # Try to create YouTube object without progress callback
            yt = YouTube(url)

        # Get video title and create safe filename
        safe_title = sanitize_filename(video_title)
        if not safe_title:  # If title becomes empty after sanitization
            safe_title = "video_download"
        
        final_filename = os.path.join(output_path, f"{safe_title}.mp4")
        
        # Handle case where file already exists
        counter = 1
        original_filename = final_filename
        while os.path.exists(final_filename):
            name, ext = os.path.splitext(original_filename)
            final_filename = f"{name}_{counter}{ext}"
            counter += 1

        # Get the best streams
        print("Getting video streams...")
        video_stream = yt.streams.filter(
            adaptive=True, file_extension='mp4', only_video=True
        ).order_by('resolution').desc().first()
        
        print("Getting audio streams...")
        audio_stream = yt.streams.filter(
            adaptive=True, file_extension='mp4', only_audio=True
        ).order_by('abr').desc().first()

        if not video_stream:
            print(f"Could not find suitable video stream for {url}")
            return
        
        if not audio_stream:
            print(f"Could not find suitable audio stream for {url}")
            return

        # Download the streams
        print(f"Downloading video: '{safe_title}' ({video_stream.resolution})")
        try:
            video_stream.download(output_path=output_path, filename="video_temp.mp4")
        except Exception as e:
            print(f"Failed to download video stream: {e}")
            return

        print(f"Downloading audio: '{safe_title}' ({audio_stream.abr})")
        try:
            audio_stream.download(output_path=output_path, filename="audio_temp.mp4")
        except Exception as e:
            print(f"Failed to download audio stream: {e}")
            return

        # Verify both files were downloaded
        if not os.path.exists(video_temp_file):
            print("Video file was not downloaded successfully")
            return
        
        if not os.path.exists(audio_temp_file):
            print("Audio file was not downloaded successfully")
            return

        # Merge using FFmpeg
        print("Merging video and audio with FFmpeg...")
        command = [
            'ffmpeg',
            '-i', video_temp_file,
            '-i', audio_temp_file,
            '-c:v', 'copy',
            '-c:a', 'copy',
            '-y',  # Overwrite output file if it exists
            final_filename
        ]
        
        # Use subprocess.run for better error handling
        result = subprocess.run(command, check=True, capture_output=True, text=True)

        print(f"Successfully created: '{final_filename}'")

    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error while processing {url}: {e}")
        print("FFmpeg stderr:", e.stderr)
    except Exception as e:
        print(f"An error occurred while processing {url}: {e}")

    finally:
        # Clean up temporary files (only if they were defined)
        print("Cleaning up temporary files...")
        if video_temp_file and os.path.exists(video_temp_file):
            try:
                os.remove(video_temp_file)
                print("Removed video temp file")
            except Exception as e:
                print(f"Failed to remove video temp file: {e}")
        
        if audio_temp_file and os.path.exists(audio_temp_file):
            try:
                os.remove(audio_temp_file)
                print("Removed audio temp file")
            except Exception as e:
                print(f"Failed to remove audio temp file: {e}")

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
        
        successful_downloads = 0
        failed_downloads = 0
        
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] Processing: {url}")
            try:
                download_and_merge(url, output_path=output_dir)
                successful_downloads += 1
            except Exception as e:
                print(f"Failed to process {url}: {e}")
                failed_downloads += 1
            
            print("-" * 50)
        
        print(f"\nDownload summary:")
        print(f"Successful: {successful_downloads}")
        print(f"Failed: {failed_downloads}")
        print("All downloads complete.")
        
    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting...")
        return
    
    except Exception as e:
        print(f"An error occurred in main: {e}")
        return

if __name__ == "__main__":
    main()