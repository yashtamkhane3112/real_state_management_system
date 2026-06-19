with open("E:/PropVista_Final/static/js/app.js", "r", encoding="utf-8", errors="replace") as f:
    lines = f.readlines()

for i in range(1019, 1224):
    print(lines[i], end="")
