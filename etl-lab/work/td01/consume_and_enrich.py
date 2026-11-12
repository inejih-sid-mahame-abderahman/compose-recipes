import json
import logging
import time
from datetime import datetime

import requests
import psycopg2
from confluent_kafka import Consumer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

consumer = Consumer({
    "bootstrap.servers": "etlkafka:9092",
    "group.id": "btc_group",
    "auto.offset.reset": "earliest"
})

db_connection = psycopg2.connect(
    dbname="etldb",
    user="admin",
    password="admin12345",
    host="etldb",
    port=5432
)

db_cursor = db_connection.cursor()

db_cursor.execute("""
    CREATE TABLE IF NOT EXISTS btc_prices (
        date DATE NOT NULL UNIQUE,
        btc_usd NUMERIC NOT NULL,
        microbtc_mru NUMERIC NOT NULL,
        insert_time TIMESTAMP NOT NULL
    );
""")

# Also enforce uniqueness if the table already existed.
db_cursor.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS btc_prices_date_unique
    ON btc_prices (date);
""")
db_connection.commit()

# Cache the exchange rate for one hour.
cached_rate = None
rate_fetched_at = 0


def get_mru_rate():
    global cached_rate, rate_fetched_at

    now = time.monotonic()

    if cached_rate is not None and now - rate_fetched_at < 3600:
        return cached_rate

    try:
        response = requests.get(
            "https://api.exchangerate-api.com/v4/latest/USD",
            timeout=10
        )
        response.raise_for_status()
        rates = response.json()["rates"]
        rate = rates.get("MRU")

        if rate is None:
            raise ValueError("MRU exchange rate is missing")

        cached_rate = float(rate)
        rate_fetched_at = now
        return cached_rate

    except (requests.exceptions.RequestException, ValueError, KeyError) as exc:
        logging.error("Exchange-rate request failed: %s", exc)

        # If available, use the previous cached rate as a fallback.
        if cached_rate is not None:
            logging.warning("Using previously cached exchange rate")
            return cached_rate

        raise


def enrich_data(record):
    rate = get_mru_rate()
    record["microbtc_mru"] = (
        record["btc_usd"] * 1_000_000 * rate
    )
    return record


def save_to_db(record):
    now = datetime.now()

    query = """
        INSERT INTO btc_prices
            (date, btc_usd, microbtc_mru, insert_time)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (date) DO UPDATE SET
            btc_usd = EXCLUDED.btc_usd,
            microbtc_mru = EXCLUDED.microbtc_mru,
            insert_time = EXCLUDED.insert_time;
    """

    db_cursor.execute(query, (
        now.date(),
        record["btc_usd"],
        record["microbtc_mru"],
        now
    ))
    db_connection.commit()
    logging.info("BTC price saved or updated for %s", now.date())


def main():
    consumer.subscribe(["btc_prices"])
    logging.info("Consumer started; waiting for messages")

    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue

            if msg.error():
                logging.error("Kafka consumer error: %s", msg.error())
                continue

            try:
                record = json.loads(msg.value().decode("utf-8"))
                logging.info("Message consumed: %s", record)

                if "btc_usd" not in record:
                    logging.info("Skipping non-BTC message")
                    continue

                enriched_record = enrich_data(record)
                save_to_db(enriched_record)

            except (
                ValueError,
                KeyError,
                requests.exceptions.RequestException
            ) as exc:
                logging.error("Could not process message: %s", exc)

    except KeyboardInterrupt:
        logging.info("Stopping consumer")

    finally:
        consumer.close()
        db_cursor.close()
        db_connection.close()


if __name__ == "__main__":
    main()