import { useState, useEffect } from "react";

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

interface QueueItem {
  id: string;
  url: string;
  status: DownloadStatus;
}

function App() {
  const [url, setUrl] = useState("");
  const [downloadPath, setDownloadPath] = useState("./vids");
  const [downloadQueue, setDownloadQueue] = useState<QueueItem[]>([]);
  const [videos, setVideos] = useState<Video[]>([]);

  const API_BASE = "http://127.0.0.1:5000/api";

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

  // Check download status for a specific item
  const checkDownloadStatus = async (id: string) => {
    try {
      const response = await fetch(`${API_BASE}/status/${id}`);
      const status = await response.json();

      setDownloadQueue((prev) => prev.map((item) => (item.id === id ? { ...item, status } : item)));

      if (status.status === "completed" || status.status === "error") {
        fetchVideos();
      }
    } catch (error) {
      console.error("Error checking download status:", error);
    }
  };

  // Poll download status for all active downloads
  useEffect(() => {
    const activeDownloads = downloadQueue.filter((item) => item.status.status === "downloading");

    if (activeDownloads.length > 0) {
      const interval = setInterval(() => {
        activeDownloads.forEach((item) => {
          checkDownloadStatus(item.id);
        });
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [downloadQueue]);

  // Initial fetch
  useEffect(() => {
    fetchVideos();
  }, []);

  const addToQueue = () => {
    const trimmedUrl = url.trim();
    if (!trimmedUrl) return;

    // Check if URL already exists in queue
    const exists = downloadQueue.some((item) => item.url === trimmedUrl);
    if (exists) {
      setUrl("");
      return;
    }

    const newItem: QueueItem = {
      id: Date.now().toString(),
      url: trimmedUrl,
      status: {
        status: "downloading",
        progress: 0,
        message: "queued...",
      },
    };

    setDownloadQueue((prev) => [...prev, newItem]);
    setUrl("");
    startDownload(newItem);
  };

  const startDownload = async (item: QueueItem) => {
    try {
      const response = await fetch(`${API_BASE}/download`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          url: item.url,
          output_path: downloadPath,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        // Update the queue item with the actual download ID
        setDownloadQueue((prev) =>
          prev.map((queueItem) =>
            queueItem.id === item.id ? { ...queueItem, id: data.download_id } : queueItem
          )
        );
      } else {
        setDownloadQueue((prev) =>
          prev.map((queueItem) =>
            queueItem.id === item.id
              ? {
                  ...queueItem,
                  status: {
                    status: "error",
                    progress: 0,
                    message: data.error || "failed to start download",
                  },
                }
              : queueItem
          )
        );
      }
    } catch (error) {
      console.error("Error downloading video:", error);
      setDownloadQueue((prev) =>
        prev.map((queueItem) =>
          queueItem.id === item.id
            ? {
                ...queueItem,
                status: {
                  status: "error",
                  progress: 0,
                  message: "connection error",
                },
              }
            : queueItem
        )
      );
    }
  };

  const removeFromQueue = (id: string) => {
    setDownloadQueue((prev) => prev.filter((item) => item.id !== id));
  };

  const clearCompleted = () => {
    setDownloadQueue((prev) =>
      prev.filter((item) => item.status.status !== "completed" && item.status.status !== "error")
    );
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      addToQueue();
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        backgroundColor: "#000000",
        color: "#ffffff",
        fontFamily: "system-ui, -apple-system, sans-serif",
        fontSize: "14px",
        fontWeight: "300",
      }}
    >
      <div
        style={{
          maxWidth: "600px",
          margin: "0 auto",
          padding: "60px 20px",
        }}
      >
        {/* Header */}
        <div
          style={{
            textAlign: "center",
            marginBottom: "60px",
          }}
        >
          <h1
            style={{
              fontSize: "24px",
              fontWeight: "200",
              margin: "0 0 8px 0",
              letterSpacing: "1px",
            }}
          >
            youtube downloader
          </h1>
          <p
            style={{
              color: "#666666",
              margin: "0",
              fontSize: "12px",
            }}
          >
            paste. download. done.
          </p>
        </div>

        {/* Input Section */}
        <div
          style={{
            marginBottom: "40px",
          }}
        >
          <div
            style={{
              display: "flex",
              gap: "12px",
              marginBottom: "16px",
            }}
          >
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="paste youtube url..."
              style={{
                flex: 1,
                padding: "12px 16px",
                backgroundColor: "#111111",
                border: "1px solid #333333",
                borderRadius: "4px",
                color: "#ffffff",
                fontSize: "14px",
                outline: "none",
                transition: "border-color 0.2s",
              }}
              onFocus={(e) => (e.target.style.borderColor = "#555555")}
              onBlur={(e) => (e.target.style.borderColor = "#333333")}
            />
            <button
              onClick={addToQueue}
              disabled={!url.trim()}
              style={{
                padding: "12px 20px",
                backgroundColor: url.trim() ? "#ffffff" : "#222222",
                color: url.trim() ? "#000000" : "#666666",
                border: "none",
                borderRadius: "4px",
                cursor: url.trim() ? "pointer" : "not-allowed",
                fontSize: "14px",
                fontWeight: "400",
                transition: "all 0.2s",
              }}
            >
              add
            </button>
          </div>

          <input
            type="text"
            value={downloadPath}
            onChange={(e) => setDownloadPath(e.target.value)}
            placeholder="download path..."
            style={{
              width: "100%",
              padding: "8px 16px",
              backgroundColor: "#111111",
              border: "1px solid #222222",
              borderRadius: "4px",
              color: "#888888",
              fontSize: "12px",
              outline: "none",
              boxSizing: "border-box",
            }}
          />
        </div>

        {/* Download Queue */}
        {downloadQueue.length > 0 && (
          <div
            style={{
              marginBottom: "40px",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: "20px",
              }}
            >
              <h3
                style={{
                  fontSize: "16px",
                  fontWeight: "300",
                  margin: "0",
                  color: "#cccccc",
                }}
              >
                download queue
              </h3>
              <button
                onClick={clearCompleted}
                style={{
                  padding: "6px 12px",
                  backgroundColor: "transparent",
                  color: "#666666",
                  border: "1px solid #333333",
                  borderRadius: "4px",
                  cursor: "pointer",
                  fontSize: "12px",
                }}
              >
                clear completed
              </button>
            </div>

            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "12px",
              }}
            >
              {downloadQueue.map((item) => (
                <div
                  key={item.id}
                  style={{
                    padding: "16px",
                    backgroundColor: "#111111",
                    borderRadius: "4px",
                    border: "1px solid #222222",
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "flex-start",
                      marginBottom: "8px",
                    }}
                  >
                    <div
                      style={{
                        flex: 1,
                        fontSize: "12px",
                        color: "#888888",
                        wordBreak: "break-all",
                        marginRight: "12px",
                      }}
                    >
                      {item.url}
                    </div>
                    <button
                      onClick={() => removeFromQueue(item.id)}
                      style={{
                        padding: "4px 8px",
                        backgroundColor: "transparent",
                        color: "#666666",
                        border: "none",
                        borderRadius: "2px",
                        cursor: "pointer",
                        fontSize: "10px",
                      }}
                    >
                      ×
                    </button>
                  </div>

                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "12px",
                    }}
                  >
                    <div
                      style={{
                        fontSize: "11px",
                        color:
                          item.status.status === "downloading"
                            ? "#ffffff"
                            : item.status.status === "completed"
                            ? "#666666"
                            : item.status.status === "error"
                            ? "#ff6b6b"
                            : "#888888",
                      }}
                    >
                      {item.status.message}
                    </div>

                    {item.status.status === "downloading" && (
                      <div
                        style={{
                          flex: 1,
                          height: "2px",
                          backgroundColor: "#222222",
                          borderRadius: "1px",
                          overflow: "hidden",
                        }}
                      >
                        <div
                          style={{
                            height: "100%",
                            backgroundColor: "#ffffff",
                            width: `${item.status.progress}%`,
                            transition: "width 0.3s ease",
                          }}
                        />
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Downloaded Videos */}
        <div>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "20px",
            }}
          >
            <h3
              style={{
                fontSize: "16px",
                fontWeight: "300",
                margin: "0",
                color: "#cccccc",
              }}
            >
              downloaded videos
            </h3>
            <button
              onClick={fetchVideos}
              style={{
                padding: "6px 12px",
                backgroundColor: "transparent",
                color: "#666666",
                border: "1px solid #333333",
                borderRadius: "4px",
                cursor: "pointer",
                fontSize: "12px",
              }}
            >
              refresh
            </button>
          </div>

          {videos.length === 0 ? (
            <p
              style={{
                color: "#666666",
                textAlign: "center",
                padding: "40px 0",
                margin: "0",
                fontSize: "12px",
              }}
            >
              no videos yet
            </p>
          ) : (
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "8px",
              }}
            >
              {videos.map((video, index) => (
                <div
                  key={index}
                  style={{
                    padding: "12px 16px",
                    backgroundColor: "#111111",
                    borderRadius: "4px",
                    border: "1px solid #222222",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <span
                    style={{
                      fontSize: "12px",
                      color: "#cccccc",
                      flex: 1,
                      wordBreak: "break-word",
                    }}
                  >
                    {video.filename}
                  </span>
                  <span
                    style={{
                      fontSize: "11px",
                      color: "#666666",
                      marginLeft: "12px",
                    }}
                  >
                    {video.size_mb} mb
                  </span>
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
