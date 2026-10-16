import unittest
from unittest.mock import patch

from yummy_app import YummyApp
import gps_service


# ================================================================
# CAP DO 1: Bo test co ban (chi dat ~35% Coverage)
# ================================================================
class TestEasyLevel(unittest.TestCase):
    """Kiem thu chuc nang co ban tinh tien don hang"""

    def setUp(self):
        self.app = YummyApp()

    def test_calculate_total_for_single_item(self):
        cart = {"pho": 2}
        self.assertEqual(self.app.calculate_order_total(cart), 100000)

    def test_calculate_total_for_multiple_items(self):
        cart = {"pho": 1, "bun": 1}
        self.assertEqual(self.app.calculate_order_total(cart), 95000)

    def test_calculate_total_for_empty_cart(self):
        self.assertEqual(self.app.calculate_order_total({}), 0.0)

    def test_calculate_total_with_zero_quantity(self):
        cart = {"pho": 0}
        self.assertEqual(self.app.calculate_order_total(cart), 0.0)


# ================================================================
# CAP DO 2 (TIET 3): 4 test case cho apply_promo_code
# ================================================================
class TestMediumLevel(unittest.TestCase):

    # TC1: online + ma hop le -> duoc giam 10%
    def test_online_valid_code(self):
        app = YummyApp(network_status="online", os_version=15)
        self.assertEqual(app.apply_promo_code(100000, "GIAM10"), 90000)

    # TC2: offline -> khong xac thuc duoc ma -> bao loi ket noi
    def test_offline(self):
        app = YummyApp(network_status="offline")
        with self.assertRaises(ConnectionError):
            app.apply_promo_code(100000, "GIAM10")

    # TC3: ma NEW_OS_ONLY tren OS 15 (du dieu kien) -> giam 20%
    def test_special_code_os15(self):
        app = YummyApp(network_status="online", os_version=15)
        self.assertEqual(app.apply_promo_code(100000, "NEW_OS_ONLY"), 80000)

    # TC4: ma NEW_OS_ONLY tren OS 14 (khong du dieu kien) -> bao loi
    def test_special_code_os14(self):
        app = YummyApp(network_status="online", os_version=14)
        with self.assertRaises(ValueError):
            app.apply_promo_code(100000, "NEW_OS_ONLY")


# ================================================================
# CAP DO 2 (TIET 3): 3 test case cho get_nearby_restaurants
# Dung @patch de gia lap GPS (khong can dien thoai that)
# ================================================================
class TestHardLevel(unittest.TestCase):
    
    # TC5: GPS tra ve (10.0, 105.0) -> co 2 nha hang
    @patch('yummy_app.gps_service.get_current_location')
    def test_gps_in_area(self, mock_gps):
        mock_gps.return_value = (10.0, 105.0)
        result = YummyApp().get_nearby_restaurants()
        self.assertEqual(len(result), 2)

    # TC6: GPS tra ve (20.0, 110.0) -> khong co nha hang nao
    @patch('yummy_app.gps_service.get_current_location')
    def test_gps_out_of_area(self, mock_gps):
        mock_gps.return_value = (20.0, 110.0)
        self.assertEqual(YummyApp().get_nearby_restaurants(), [])

    # TC7: GPS mat tin hieu -> tra ve thong bao loi
    @patch('yummy_app.gps_service.get_current_location')
    def test_gps_signal_lost(self, mock_gps):
        mock_gps.side_effect = gps_service.GPSSignalLostError()
        self.assertEqual(
            YummyApp().get_nearby_restaurants(), "Khong the xac dinh vi tri."
        )


if __name__ == '__main__':
    unittest.main()