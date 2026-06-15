from django.conf import settings


def gemini_or_fallback(feature: str, payload: dict) -> str:
    prompt = payload.get("prompt") or " ".join(f"{key}: {value}" for key, value in payload.items())
    fallback = (
        f"{feature.replace('_', ' ').title()}: Add crisp location benefits, verified amenities, transparent pricing, "
        f"strong photos, and a clear visit CTA. Input considered: {prompt[:280]}"
    )
    if not settings.GEMINI_API_KEY:
        return fallback
    try:
        import google.generativeai as genai

        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")
        result = model.generate_content(f"You are a real estate marketing assistant. Feature: {feature}. Input: {prompt}")
        return result.text or fallback
    except Exception:
        return fallback

