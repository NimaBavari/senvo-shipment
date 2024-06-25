import unittest
from unittest.mock import patch

from custom_exceptions import InputValidationError
from main import app


class TestShipmentAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch("main.shipment_repo")
    def test_create_shipments_no_data(self, mock_shipment_repo):
        response = self.app.post("/shipments/", json=[])
        self.assertEqual(response.status_code, 400)
        self.assertIn("No data provided", response.get_json()["error"])

    @patch("main.shipment_repo")
    def test_create_shipments_invalid_data(self, mock_shipment_repo):
        mock_shipment_repo.insert_shipments.side_effect = InputValidationError("Missing fields")
        data = [{"shipment_date": "2022-07-15"}]
        response = self.app.post("/shipments/", json=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid data format or missing required fields", response.get_json()["error"])

    @patch("main.shipment_repo")
    def test_create_shipments_valid_data(self, mock_shipment_repo):
        data = [
            {
                "shipment_date": "2022-07-15",
                "addr_line_1": "123 Main St",
                "addr_line_2": "Apt 4",
                "postal_code": "12345",
                "city": "Anytown",
                "country_code": "USA",
                "length": 15,
                "width": 10,
                "height": 8,
                "weight": 10,
                "price_amt": 100,
                "price_currency": "USD",
                "carrier": "dhl-express",
            }
        ]
        response = self.app.post("/shipments/", json=data)
        self.assertEqual(response.status_code, 201)
        self.assertIn("Shipments created successfully", response.get_json()["message"])
        mock_shipment_repo.insert_shipments.assert_called_once()

    @patch("main.shipment_repo")
    def test_get_shipments_malformed_params(self, mock_shipment_repo):
        response = self.app.get("/shipments/", query_string={"wrong_param": "value"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Malformed query params", response.get_json()["error"])

    @patch("main.shipment_repo")
    def test_get_shipments_valid_params(self, mock_shipment_repo):
        mock_shipment_repo.fetch_shipments.return_value = [{"shipment_id": 1, "carrier": "dhl-express"}]
        response = self.app.get(
            "/shipments/", query_string={"carrier": "dhl-express", "date": "2020-01-01:2020-01-31", "price": "100:500"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [{"shipment_id": 1, "carrier": "dhl-express"}])

    @patch("main.shipment_repo")
    def test_get_shipments_no_params(self, mock_shipment_repo):
        mock_shipment_repo.fetch_shipments.return_value = [{"shipment_id": 1, "carrier": "dhl-express"}]
        response = self.app.get("/shipments/", query_string={})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [{"shipment_id": 1, "carrier": "dhl-express"}])


if __name__ == "__main__":
    unittest.main()
