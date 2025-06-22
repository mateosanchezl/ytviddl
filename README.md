# YouTube Video Downloader

A beautiful web application for downloading YouTube videos with high quality. Built with React frontend and Python Flask backend.

## Features

- 🎥 Download YouTube videos in high quality
- 📁 Customizable download path
- 📊 Real-time download progress tracking
- 📋 List of downloaded videos with file sizes
- 🎨 Modern, responsive UI
- ⚡ Fast and efficient downloads

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

## Setup

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
4. Click "Download Video"
5. Monitor the download progress in real-time
6. View your downloaded videos in the list below

## API Endpoints

- `POST /api/download` - Start a video download
- `GET /api/status/<download_id>` - Get download status
- `GET /api/videos` - List downloaded videos

## Project Structure

```
ytviddl/
├── py/                    # Python backend
│   ├── api.py            # Flask API server
│   ├── main.py           # YouTube download logic
│   ├── requirements.txt  # Python dependencies
│   └── links.txt         # Sample URLs
└── front/                # React frontend
    ├── src/
    │   ├── App.tsx       # Main application component
    │   └── App.css       # Styling
    └── package.json      # Node.js dependencies
```

## Troubleshooting

### Common Issues

1. **FFmpeg not found**: Make sure FFmpeg is installed and in your system PATH
2. **CORS errors**: The Flask API includes CORS headers, but ensure both servers are running
3. **Download fails**: Check that the YouTube URL is valid and the video is available
4. **Permission errors**: Ensure the download directory is writable

### Error Messages

- "Error connecting to server": Make sure the Python API is running on port 5000
- "FFmpeg is not installed": Install FFmpeg following the instructions above
- "URL is required": Enter a valid YouTube URL

## License

This project is for educational purposes. Please respect YouTube's terms of service and copyright laws.

## Contributing

Feel free to submit issues and enhancement requests!
