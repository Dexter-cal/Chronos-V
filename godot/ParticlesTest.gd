extends Control

@onready var test_button = $VBoxContainer/TestButton
@onready var particles_manager = $ParticlesManager

func _ready():
    test_button.pressed.connect(self._on_test_button_pressed)

func _on_test_button_pressed():
    # Request a "campfire" particle effect at the center of the screen
    particles_manager.request_particle_effect("campfire", Vector3(0, 0, 0))
