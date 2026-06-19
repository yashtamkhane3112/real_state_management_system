import os
import sys
import django

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'propvista.settings')
django.setup()


from django.test import Client, override_settings

def test_modes():
    client = Client()

    print("--- TESTING MODE A: VIDEO_HERO ---")
    with override_settings(LANDING_MEDIA_MODE="VIDEO_HERO", ALLOWED_HOSTS=["localhost", "127.0.0.1", "testserver"]):
        response = client.get("/")

        assert response.status_code == 200, f"VIDEO_HERO failed: {response.status_code}"
        content = response.content.decode("utf-8")
        
        # Verify VIDEO_HERO markup is present
        assert "pv-hero pm-hero" in content, "Missing VIDEO_HERO wrapper class"
        assert "media/landing/video-hero/videoplayback.mp4" in content, "Missing hero video asset path"
        
        # Verify others are absent
        assert "lp-cinematic" not in content, "VIDEO_SCRUB/IMAGE_STORY markup leaked into VIDEO_HERO"
        assert "landing-mode-config" in content, "Missing landing-mode-config helper"
        assert 'data-mode="VIDEO_HERO"' in content, "Incorrect config data-mode"
        print("VIDEO_HERO matches perfectly!")

    print("\n--- TESTING MODE C: IMAGE_STORY ---")
    with override_settings(LANDING_MEDIA_MODE="IMAGE_STORY", ALLOWED_HOSTS=["localhost", "127.0.0.1", "testserver"]):
        response = client.get("/")
        assert response.status_code == 200, f"IMAGE_STORY failed: {response.status_code}"
        content = response.content.decode("utf-8")
        
        # Verify IMAGE_STORY markup is present
        assert "lp-cinematic" in content, "Missing lp-cinematic section"
        assert "lp-story-wrapper" in content, "Missing lp-story-wrapper"
        assert "media/landing/image-story/story_01.jpg" in content, "Missing story frame 1 path"
        assert "media/landing/image-story/story_10.jpg" in content, "Missing story frame 10 path"

        # Verify others are absent
        assert "pv-hero pm-hero" not in content, "VIDEO_HERO leaked into IMAGE_STORY"
        assert 'data-mode="IMAGE_STORY"' in content, "Incorrect config data-mode"
        print("IMAGE_STORY matches perfectly!")

    print("\nALL LANDING MODES VALIDATED SUCCESSFULLY!")

if __name__ == "__main__":
    try:
        test_modes()
    except AssertionError as e:
        print("AssertionError:", e)
        sys.exit(1)
    except Exception as e:
        print("Unexpected Error:", e)
        sys.exit(1)
