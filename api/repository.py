from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple

import psycopg2
import psycopg2.extras
from annotated_types import Gt
from custom_exceptions import FetchError, InputValidationError, InsertionError
from db import SHIPMENT_TBL_SCM, conn
from pydantic import BaseModel, ValidationError
from typing_extensions import Annotated


class ShipmentInput(BaseModel):
    shipment_date: date
    addr_line_1: str
    addr_line_2: Optional[str] = None
    postal_code: str
    city: str
    country_code: str
    length: float
    width: float
    height: float
    weight: float
    price_amt: Annotated[float, Gt(0)]
    price_currency: str
    carrier: str


class ShipmentRepository(ABC):
    @abstractmethod
    def insert_shipments(self, shipments_data: List[Dict[str, str]]) -> None:
        pass

    @abstractmethod
    def fetch_shipments(self, query_params: Dict[str, str]) -> List[Tuple[Any, ...]]:
        pass


class PostgreSQLShipmentRepository(ShipmentRepository):
    def __init__(self) -> None:
        self.conn: psycopg2.extensions.connection = conn
        self.cursor: psycopg2.extensions.cursor = self.conn.cursor()
        self.cursor.execute(SHIPMENT_TBL_SCM)
        self.conn.commit()

    def insert_shipments(self, shipments_data: List[Dict[str, str]]) -> None:
        try:
            values = [
                ShipmentInput(
                    shipment_date=datetime.strptime(shipment["shipment_date"], "%Y-%m-%d"),
                    addr_line_1=shipment["addr_line_1"],
                    addr_line_2=shipment.get("addr_line_2"),
                    postal_code=shipment["postal_code"],
                    city=shipment["city"],
                    country_code=shipment["country_code"],
                    length=float(shipment["length"]),
                    width=float(shipment["width"]),
                    height=float(shipment["height"]),
                    weight=float(shipment["weight"]),
                    price_amt=float(shipment["price_amt"]),
                    price_currency=shipment["price_currency"],
                    carrier=shipment["carrier"],
                )
                for shipment in shipments_data
            ]
        except (KeyError, ValueError, TypeError, ValidationError):
            raise InputValidationError

        insert_address_query = """
        INSERT INTO shipment_addresses (addr_line_1, addr_line_2, postal_code, city, country_code)
        VALUES %s ON CONFLICT (addr_line_1, addr_line_2, postal_code, city, country_code)
        DO UPDATE SET addr_line_1 = EXCLUDED.addr_line_1
        RETURNING id;
        """

        insert_shipment_query = """
        INSERT INTO shipments (address_id, shipment_date, length, width, height, weight, price_amt, price_currency, carrier)
        VALUES %s;
        """

        address_records = [(v.addr_line_1, v.addr_line_2, v.postal_code, v.city, v.country_code) for v in values]
        try:
            psycopg2.extras.execute_values(
                self.cursor, insert_address_query, address_records, template=None, page_size=100
            )
            address_ids = self.cursor.fetchall()
            shipment_tbl_data = [
                (
                    address_ids[idx][0],
                    v.shipment_date,
                    v.length,
                    v.width,
                    v.height,
                    v.price_amt,
                    v.price_currency,
                    v.carrier,
                )
                for idx, v in enumerate(values)
            ]
            psycopg2.extras.execute_values(
                self.cursor, insert_shipment_query, shipment_tbl_data, template=None, page_size=100
            )
            self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            raise InsertionError from e

    def fetch_shipments(self, query_params: Dict[str, str]) -> List[Tuple[Any, ...]]:
        query = "SELECT * FROM shipments"
        vars = []

        conditions = []
        if "date" in query_params:
            try:
                start_date, end_date = query_params["date"].split(":")
            except ValueError:
                raise InputValidationError

            conditions.append("shipment_date BETWEEN %s AND %s")
            vars.extend([start_date, end_date])

        if "price" in query_params:
            try:
                start_price, end_price = query_params["price"].split(":")
            except ValueError:
                raise InputValidationError

            conditions.append("price_amt BETWEEN %s AND %s")
            vars.extend([start_price, end_price])

        if "carrier" in query_params:
            conditions.append("carrier = %s")
            vars.append(query_params["carrier"])

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += ";"

        try:
            self.cursor.execute(query, vars)
        except psycopg2.Error:
            raise FetchError

        return self.cursor.fetchall()
