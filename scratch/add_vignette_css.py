css_path = "E:/PropVista_Final/static/css/app.css"

vignette_css = """

/* LP Cinematic Video Vignette Overlay */
.lp-cinematic__vignette {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  background: radial-gradient(circle, rgba(8, 16, 36, 0) 35%, rgba(8, 16, 36, 0.45) 85%);
  z-index: 2;
}
"""

with open(css_path, "a", encoding="utf-8") as f:
    f.write(vignette_css)

print("Vignette CSS appended successfully!")
