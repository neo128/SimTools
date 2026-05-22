from simtools.adapters.ai2thor_scenes import ITHOR_SCENE_GROUPS, ithor_scenes, room_type_for_scene


def test_ithor_scene_groups_match_public_numbering():
    assert len(ithor_scenes()) == 120
    assert ITHOR_SCENE_GROUPS["Kitchens"][0] == "FloorPlan1"
    assert ITHOR_SCENE_GROUPS["Kitchens"][-1] == "FloorPlan30"
    assert ITHOR_SCENE_GROUPS["Living rooms"][0] == "FloorPlan201"
    assert ITHOR_SCENE_GROUPS["Living rooms"][-1] == "FloorPlan230"
    assert ITHOR_SCENE_GROUPS["Bedrooms"][0] == "FloorPlan301"
    assert ITHOR_SCENE_GROUPS["Bedrooms"][-1] == "FloorPlan330"
    assert ITHOR_SCENE_GROUPS["Bathrooms"][0] == "FloorPlan401"
    assert ITHOR_SCENE_GROUPS["Bathrooms"][-1] == "FloorPlan430"


def test_room_type_for_scene_accepts_public_and_physics_names():
    assert room_type_for_scene("FloorPlan1") == "Kitchens"
    assert room_type_for_scene("FloorPlan1_physics") == "Kitchens"
    assert room_type_for_scene("FloorPlan201") == "Living rooms"
    assert room_type_for_scene("FloorPlan301") == "Bedrooms"
    assert room_type_for_scene("FloorPlan401") == "Bathrooms"
    assert room_type_for_scene("Procedural") is None
