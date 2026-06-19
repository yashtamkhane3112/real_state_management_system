with open("E:/PropVista_Final/templates/home.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "<h" in line or "<form" in line or "class=\"lp-btn" in line:
        print(f"{i+1}: {line.strip()}")
