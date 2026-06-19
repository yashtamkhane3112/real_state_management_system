import os

css_path = "E:/PropVista_Final/static/css/app.css"

with open(css_path, "r", encoding="utf-8", errors="replace") as f:
    content = f.read()

# 1. Update lp-cinematic height
old_cinematic_css = """  height: 700vh; /* scroll range of 700vh */"""
new_cinematic_css = """  height: 600vh; /* scroll range of 600vh */"""

if old_cinematic_css in content:
    content = content.replace(old_cinematic_css, new_cinematic_css)
    print("Updated cinematic height to 600vh in CSS.")
else:
    print("Cinematic height rule not found!")

# 2. Remove roles/role-pill css styles
target_roles_css = """.lp-cta__roles { display: flex; flex-wrap: wrap; gap: 0.75rem; justify-content: center; margin-top: 0.5rem; }
.lp-role-pill { display: inline-flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1.25rem; border-radius: 14px; background: rgba(255,255,255,0.10); border: 1px solid rgba(255,255,255,0.18); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); text-decoration: none; color: #ffffff; font-size: 0.88rem; transition: all 0.25s ease; }
.lp-role-pill:hover { background: rgba(255,255,255,0.18); border-color: rgba(255,255,255,0.35); transform: translateY(-2px); color: #ffffff; }
.lp-role-pill i { font-size: 1.15rem; }
.lp-role-pill span { display: flex; flex-direction: column; gap: 0.05rem; text-align: left; }
.lp-role-pill strong { font-weight: 700; font-size: 0.88rem !important; }
.lp-role-pill small { font-size: 0.72rem !important; color: rgba(255,255,255,0.60); }"""

if target_roles_css in content:
    content = content.replace(target_roles_css, "/* Role access cards styles removed */")
    print("Role buttons CSS rules removed.")
else:
    content_norm = content.replace("\r\n", "\n")
    target_roles_css_norm = target_roles_css.replace("\r\n", "\n")
    if target_roles_css_norm in content_norm:
        content = content_norm.replace(target_roles_css_norm, "/* Role access cards styles removed */")
        print("Role buttons CSS rules removed (normalized lines).")
    else:
        print("Role buttons CSS rules not found!")

# 3. Clean up responsive rules for roles
old_responsive_roles = """.lp-stats__grid,.lp-market__kpi-row,.lp-ai__grid,.lp-cta__roles { grid-template-columns: 1fr; }
  .lp-story__container { gap: 3.5rem; }
  .lp-cta__roles { flex-direction: column; }
  .lp-role-pill { width: 100%; }"""

new_responsive_roles = """.lp-stats__grid,.lp-market__kpi-row,.lp-ai__grid { grid-template-columns: 1fr; }
  .lp-story__container { gap: 3.5rem; }"""

if old_responsive_roles in content:
    content = content.replace(old_responsive_roles, new_responsive_roles)
    print("Responsive role buttons CSS rules removed.")
else:
    content_norm = content.replace("\r\n", "\n")
    old_responsive_roles_norm = old_responsive_roles.replace("\r\n", "\n")
    new_responsive_roles_norm = new_responsive_roles.replace("\r\n", "\n")
    if old_responsive_roles_norm in content_norm:
        content = content_norm.replace(old_responsive_roles_norm, new_responsive_roles_norm)
        print("Responsive role buttons CSS rules removed (normalized lines).")
    else:
        print("Responsive role buttons CSS rules not found!")

# 4. Remove previous vignette style and append new image story styles
# Let's search if our previous custom vignette was added at the bottom
vignette_part = """/* LP Cinematic Video Vignette Overlay */
.lp-cinematic__vignette {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  background: radial-gradient(circle, rgba(8, 16, 36, 0) 35%, rgba(8, 16, 36, 0.45) 85%);
  z-index: 2;
}"""

if vignette_part in content:
    content = content.replace(vignette_part, "")
else:
    content_norm = content.replace("\r\n", "\n")
    vignette_part_norm = vignette_part.replace("\r\n", "\n")
    if vignette_part_norm in content_norm:
        content = content_norm.replace(vignette_part_norm, "")

story_experience_css = """
/* ================================================================
   PropVista V8 Cinematic Image Story Experience
   ================================================================ */
.lp-story-wrapper {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 1;
}

.lp-story-img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0;
  transform: scale(1.00);
  transform-origin: center;
  will-change: opacity, transform;
  transition: opacity 0.4s ease-out;
}

.lp-story-img.active {
  opacity: 1;
}

.lp-cinematic__vignette {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  background: linear-gradient(180deg, rgba(15, 23, 42, 0.15), rgba(15, 23, 42, 0.30));
  z-index: 2;
}
"""

content = content.strip() + "\n" + story_experience_css

with open(css_path, "w", encoding="utf-8") as f:
    f.write(content)
print("app.css updated successfully for V8!")
