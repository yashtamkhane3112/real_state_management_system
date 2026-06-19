with open("E:/PropVista_Final/static/css/app.css", "r", encoding="utf-8", errors="replace") as f:
    lines = f.readlines()

for i in range(2659, min(2735, len(lines))):
    cleaned = "".join([c if ord(c) < 128 else "?" for c in lines[i]])
    print(f"{i+1}: {cleaned}", end="")
