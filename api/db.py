import os

import psycopg2
from logger_setup import setup_logger

SHIPMENT_TBL_SCM = """do $$
begin
    perform pg_advisory_xact_lock(123456);

    if not exists (select from pg_extension where extname = 'pgcrypto') then
        create extension pgcrypto;
    end if;

    create table if not exists shipment_addresses(
        id uuid DEFAULT gen_random_uuid(),
        addr_line_1 VARCHAR(255) NOT NULL,
        addr_line_2 VARCHAR(255),
        postal_code VARCHAR(50) NOT NULL,
        city VARCHAR(100) NOT NULL,
        country_code CHAR(2) NOT NULL,
        primary key (id)
    );

    create table if not exists shipments(
        tracking_no uuid DEFAULT gen_random_uuid(),
        address_id uuid,
        shipment_date DATE,
        length NUMERIC(10, 2) NOT NULL,
        width NUMERIC(10, 2) NOT NULL,
        height NUMERIC(10, 2) NOT NULL,
        weight NUMERIC(10, 2) NOT NULL,
        price_amt NUMERIC(10, 2) NOT NULL,
        price_currency CHAR(3) NOT NULL,
        carrier VARCHAR(11) CHECK (carrier in ('dhl-express', 'ups', 'fedex')),
        primary key (tracking_no),
        constraint fk_address foreign key (address_id) references shipment_addresses (id)
    );
end $$"""

conn_str = os.getenv("DATABASE_URL")

logger = setup_logger()

conn: psycopg2.extensions.connection | None = None
try:
    conn = psycopg2.connect(conn_str)
except psycopg2.OperationalError as e:
    logger.error("Connection failed: %s" % e)
    raise
