import os

css_path = "E:/PropVista_Final/static/css/app.css"

with open(css_path, "r", encoding="utf-8", errors="replace") as f:
    content = f.read()

target = """.lp-cinematic__canvas {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}"""

replacement = """.lp-cinematic__canvas,
.lp-cinematic__video {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}"""

if target in content:
    content = content.replace(target, replacement)
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("CSS updated successfully!")
else:
    print("Target CSS block not found!")
