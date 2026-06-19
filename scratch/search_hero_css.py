with open("E:/PropVista_Final/static/css/app.css", "r", encoding="utf-8", errors="replace") as f:
    content = f.read()

# Print rules containing pv-hero or pm-hero
lines = content.split("\n")
for i, line in enumerate(lines):
    if "pv-hero" in line or "pm-hero" in line:
        print(f"{i+1}: {line}")
