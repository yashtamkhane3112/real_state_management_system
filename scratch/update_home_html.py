import os

html_path = "E:/PropVista_Final/templates/home.html"

with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Replace the cinematic section
old_cinematic = """<section class="lp-cinematic" id="cinematic-container" aria-label="Cinematic property presentation">
  <div class="lp-cinematic__sticky" id="cinematic-sticky">
    <video class="lp-cinematic__video" id="cinematic-video" preload="auto" muted playsinline webkit-playsinline>
      <source src="{% static 'property.mp4' %}" type="video/mp4">
    </video>
    
    <!-- Subtle luxury scroll indicator -->
    <div class="lp-cinematic__hint" id="cinematic-hint">
      <span class="lp-cinematic__hint-text">Scroll to explore the property</span>
      <div class="lp-cinematic__hint-line"></div>
    </div>
  </div>
</section>"""

new_cinematic = """<section class="lp-cinematic" id="cinematic-container" aria-label="Cinematic property presentation" style="height: 600vh;">
  <div class="lp-cinematic__sticky" id="cinematic-sticky">
    <!-- Cinematic Image Story Stack -->
    <div class="lp-story-wrapper">
      <img class="lp-story-img active" src="{% static 'images/story-frames/property_000.jpg' %}" alt="Story Frame 1" fetchpriority="high">
      <img class="lp-story-img" src="{% static 'images/story-frames/property_010.jpg' %}" alt="Story Frame 2">
      <img class="lp-story-img" src="{% static 'images/story-frames/property_020.jpg' %}" alt="Story Frame 3">
      <img class="lp-story-img" src="{% static 'images/story-frames/property_030.jpg' %}" alt="Story Frame 4">
      <img class="lp-story-img" src="{% static 'images/story-frames/property_040.jpg' %}" alt="Story Frame 5">
      <img class="lp-story-img" src="{% static 'images/story-frames/property_050.jpg' %}" alt="Story Frame 6">
      <img class="lp-story-img" src="{% static 'images/story-frames/property_060.jpg' %}" alt="Story Frame 7">
      <img class="lp-story-img" src="{% static 'images/story-frames/property_070.jpg' %}" alt="Story Frame 8">
      <img class="lp-story-img" src="{% static 'images/story-frames/property_080.jpg' %}" alt="Story Frame 9">
      <img class="lp-story-img" src="{% static 'images/story-frames/property_090.jpg' %}" alt="Story Frame 10">
      <img class="lp-story-img" src="{% static 'images/story-frames/property_099.jpg' %}" alt="Story Frame 11">
    </div>
    
    <!-- Luxury vignette overlay -->
    <div class="lp-cinematic__vignette"></div>
    
    <!-- Subtle luxury scroll indicator -->
    <div class="lp-cinematic__hint" id="cinematic-hint">
      <span class="lp-cinematic__hint-text">Scroll to explore the property</span>
      <div class="lp-cinematic__hint-line"></div>
    </div>
  </div>
</section>"""

if old_cinematic in content:
    content = content.replace(old_cinematic, new_cinematic)
    print("Cinematic section HTML replaced.")
else:
    print("Cinematic section HTML not found!")

# 2. Remove the comparison card
old_compare_card = """      <!-- Comparison card -->
      <div class="lp-ai-card" id="ai-card-compare">
        <div class="lp-ai-card__icon lp-ai-card__icon--gold"><i class="bi bi-columns-gap"></i></div>
        <h3 class="lp-ai-card__title">Property Comparison</h3>
        <p class="lp-ai-card__body">Compare up to 4 properties side-by-side across price, area, location score, amenities, and AI rating.</p>
        <a href="{% url 'properties:list' %}" class="lp-ai-card__link" id="ai-compare-link">Start comparing <i class="bi bi-arrow-right"></i></a>
      </div>"""

if old_compare_card in content:
    content = content.replace(old_compare_card, "")
    print("Comparison card HTML removed.")
else:
    # Try with different whitespace/indentation
    content_norm = content.replace("\r\n", "\n")
    old_compare_card_norm = old_compare_card.replace("\r\n", "\n")
    if old_compare_card_norm in content_norm:
        content = content_norm.replace(old_compare_card_norm, "")
        print("Comparison card HTML removed (normalized lines).")
    else:
        print("Comparison card HTML not found!")

# 3. Remove the role access cards
old_roles = """      <!-- Role access cards -->
      <div class="lp-cta__roles">
        <a href="{% url 'accounts:buyer_dashboard' %}" class="lp-role-pill" id="cta-role-buyer">
          <i class="bi bi-person-heart"></i>
          <span><strong>Buyer</strong><small>Wishlist, visits, inquiries</small></span>
        </a>
        <a href="{% url 'accounts:seller_dashboard' %}" class="lp-role-pill" id="cta-role-seller">
          <i class="bi bi-house-gear"></i>
          <span><strong>Seller</strong><small>Listings, pipeline</small></span>
        </a>
        <a href="{% url 'accounts:admin_dashboard' %}" class="lp-role-pill" id="cta-role-admin">
          <i class="bi bi-shield-check"></i>
          <span><strong>Admin</strong><small>Approvals, audit</small></span>
        </a>
      </div>"""

if old_roles in content:
    content = content.replace(old_roles, "")
    print("Role access cards HTML removed.")
else:
    content_norm = content.replace("\r\n", "\n")
    old_roles_norm = old_roles.replace("\r\n", "\n")
    if old_roles_norm in content_norm:
        content = content_norm.replace(old_roles_norm, "")
        print("Role access cards HTML removed (normalized lines).")
    else:
        print("Role access cards HTML not found!")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(content)
print("home.html updated successfully!")
