from simtools.ui.ai2thor_app import action_status, object_action_specs, visible_object_options


def test_visible_object_options_filters_and_sorts():
    objects = [
        {
            "objectId": "Mug|1",
            "objectType": "Mug",
            "name": "Mug",
            "visible": True,
            "distance": 1.25,
            "pickupable": True,
        },
        {
            "objectId": "Hidden|1",
            "objectType": "Hidden",
            "visible": False,
        },
    ]

    options = visible_object_options(objects)

    assert len(options) == 1
    assert options[0]["object_id"] == "Mug|1"
    assert options[0]["pickupable"] is True
    assert "1.25m" in options[0]["label"]


def test_object_action_specs_reflect_object_state():
    option = {
        "pickupable": True,
        "openable": True,
        "is_open": False,
        "toggleable": True,
        "is_toggled": True,
        "receptacle": True,
    }

    specs = object_action_specs(option)

    assert {"label": "Pick up", "action": "PickupObject"} in specs
    assert {"label": "Open", "action": "OpenObject"} in specs
    assert {"label": "Toggle off", "action": "ToggleObjectOff"} in specs
    assert {"label": "Put held object", "action": "PutObject"} in specs


def test_action_status_formats_success_and_failure():
    assert action_status({"lastAction": "MoveAhead", "lastActionSuccess": True}) == "MoveAhead: ok"
    assert (
        action_status(
            {
                "lastAction": "OpenObject",
                "lastActionSuccess": False,
                "errorMessage": "not visible",
            }
        )
        == "OpenObject: failed not visible"
    )
