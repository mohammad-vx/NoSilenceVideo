NoSilenceVideo
Overview
NoSilenceVideo trims silent segments from videos, creating concise outputs for podcasts, interviews, or tutorials by keeping only audible parts with customizable time segments. It simplifies editing long videos with frequent silences, saving time and effort.
Features

Removes silent segments from videos based on customizable silence thresholds.
Supports processing specific video segments or entire files.
Displays durations of the original video, selected segment, and output video.
Optionally cleans up temporary files after processing.
Ensures smooth playback by cutting at keyframes to avoid delays or black frames.

Requirements

Python 3.6+
pydub library: pip install pydub
ffmpeg-python library (optional, for duration probing): pip install ffmpeg-python
ffmpeg installed and accessible in your system PATH:
Windows: Download from ffmpeg.org or install via choco install ffmpeg.
Linux/Mac: Install via sudo apt install ffmpeg (Ubuntu) or brew install ffmpeg (Mac).



Installation

Clone or download this repository.
Install the required Python packages:pip install pydub ffmpeg-python


Ensure ffmpeg is installed and added to your system PATH.

Usage

Open main.py and modify the following settings as needed:

VIDEO_PATH: Path to your input video file (e.g., r"path\to\video.mp4").
FINAL_OUTPUT: Output video file name (default: output_no_silence.mp4).
MIN_SILENCE_LEN: Minimum silence duration in milliseconds (default: 500).
SILENCE_THRESH: Silence threshold in dB (default: -40, range: -30 to -60).
USE_VIDEO_SEGMENT: Set to True to process a specific segment, or False for the entire video.
SEGMENT_START and SEGMENT_END: Start and end times of the segment (format: HH:MM:SS).
DELETE_TEMP: Set to True to delete temporary files after processing.


Run the script:
python main.py


The script will:

Extract audio from the video.
Detect non-silent segments.
Cut the video into clips based on non-silent ranges.
Merge clips into a single video without re-encoding.
Display durations of the original video, selected segment, and output video.
Clean up temporary files (if enabled).


The output video will be saved as output_no_silence.mp4 (or your specified FINAL_OUTPUT name).


Example
To process a segment from 01:10:50 to 01:11:50 of a video at D:\video.mp4:
VIDEO_PATH = r"D:\video.mp4"
USE_VIDEO_SEGMENT = True
SEGMENT_START = "01:10:50"
SEGMENT_END = "01:11:50"

Run the script, and the output will be output_no_silence.mp4 with silent parts removed.
Notes

Ensure the input video is in a standard format (e.g., H.264 video with AAC audio) to avoid issues. Convert non-standard videos using:ffmpeg -i input.mp4 -c:v libx264 -c:a aac converted_input.mp4


If you encounter issues like black frames or audio-video desync, check the ffmpeg output for warnings or adjust MIN_SILENCE_LEN (e.g., 400) and SILENCE_THRESH (e.g., -42).
The script adds a small buffer (0.1s before, 0.2s after) to each clip to ensure smooth transitions.

Troubleshooting

"ffmpeg not found": Ensure ffmpeg is installed and added to your system PATH.
Black frames or desync: Verify the input video format or try adjusting silence detection parameters.
Output video too long: Print len(non_silent_ranges) to debug potential segment overlaps.
No output: Check the input video path and ensure it exists.

License
This project is open-source and available under the MIT License.