# PropVista Video/Image Quality Audit Report

## 1. Quality & Resolution Audit
- **Video Source Resolution**: The video file `static/property.mp4` has a native resolution of **1280x720** (720p HD).
- **Extracted Frames Resolution**: The extracted frames in the `property_000` directory also have a native resolution of **1280x720**.
- **Upscaling / Softness Analysis**:
  - When rendering on standard desktop screens (such as 1920x1080 or 1440x900 viewports) under `object-fit: cover`, the browser must scale the 1280x720 source up to fill the viewport. This upscaling introduces significant bilinear filtering softness.
  - On a 1920x1080 display, upscaling a 1280x720 video represents a **1.5x linear stretch** (a 50% increase in both dimensions), which reduces pixel density and yields a soft, non-premium visual appearance.

## 2. Root Cause of Blur/Softness
We investigated the following factors to isolate the source of visual softness:
1. **Low-Resolution Source**: 720p is insufficient for crisp, premium fullscreen showcases on desktop viewports. High-end real estate presentation requires 1080p (FHD) or 4K (UHD) media.
2. **Lossy Compression Artifacts**:
   - `property.mp4` has typical H.264 inter-frame compression.
   - When scrubbing, the browser must decode I-frames and interpolate delta frames. Rapid seek operations force the decoder to quickly reconstruct frames, resulting in visible macroblocks (blocky details) and color banding.
3. **Object-Fit Cover Stretching**:
   - Stretches pixels directly to cover the width and height of the screen.
   - This causes layout-ratio stretching where aspect ratios differ, amplifying blur in corners.
4. **CSS Blur Transition**:
   - The previous scroll-interactive Javascript logic applied a blur filter of up to `8px` in the final 10% of scroll progress, which was intentionally designed but contributed to user-perceived blur.

## 3. Playback Smoothness and Browser Behavior
- **Desktop (Chrome/Safari/Firefox)**: Smooth, hardware-accelerated seek times are achieved when scrolling slowly. However, rapid scrolling results in minor frame skipping because the decoder cannot keep up with high-frequency seeking requests.
- **Mobile Devices (iOS/Android)**: iOS Safari restricts rapid video seeks to save battery, causing noticeable frame skipping and stuttering when scrubbing via scroll.
- **Memory/CPU Overhead**: Keeping an active video decoder running and seeking at 60 FPS consumes significant CPU and GPU decoding resources.

## 4. Remediation Plan
Moving to the **V8 Cinematic Image Story Experience** resolves these quality limitations:
- Instead of upscaled compressed video frames, we will use a curated set of **11 high-quality, high-detail frame images** from `property_000` folder.
- The transitions will be driven by smooth, GPU-accelerated opacity cross-fades rather than lossy video seeking, resulting in an exceptionally sharp, high-end, and battery-friendly luxury showcase.
