extends Control

@onready var test_button = $VBoxContainer/TestButton
@onready var result_label = $VBoxContainer/ResultLabel
@onready var physics_manager = $PhysicsManager

func _ready():
    test_button.pressed.connect(self._on_test_button_pressed)
    physics_manager.physics_query_completed.connect(self._on_physics_query_completed)

func _on_test_button_pressed():
    result_label.text = "Querying..."
    # Test the "is_area_clear" query with a position that should be clear
    physics_manager.query_is_area_clear(Vector3(0, 0, 0))

func _on_physics_query_completed(response):
    if response.success:
        result_label.text = f"Query '{response.query_type}' result: {response.result}"
    else:
        result_label.text = "Query failed."
