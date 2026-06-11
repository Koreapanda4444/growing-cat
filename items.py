from config import asset_path


ITEM_INFO = {
    "사료": {"name": "밥", "image": asset_path("foods", "bab.png")},
    "생선": {"name": "생선", "image": asset_path("foods", "fish.png")},
    "츄르": {"name": "츄르", "image": asset_path("foods", "chur.png")},
    "고기": {"name": "고기", "image": asset_path("evolution", "meat.png")},
    "강아지풀": {"name": "강아지풀", "image": asset_path("toys", "doggrass.png")},
    "낚싯대": {"name": "낚싯대", "image": asset_path("toys", "fishing.png")},
    "실": {"name": "실", "image": asset_path("toys", "string.png")},
    "뼈": {"name": "뼈", "image": asset_path("evolution", "bone.png")},
}

SHOP_CATEGORIES = {
    "FOOD": [
        {"name": "밥", "price": 25, "id": "bab", "image": asset_path("foods", "bab.png")},
        {"name": "생선", "price": 45, "id": "fish", "image": asset_path("foods", "fish.png")},
        {"name": "츄르", "price": 70, "id": "chur", "image": asset_path("foods", "chur.png")},
    ],
    "TOY": [
        {"name": "강아지풀", "price": 25, "id": "doggrass", "image": asset_path("toys", "doggrass.png")},
        {"name": "낚싯대", "price": 65, "id": "fishing", "image": asset_path("toys", "fishing.png")},
        {"name": "실", "price": 45, "id": "string", "image": asset_path("toys", "string.png")},
    ],
    "EVOLUTION": [
        {"name": "고기", "price": 120, "id": "meat", "image": asset_path("evolution", "meat.png")},
        {"name": "뼈", "price": 260, "id": "bone", "image": asset_path("evolution", "bone.png")},
    ],
}

SHOP_ID_TO_INVENTORY_ID = {
    "bab": "사료",
    "fish": "생선",
    "chur": "츄르",
    "meat": "고기",
    "doggrass": "강아지풀",
    "fishing": "낚싯대",
    "string": "실",
    "bone": "뼈",
}

ITEM_ALIASES = {
    **SHOP_ID_TO_INVENTORY_ID,
    "밥": "사료",
    "풀밭": "강아지풀",
}


def get_shop_categories() -> dict[str, list[dict]]:
    return {
        category: [dict(item) for item in items]
        for category, items in SHOP_CATEGORIES.items()
    }


def normalize_inventory_item(item_id: str) -> str:
    item = str(item_id)
    return ITEM_ALIASES.get(item, item)


def normalize_inventory(inventory) -> dict[str, int]:
    if not isinstance(inventory, dict):
        return {}

    normalized = {}
    for key, value in inventory.items():
        if not isinstance(key, str):
            continue
        try:
            amount = int(value)
        except (TypeError, ValueError):
            continue
        if amount <= 0:
            continue
        item_id = normalize_inventory_item(key)
        normalized[item_id] = normalized.get(item_id, 0) + amount
    return normalized


def inventory_item_from_shop_id(item_id: str) -> str | None:
    return SHOP_ID_TO_INVENTORY_ID.get(str(item_id))


def get_item_info(item_id: str) -> dict:
    return ITEM_INFO.get(normalize_inventory_item(item_id), {})
