# KDrama Downloader

Kdrama downloader is a Python-based program that enables users to easily download their favorite Korean dramas with just one click. The program uses the ffmpeg binary for converting the video segments (ts) obtained from the Consumet API into a standard video format. This makes it easy for users to watch their downloaded content on any device without any compatibility issues.

<br />

## Folder Structure

```
Root/
├─ movies/
├─ ffmpeg/      (Optional, can be placed anywhere)
├─ kdrama.ui
├─ main.exe
```

## Prerequisites

1. Download the `ffmpeg` folder and save it.
2. Grab the **Absolute Path** of the `ffmpeg` bin folder and save it in **Environment Variables** Path. (e.g. C:\ffmpeg_files\bin)
3. Run the `main.exe`.
