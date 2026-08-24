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

    @staticmethod
    def _as_float(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @classmethod
    def _percentile(cls, values, ratio):
        if not values:
            return None
        ordered = sorted(values)
        index = int((len(ordered) - 1) * ratio)
        return ordered[max(0, min(index, len(ordered) - 1))]

    @classmethod
    def _compute_dynamic_thresholds(cls, recent_measurements):
        """Derive soft min/max bands from recent sensor history."""
        parameters = ["temperatura", "umiditate", "co2", "pm25", "pm10", "voc"]
        dynamic = {}

        for parameter in parameters:
            values = []
            for row in recent_measurements or []:
                numeric = cls._as_float(row.get(parameter))
                if numeric is not None:
                    values.append(numeric)

            if len(values) < 10:
                continue

            p10 = cls._percentile(values, 0.10)
            p90 = cls._percentile(values, 0.90)
            avg = mean(values)
            if p10 is None or p90 is None:
                continue

            spread = max(p90 - p10, max(abs(avg) * 0.05, 0.5))
            dynamic[parameter] = {
                "minimum": round(p10 - spread * 0.25, 2),
                "maximum": round(p90 + spread * 0.25, 2),
                "samples": len(values),
            }

        return dynamic

    def recommend_transport_thresholds(self, profile_name, device_name=None, search_goal=None, operation_mode=None, recent_measurements=None):
        """Deterministic recommendation based on cargo keywords + operation mode."""
        profile_text = (profile_name or "").strip()
        mode_text = (operation_mode or "general").strip().lower()
        if mode_text not in {"general", "depozitare", "transport"}:
            mode_text = "general"

        slug = profile_text.lower()

        # Rule 1: cargo name -> temperature/humidity
        cargo_rules = [
            ("lactate", ["lapte", "lactate", "branza", "iaurt", "unt"], (2.0, 8.0), (40.0, 70.0)),
            ("carne", ["carne", "pui", "porc", "vita"], (-2.0, 4.0), (80.0, 95.0)),
            ("peste", ["peste", "fish"], (-2.0, 2.0), (85.0, 95.0)),
            ("flori/plante", ["flor", "plant"], (2.0, 8.0), (70.0, 90.0)),
            ("electronice", ["electron", "componente"], (10.0, 35.0), (20.0, 60.0)),
            ("medicamente", ["medicament", "farma", "vaccin"], (2.0, 8.0), (35.0, 65.0)),
            ("legume/fructe", ["legum", "fruct", "mer", "banan"], (4.0, 12.0), (85.0, 95.0)),
        ]

        detected_category = "implicit"
        temperatura = {"minimum": 15.0, "maximum": 30.0}
        umiditate = {"minimum": 30.0, "maximum": 70.0}

        for category, keywords, temp_range, hum_range in cargo_rules:
            if any(keyword in slug for keyword in keywords):
                detected_category = category
                temperatura = {"minimum": temp_range[0], "maximum": temp_range[1]}
                umiditate = {"minimum": hum_range[0], "maximum": hum_range[1]}
                break

        # Rule 2: operation mode -> gas/particles
        mode_thresholds = {
            "general": {
                "co2": {"minimum": 400.0, "maximum": 1000.0},
                "pm25": {"minimum": 0.0, "maximum": 15.0},
                "pm10": {"minimum": 0.0, "maximum": 50.0},
                "voc": {"minimum": 0.0, "maximum": 250.0},
            },
            "depozitare": {
                "co2": {"minimum": 400.0, "maximum": 800.0},
                "pm25": {"minimum": 0.0, "maximum": 12.0},
                "pm10": {"minimum": 0.0, "maximum": 40.0},
                "voc": {"minimum": 0.0, "maximum": 200.0},
            },
            "transport": {
                "co2": {"minimum": 350.0, "maximum": 1300.0},
                "pm25": {"minimum": 0.0, "maximum": 25.0},
                "pm10": {"minimum": 0.0, "maximum": 75.0},
                "voc": {"minimum": 0.0, "maximum": 350.0},
            },
        }

        thresholds = {
            "temperatura": temperatura,
            "umiditate": umiditate,
            **mode_thresholds[mode_text],
        }

        notes = (
            f"Categorie detectata: {detected_category}. "
            f"Regula aplicata pentru temperatura/umiditate din numele profilului '{profile_text or 'necunoscut'}'. "
            f"Mod operare aplicat pentru CO2/PM/VOC: {mode_text}."
        )

        if search_goal:
            notes += f" Context introdus: {search_goal.strip()}."

        return {
            "profile_name": f"AI-{profile_text or 'profil'}-{mode_text}",
            "notes": notes,
            "thresholds": thresholds,
            "reason": "mapare determinista keyword + mod operare",
            "search_goal": (search_goal or "").strip(),
            "operation_mode": mode_text,
            "detected_category": detected_category,
            "mock": True,
        }