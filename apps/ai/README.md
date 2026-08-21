# AI integration boundary

Paginile website-ului si endpointurile `/ai/train/`, `/ai/predict/` si `/ai/chat/` depind exclusiv de `AIService`.

Inlocuieste implementarile mock din `services.py` cu apelurile HTTP catre API-ul AI atunci cand acesta devine public. Pastreaza semnaturile `train()`, `predict(payload)` si `chat(message)` pentru ca rutele si paginile existente sa nu necesite modificari.