import { useState, useEffect } from "react";
import "./App.css";

interface DownloadStatus {
  status: "downloading" | "completed" | "error" | "not_found";
  progress: number;
  message: string;
}

interface Video {
  filename: string;
  size: number;
  size_mb: number;
}

function App() {
  const [url, setUrl] = useState("");
  const [downloadPath, setDownloadPath] = useState("./vids");
  const [downloadId, setDownloadId] = useState<string | null>(null);
  const [downloadStatus, setDownloadStatus] = useState<DownloadStatus | null>(null);
  const [videos, setVideos] = useState<Video[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const API_BASE = "http://localhost:5000/api";

  // Fetch videos list
  const fetchVideos = async () => {
    try {
      const response = await fetch(`${API_BASE}/videos?path=${encodeURIComponent(downloadPath)}`);
      const data = await response.json();
      setVideos(data);
    } catch (error) {
      console.error("Error fetching videos:", error);
    }
  };

  // Check download status
  const checkDownloadStatus = async (id: string) => {
    try {
      const response = await fetch(`${API_BASE}/status/${id}`);
      const status = await response.json();
      setDownloadStatus(status);

      if (status.status === "completed" || status.status === "error") {
        setDownloadId(null);
        fetchVideos(); // Refresh video list
      }
    } catch (error) {
      console.error("Error checking download status:", error);
    }
  };

  // Poll download status
  useEffect(() => {
    if (downloadId) {
      const interval = setInterval(() => {
        checkDownloadStatus(downloadId);
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [downloadId]);

  // Initial fetch
  useEffect(() => {
    fetchVideos();
  }, []);

  const handleDownload = async () => {
    if (!url.trim()) {
      alert("Please enter a YouTube URL");
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/download`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          url: url.trim(),
          output_path: downloadPath,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setDownloadId(data.download_id);
        setUrl(""); // Clear URL after successful start
      } else {
        alert(data.error || "Failed to start download");
      }
    } catch (error) {
      alert("Error connecting to server. Make sure the Python API is running.");
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "downloading":
        return "#f39c12";
      case "completed":
        return "#27ae60";
      case "error":
        return "#e74c3c";
      default:
        return "#95a5a6";
    }
  };

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1>🎥 YouTube Video Downloader</h1>
          <p>Download YouTube videos with high quality</p>
        </header>

        <div className="download-section">
          <div className="input-group">
            <label htmlFor="url">YouTube URL:</label>
            <input
              id="url"
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://www.youtube.com/watch?v=..."
              disabled={isLoading}
            />
          </div>

          <div className="input-group">
            <label htmlFor="path">Download Path:</label>
            <input
              id="path"
              type="text"
              value={downloadPath}
              onChange={(e) => setDownloadPath(e.target.value)}
              placeholder="./vids"
              disabled={isLoading}
            />
          </div>

          <button
            onClick={handleDownload}
            disabled={isLoading || !url.trim()}
            className="download-btn"
          >
            {isLoading ? "Starting Download..." : "Download Video"}
          </button>
        </div>

        {downloadStatus && (
          <div className="status-section">
            <h3>Download Status</h3>
            <div
              className="status-indicator"
              style={{ color: getStatusColor(downloadStatus.status) }}
            >
              <div className="status-message">{downloadStatus.message}</div>
              {downloadStatus.status === "downloading" && (
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{ width: `${downloadStatus.progress}%` }}
                  ></div>
                </div>
              )}
            </div>
          </div>
        )}

        <div className="videos-section">
          <div className="section-header">
            <h3>Downloaded Videos</h3>
            <button onClick={fetchVideos} className="refresh-btn">
              🔄 Refresh
            </button>
          </div>

          {videos.length === 0 ? (
            <p className="no-videos">No videos downloaded yet</p>
          ) : (
            <div className="videos-list">
              {videos.map((video, index) => (
                <div key={index} className="video-item">
                  <div className="video-info">
                    <span className="video-name">{video.filename}</span>
                    <span className="video-size">{video.size_mb} MB</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
