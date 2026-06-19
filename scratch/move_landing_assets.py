import os
import shutil

base_dir = "E:/PropVista_Final/static/media/landing"
os.makedirs(os.path.join(base_dir, "video-hero"), exist_ok=True)
os.makedirs(os.path.join(base_dir, "video-scrub"), exist_ok=True)
os.makedirs(os.path.join(base_dir, "image-story"), exist_ok=True)

print("Directories created successfully!")

# Move video-hero asset
hero_video = "E:/PropVista_Final/static/videoplayback.mp4"
if os.path.exists(hero_video):
    shutil.copy2(hero_video, os.path.join(base_dir, "video-hero", "videoplayback.mp4"))
    print("Copied videoplayback.mp4 to video-hero/")

# Move video-scrub asset
scrub_video = "E:/PropVista_Final/static/property.mp4"
if os.path.exists(scrub_video):
    shutil.copy2(scrub_video, os.path.join(base_dir, "video-scrub", "property.mp4"))
    print("Copied property.mp4 to video-scrub/")

# Move image-story assets
story_frames_dir = "E:/PropVista_Final/static/images/story-frames"
if os.path.exists(story_frames_dir):
    for f in os.listdir(story_frames_dir):
        if f.endswith(".jpg"):
            shutil.copy2(os.path.join(story_frames_dir, f), os.path.join(base_dir, "image-story", f))
    print("Copied story frames to image-story/")
