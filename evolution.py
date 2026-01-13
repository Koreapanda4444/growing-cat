BABY = "아기고양이"
ADULT = "어른고양이"
LION = "사자고양이"
DINO = "공룡고양이"

EVOLUTION_ORDER = [BABY, ADULT, LION, DINO]

EVOLUTION_COST = {
    BABY: 100,
    ADULT: 500,
    LION: 1000,
}

def get_next_stage(stage):
    if stage not in EVOLUTION_ORDER:
        return None
    idx = EVOLUTION_ORDER.index(stage)
    if idx + 1 >= len(EVOLUTION_ORDER):
        return None
    return EVOLUTION_ORDER[idx + 1]

def can_evolve(cat, day, coin, has_meat=False, has_bone=False):
    next_stage = get_next_stage(cat.stage)
    if not next_stage:
        return False, "최종 단계입니다"

    cost = EVOLUTION_COST[cat.stage]
    if coin < cost:
        return False, f"코인 {cost} 필요"

    if cat.stage == BABY:
        if day < 7:
            return False, "7일 필요"
        return True, "진화 가능"

    if cat.stage == ADULT:
        if day < 21 or not has_meat:
            return False, "21일 + 고기 필요"
        if cat.happiness < 75 or cat.tiredness > 25 or cat.cleanliness < 75 or cat.hunger > 25:
            return False, "스탯 부족"
        return True, "진화 가능"

    if cat.stage == LION:
        if day < 35 or not has_bone:
            return False, "35일 + 뼈 필요"
        if cat.happiness < 80 or cat.tiredness > 15 or cat.cleanliness < 80 or cat.hunger > 15:
            return False, "스탯 부족"
        return True, "진화 가능"

    return False, "불가"


def evolve(cat):
    next_stage = get_next_stage(getattr(cat, "stage", None))
    if not next_stage:
        return False

    if hasattr(cat, "evolve_to") and callable(getattr(cat, "evolve_to")):
        cat.evolve_to(next_stage)
    else:
        cat.stage = next_stage

    return True
