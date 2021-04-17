# Run celery workers
# celery -A db worker --loglevel=info

import sys
import json
import psycopg2
import logging
from celery import Celery
from datetime import datetime

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Configure with your own broker
app = Celery("tasks", broker="redis://localhost:6379/4")

# Initialize db
db = psycopg2.connect(database="postgres", user="postgres", password="password", host="127.0.0.1", port="5432")

# Db insert statement
insert_tick_statement = """INSERT INTO ticks (tradable, mode, instrument_token, date, last_price, last_quantity, average_price, volume, buy_quantity, sell_quantity, ohlc_open, ohlc_high, ohlc_low, ohlc_close, change) VALUES (%(tradable)s, %(mode)s, %(instrument_token)s, %(date)s, %(last_price)s, %(last_quantity)s, %(average_price)s, %(volume)s, %(buy_quantity)s, %(sell_quantity)s, %(ohlc_open)s, %(ohlc_high)s, %(ohlc_low)s, %(ohlc_close)s, %(change)s)"""
# insert_tick_statement = "INSERT INTO ticks (date, token, price) VALUES (%(date)s, %(token)s, %(price)s)"


# Task to insert to SQLite db
@app.task
def insert_ticks(ticks):
    c = db.cursor()
    for tick in ticks:
        c.execute(insert_tick_statement, {
            "tradable": tick.get("tradable"),
            "mode": tick.get("mode"),
            "instrument_token": tick.get("instrument_token"),
            "date": datetime.now(),
            "last_price": tick.get("last_price"),
            "last_quantity": tick.get("last_quantity"),
            "average_price": tick.get("average_price"),
            "volume": tick.get("volume"),
            "buy_quantity": tick.get("buy_quantity"),
            "sell_quantity": tick.get("sell_quantity"),
            "ohlc_open": tick.get("ohlc").get('open'),
            "ohlc_high": tick.get("ohlc").get('high'),
            "ohlc_low": tick.get("ohlc").get('low'),
            "ohlc_close": tick.get("ohlc").get('close'),
            "change": tick.get("change")})
        # c.execute(insert_tick_statement, {
        #     "date": datetime.now(),
        #     "token": tick["instrument_token"],
        #     "price": tick["last_price"]})

    # logging.info("Inserting ticks to db : {}".format(json.dumps(ticks)))

    try:
        db.commit()
        logging.info("************Insert successful**************")
    except Exception:
        db.rollback()
        logging.exception("Couldn't write ticks to db: ")



# CREATE TABLE ticks (
#     tradable text,
#     mode text,
#     instrument_token integer NOT NULL,
#     date timestamp without time zone,
#     last_price double precision,
#     last_quantity integer,
#     average_price double precision,
#     volume integer,
#     buy_quantity integer,
#     sell_quantity integer,
#     ohlc_open double precision,
#     ohlc_high double precision,
#     ohlc_low double precision,
#     ohlc_close double precision,
#     change double precision
# );
