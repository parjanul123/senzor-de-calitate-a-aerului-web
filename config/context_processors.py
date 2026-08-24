def ui_preferences(request):
    theme = request.session.get("ui_theme", "light")
    if theme not in {"light", "dark"}:
        theme = "light"
    return {"ui_theme": theme}