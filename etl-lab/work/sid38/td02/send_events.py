
import random
import time
import requests

NIFI_URL = "http://nifi:9091/sid38/td1/logs"
SERVICES = ["api-gateway", "auth-service", "billing-service"]
SEVERITY_WEIGHTS = {"INFO": 0.70, "WARNING": 0.15, "ERROR": 0.10, "CRITICAL": 0.05}
MESSAGES = {
    "INFO": "Requete traitee avec succes",
    "WARNING": "Latence elevee detectee",
    "ERROR": "Echec de connexion a la base de donnees",
    "CRITICAL": "Service indisponible",
}


def build_event():
    severity = random.choices(
        list(SEVERITY_WEIGHTS), weights=list(SEVERITY_WEIGHTS.values())
    )[0]
    return {
        "service": random.choice(SERVICES),
        "severity": severity,
        "message": MESSAGES[severity],
    }


def send_loop(nb_events, delay_s):
    for _ in range(nb_events):
        event = build_event()
        try:
            response = requests.post(NIFI_URL, json=event, timeout=5)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Erreur reseau : {e}")
        time.sleep(delay_s)


if __name__ == "__main__":
    send_loop(nb_events=200, delay_s=0.5)