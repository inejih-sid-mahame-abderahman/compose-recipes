import json
import logging
import requests
from confluent_kafka import Producer

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")

producer = Producer({
    "bootstrap.servers": "etlkafka:9092"
})


def delivery_report(err, msg):
    if err is not None:
        logging.error("Delivery failed: %s", err)
    else:
        logging.info(
            "Sent to topic=%s partition=%s offset=%s",
            msg.topic(), msg.partition(), msg.offset()
        )


def fetch_price(asset):
    url = f"https://api.coinbase.com/v2/prices/{asset}-USD/spot"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return float(data["data"]["amount"])
    except requests.exceptions.RequestException as exc:
        logging.error("HTTP error fetching %s: %s", asset, exc)
    except (KeyError, ValueError) as exc:
        logging.error("Invalid response for %s: %s", asset, exc)

    return None


def main():
    for asset in ("BTC", "ETH"):
        price = fetch_price(asset)

        if price is None:
            continue

        record = {f"{asset.lower()}_usd": price}
        key = f"{asset.lower()}_usd_price"

        producer.produce(
            "btc_prices",
            key=key,
            value=json.dumps(record),
            callback=delivery_report
        )

    remaining = producer.flush(timeout=15)

    if remaining:
        logging.error("%s message(s) still pending", remaining)


if __name__ == "__main__":
    main()