# Senvo Shipment Simple API & Logger

by Tural Mahmudov

## Notes for Reviewer

This is a fully dockerized system comprising of 4 services: `redis`, `db`, `api`, and `log-consumer`.

The system is fully covered with unit tests.

The architecture is defined by minimalistic, yet clean and type-checked code. I maintain strict coding standards to enhance idiomacy, readability, and consistency, significantly reducing technical debt.

**Database Design.** The data model comprises two primary tables: `shipments` and `shipment_addresses`. The `shipments` table uses `tracking_no` as its primary key and `address_id` as a foreign key. The foreign key corresponds to the primary key in the `shipment_addresses` table. This design supports the recurring scenario where a single address is linked to multiple shipments, thereby establishing a one-to-many relationship between `shipment_addresses` and `shipments`.

I avoided using large frameworks including ORMs, save for the very minimal Flask and Pydantic. Even though the code is well-organised and adheres to the best practices, in particular, SOLID principles, most everything has been custom implemented.

In particular, I have implemented a repository layer between the DB connection and the API. The repository handles the DB interaction and masks direct exceptions that arise from the DB driver, exposing only custom, more friendly exceptions that concern the API.

I have a logger with a custom handler that publishes the log messages to a Redis channel, which is almost exclusively at the responsibility of the API. Any monitoring tool -- a simple log consumer in our case -- can then subscribe and listen to this channel, and use the streamed log messages for any purpose.

## Usage

### Startup

You can start the entire system by running

```sh
docker-compose up -d
```

In order to only start up an individual service, run

```sh
docker-compose up -d <service-name>
```

### Monitoring

You can get the entire docker logs by running

```sh
docker-compose logs --follow
```

or, alternately, you can get the logs from an individual container by running

```sh
docker container logs <container-name> --follow
```

### REST API

After the services are up, issue a GET request to the following endpoint: `localhost:5050/shipments` to view all shipments.

This endpoint supports various query parameters for filtering the results, as detailed below. Filters are applied additively when multiple parameters are used.

Available query parameters are:

* carrier: Filters shipments by carrier. Acceptable values are "dhl-express", "ups", or "fedex"
* price: Specifies a price range for filtering. Format this parameter as start_price:end_price
* date: Specifies a date range for filtering. Use the format start_date:end_date, with dates in YYYY-MM-DD format.

Example request:

GET http://localhost:5050/shipments?date=2023-01-01:2023-01-31&price=100:500&carrier=dhl-express

This request retrieves all shipments for dhl-express from January 1, 2023, to January 31, 2023, within the price range of 100 to 500.

Or, issue a POST request to the same endpoint `localhost:5050/shipments` with a request of the following format:

```
[
    {
        shipment_date: str,
        addr_line_1: str,
        addr_line_2: str (optional),
        postal_code: str,
        city: str,
        country_code: str,
        length: str,
        width: str,
        height: str,
        weight: str,
        price_amt: str,
        price_currency: str,
        carrier: str,
    },
    ...
]
```

### Testing

To run tests, run:

```sh
docker exec senvo-shipment_api_1 python3 -m unittest
```

Note that that container must be already up in order for you to be able to run the above command.

## Scripts

To lint, format, and check static typing, run:

```sh
chmod +x lint.sh
./lint.sh
```

from the project root.
