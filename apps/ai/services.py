class AIService:
    """Stable integration boundary for the future external AI API."""

    def train(self, payload):
        return {
            "status": "queued",
            "job_id": "mock-training-job",
            "device_id": payload.get("device_id"),
            "input": payload,
            "mock": True,
        }

    def predict(self, payload):
        return {
            "status": "available",
            "prediction": "Calitatea aerului ramane stabila.",
            "input": payload,
            "mock": True,
        }

    def detect_anomalies(self, payload):
        return {
            "anomalies": [],
            "summary": "Nu au fost identificate anomalii in datele disponibile pentru dispozitiv.",
            "device_id": payload.get("device_id"),
            "mock": True,
        }

    def chat(self, message):
        welcome_message = "Bine ați venit! Îți pot ajuta cu calitatea aerului, senzorii și recomandări rapide."
        response_text = f"Raspuns demonstrativ pentru: {message}"
        return {
            "message": response_text,
            "reply": response_text,
            "welcome_message": welcome_message,
            "mock": True,
        }