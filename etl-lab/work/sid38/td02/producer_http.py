
import random
import requests

NIFI_URL = "http://nifi:9091/sid38/td1/logs"
SERVICES = ["api-gateway", "auth-service", "billing-service"]
SEVERITIES = ["INFO", "WARNING", "ERROR", "CRITICAL"]
MESSAGES = {
    "INFO": "Requete traitee avec succes",
    "WARNING": "Latence elevee detectee",
    "ERROR": "Echec de connexion a la base de donnees",
    "CRITICAL": "Service indisponible",
}


def build_event():
    severity = random.choice(SEVERITIES)
    return {
        "service": random.choice(SERVICES),
        "severity": severity,
        "message": MESSAGES[severity],
    }


def send_event(event):
    try:
        response = requests.post(NIFI_URL, json=event, timeout=5)
        response.raise_for_status()
        print(f"Evenement envoye : {event}")
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de l'envoi a NiFi : {e}")


def main():
    send_event(build_event())


if __name__ == "__main__":
    main()