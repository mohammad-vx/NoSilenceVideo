import os
import subprocess
from pydub import AudioSegment, silence
from datetime import datetime
import shutil

# ========== إعدادات قابلة للتعديل ==========
VIDEO_PATH = r"D:\Dd\yt1z.net - لقاء عرفة الشيخ نبيل العوضي مع د. أحمد العربي TelfaznetTV (1080p).mp4"          # اسم أو مسار الفيديو الأصلي
FINAL_OUTPUT = "output_no_silence.mp4"
TEMP_DIR = "temp_chunks"
AUDIO_PATH = "temp_audio.wav"
TEMP_VIDEO = "temp_segment.mp4"

# الصمت: حدد كم ملي ثانية يُعتبر صمت (500 = 0.5 ثانية)
MIN_SILENCE_LEN = 500   # بالميلي ثانية (تقليل لتحسين الدقة)
SILENCE_THRESH = -40    # زيادة الحساسية (مسموح -30 إلى -60 تقريبًا)

# هل تريد معالجة جزء معين فقط من الفيديو؟
USE_VIDEO_SEGMENT = True
SEGMENT_START = "01:10:50"     # بصيغة HH:MM:SS
SEGMENT_END   = "01:11:50"   # بصيغة HH:MM:SS

# هل تحذف الملفات المؤقتة بعد الانتهاء؟
DELETE_TEMP = True
# ============================================

# === دالة حساب المدة بالثواني ===
def get_duration_seconds(start, end):
    fmt = "%H:%M:%S"
    t1 = datetime.strptime(start, fmt)
    t2 = datetime.strptime(end, fmt)
    return int((t2 - t1).total_seconds())

# === تأكد من ffmpeg مثبت ===
if subprocess.call(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0:
    raise EnvironmentError("يرجى تثبيت ffmpeg أولاً.")

# === التحقق من وجود ملف الفيديو ===
if not os.path.exists(VIDEO_PATH):
    raise FileNotFoundError(f"ملف الفيديو غير موجود: {VIDEO_PATH}")

# === عرض مدة الفيديو قبل القص ===
def get_video_duration(path):
    try:
        import ffmpeg
        probe = ffmpeg.probe(path)
        return float(probe['format']['duration'])
    except Exception:
        # fallback to ffprobe via subprocess
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                 "default=noprint_wrappers=1:nokey=1", path],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            return float(result.stdout.strip())
        except Exception:
            return None

orig_duration = get_video_duration(VIDEO_PATH)
if orig_duration:
    print(f"⏱️ مدة الفيديو قبل القص: {orig_duration:.2f} ثانية ({orig_duration/60:.2f} دقيقة)")
else:
    print("⚠️ تعذر حساب مدة الفيديو الأصلي.")

# === عرض مدة الجزء المحدد قبل القص ===
segment_duration = get_duration_seconds(SEGMENT_START, SEGMENT_END)
print(f"⏱️ مدة الجزء المحدد قبل القص: {segment_duration} ثانية ({segment_duration/60:.2f} دقيقة)")

# === قص جزء من الفيديو إن لزم ===
if USE_VIDEO_SEGMENT:
    duration = str(get_duration_seconds(SEGMENT_START, SEGMENT_END))
    subprocess.call([
        "ffmpeg", "-y", "-i", VIDEO_PATH,
        "-ss", SEGMENT_START, "-t", duration,
        "-c", "copy", TEMP_VIDEO
    ])
    VIDEO_PATH = TEMP_VIDEO

# === استخراج الصوت من الفيديو ===
subprocess.call([
    "ffmpeg", "-y", "-i", VIDEO_PATH,
    "-ac", "1", "-ar", "16000", "-vn", AUDIO_PATH
])

# === كشف فترات الصمت ===
audio = AudioSegment.from_wav(AUDIO_PATH)
non_silent_ranges = silence.detect_nonsilent(
    audio,
    min_silence_len=MIN_SILENCE_LEN,
    silence_thresh=SILENCE_THRESH
)

# === إنشاء مجلد مؤقت ===
os.makedirs(TEMP_DIR, exist_ok=True)
clip_paths = []

# === تقطيع الفيديو حسب الصوت ===
for i, (start_ms, end_ms) in enumerate(non_silent_ranges):
    start_sec = max(0, start_ms / 1000 - 0.1)  # إضافة عازل 0.1 ثانية
    duration = (end_ms - start_ms) / 1000 + 0.2  # عازل إضافي
    clip_name = os.path.join(TEMP_DIR, f"clip_{i:03d}.mp4")
    # إصلاح مشكلة أول 5 ثواني: استخدم -ss قبل -i لأول مقطع فقط
    if i == 0:
        # -ss قبل -i أسرع وأكثر دقة لأول مقطع
        subprocess.call([
            "ffmpeg", "-y", "-ss", str(start_sec), "-i", VIDEO_PATH,
            "-t", str(duration),
            "-c:v", "libx264", "-force_key_frames", "expr:gte(t,n_forced*2)",
            "-c:a", "copy", clip_name
        ])
    else:
        subprocess.call([
            "ffmpeg", "-y", "-i", VIDEO_PATH,
            "-ss", str(start_sec), "-t", str(duration),
            "-c:v", "libx264", "-force_key_frames", "expr:gte(t,n_forced*2)",
            "-c:a", "copy", clip_name
        ])
    clip_paths.append(clip_name)

# === إنشاء ملف concat ===
concat_list_path = os.path.join(TEMP_DIR, "concat_list.txt")
with open(concat_list_path, "w", encoding="utf-8") as f:
    for clip in clip_paths:
        abs_path = os.path.abspath(clip).replace('\\', '/')
        f.write(f"file '{abs_path}'\n")

# === دمج المقاطع بدون إعادة ترميز ===
subprocess.call([
    "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list_path,
    "-c", "copy", FINAL_OUTPUT
])

# === عرض مدة الفيديو بعد القص ===
final_duration = get_video_duration(FINAL_OUTPUT)
if final_duration:
    print(f"\n\n⏱️ Selected segment duration before cut: {segment_duration} seconds ({segment_duration/60:.2f} minutes)")
    print(f"⏱️ Video duration after cut: {final_duration:.2f} seconds ({final_duration/60:.2f} minutes)")
else:
    print("⚠️ Could not determine output video duration.")

print(f"\n✅ Video without silence created: {FINAL_OUTPUT}")

# === تنظيف الملفات المؤقتة ===
if DELETE_TEMP:
    try:
        shutil.rmtree(TEMP_DIR)
        if os.path.exists(AUDIO_PATH):
            os.remove(AUDIO_PATH)
        if USE_VIDEO_SEGMENT and os.path.exists(TEMP_VIDEO):
            os.remove(TEMP_VIDEO)
    except Exception as e:
        print(f"⚠️ فشل حذف الملفات المؤقتة: {e}")