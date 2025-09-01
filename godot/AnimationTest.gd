extends Control

@onready var test_button = $VBoxContainer/TestButton
@onready var result_label = $VBoxContainer/ResultLabel
@onready var animation_manager = $AnimationManager

func _ready():
    test_button.pressed.connect(self._on_test_button_pressed)
    # The AnimationManager does not emit a signal in its current design,
    # as it directly processes the animation queue.
    # For testing purposes, we can't easily see the result here.
    # We will rely on the `curl` test to verify the server's response.

func _on_test_button_pressed():
    result_label.text = "Requesting animation..."
    # Test the animation request with some sample data
    animation_manager.request_animation(
        "Hello, player! Welcome to ChronoVerse.",
        "happy",
        "greeting_player"
    )
    result_label.text = "Animation request sent."
