import unittest

from items import (
    get_item_info,
    get_shop_categories,
    inventory_item_from_shop_id,
    normalize_inventory,
    normalize_inventory_item,
)


class ItemsTests(unittest.TestCase):
    def test_shop_id_maps_to_inventory_id(self):
        self.assertEqual(inventory_item_from_shop_id("bab"), "사료")
        self.assertEqual(inventory_item_from_shop_id("bone"), "뼈")
        self.assertIsNone(inventory_item_from_shop_id("unknown"))

    def test_inventory_aliases_are_normalized_and_merged(self):
        inventory = normalize_inventory({"bab": 1, "밥": 2, "사료": 3, "풀밭": 4})

        self.assertEqual(inventory["사료"], 6)
        self.assertEqual(inventory["강아지풀"], 4)

    def test_inventory_normalization_drops_non_positive_counts(self):
        self.assertEqual(normalize_inventory({"bab": 0, "fish": -2, "chur": "bad"}), {})

    def test_item_info_accepts_legacy_keys(self):
        self.assertEqual(get_item_info("doggrass")["name"], "강아지풀")
        self.assertEqual(get_item_info("풀밭")["name"], "강아지풀")

    def test_shop_categories_return_copies(self):
        categories = get_shop_categories()
        categories["FOOD"][0]["price"] = 999

        self.assertNotEqual(get_shop_categories()["FOOD"][0]["price"], 999)
        self.assertEqual(normalize_inventory_item("fish"), "생선")


if __name__ == "__main__":
    unittest.main()
