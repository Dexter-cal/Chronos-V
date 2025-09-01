extends Control

func _ready():
    # Connect the button signals to the script's functions
    $CenterContainer/VBoxContainer/ResumeButton.pressed.connect(self._on_resume_button_pressed)
    $CenterContainer/VBoxContainer/SettingsButton.pressed.connect(self._on_settings_button_pressed)
    $CenterContainer/VBoxContainer/QuitButton.pressed.connect(self._on_quit_button_pressed)

func _on_resume_button_pressed():
    # The logic for un-pausing will be handled in the main scene script
    # For now, this just hides the pause menu
    self.hide()
    get_tree().paused = false

func _on_settings_button_pressed():
    print("Settings button pressed - functionality to be implemented.")
    # This is a placeholder for the settings menu functionality

func _on_quit_button_pressed():
    get_tree().quit()
