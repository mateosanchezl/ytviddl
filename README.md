# YouTube Video Downloader

A beautiful web application for downloading YouTube videos with high quality. Built with React frontend and Python Flask backend.

## Features

- 🎥 Download YouTube videos in high quality
- 📁 Customizable download path
- 📊 Real-time download progress tracking
- 🚫 Cancel downloads in progress
- 📋 List of downloaded videos with file sizes
- 🎨 Modern, responsive UI
- ⚡ Fast and efficient downloads
- 🔄 Download queue management

## Prerequisites

- Python 3.7+
- Node.js 16+
- FFmpeg (for video processing)

### Installing FFmpeg

**macOS:**

```bash
brew install ffmpeg
```

**Ubuntu/Debian:**

```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
Download from [FFmpeg official website](https://ffmpeg.org/download.html)

## Quick Start (Automated Setup)

We've created a bash script that automates the entire setup process:

```bash
# Make the script executable
chmod +x setup_and_run.sh

# Run the setup and start both servers
./setup_and_run.sh
```

This script will:

1. Install Python dependencies
2. Install Node.js dependencies
3. Start the Python backend server
4. Start the React frontend server
5. Open your browser to the application

## Manual Setup

### 1. Backend Setup

Navigate to the Python backend directory:

```bash
cd py
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Start the Flask API server:

```bash
python api.py
```

The API will be available at `http://localhost:5000`

### 2. Frontend Setup

In a new terminal, navigate to the frontend directory:

```bash
cd front
```

Install Node.js dependencies:

```bash
npm install
```

Start the React development server:

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

## Usage

1. Open your browser and go to `http://localhost:5173`
2. Paste a YouTube URL in the input field
3. (Optional) Change the download path (default: `./vids`)
4. Click "add" or press Enter to add to download queue
5. Monitor download progress in real-time
6. Cancel downloads if needed using the "cancel" button
7. View your downloaded videos in the list below

### Download Queue Features

- **Add Multiple Downloads**: Paste URLs and add them to the queue
- **Cancel Downloads**: Cancel any download in progress
- **Progress Tracking**: Real-time progress bars and status messages
- **Queue Management**: Remove completed downloads or clear the entire queue
- **Auto-paste Detection**: Automatically starts download when pasting a YouTube URL

## API Endpoints

- `POST /api/download` - Start a video download
- `POST /api/cancel/<download_id>` - Cancel a download in progress
- `GET /api/status/<download_id>` - Get download status
- `GET /api/videos` - List downloaded videos

## Project Structure

```
ytviddl/
├── py/                    # Python backend
│   ├── api.py            # Flask API server with cancellation support
│   ├── main.py           # YouTube download logic
│   ├── requirements.txt  # Python dependencies
│   └── links.txt         # Sample URLs
├── front/                # React frontend
│   ├── src/
│   │   ├── App.tsx       # Main application component
│   │   └── App.css       # Styling
│   └── package.json      # Node.js dependencies
├── setup_and_run.sh      # Automated setup and run script
└── README.md             # This file
```

## Troubleshooting

### Common Issues

1. **FFmpeg not found**: Make sure FFmpeg is installed and in your system PATH
2. **CORS errors**: The Flask API includes CORS headers, but ensure both servers are running
3. **Download fails**: Check that the YouTube URL is valid and the video is available
4. **Permission errors**: Ensure the download directory is writable
5. **Port conflicts**: Make sure ports 5000 (backend) and 5173 (frontend) are available

### Error Messages

- "Error connecting to server": Make sure the Python API is running on port 5000
- "FFmpeg is not installed": Install FFmpeg following the instructions above
- "URL is required": Enter a valid YouTube URL
- "Download cancelled": The download was manually cancelled by the user

### Cancellation Feature

The app now supports cancelling downloads in progress:

- Click the "cancel" button next to any downloading item
- The download will be stopped and temporary files cleaned up
- Cancelled downloads show "cancelled" status
- You can remove cancelled downloads from the queue

## License

This project is for educational purposes. Please respect YouTube's terms of service and copyright laws.

## Contributing

Feel free to submit issues and enhancement requests!
