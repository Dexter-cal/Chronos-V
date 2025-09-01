extends Node

@onready var pause_menu = $PauseMenu

func _unhandled_input(event):
    if event.is_action_pressed("ui_cancel"): # "ui_cancel" is the default mapping for the Escape key
        if get_tree().paused:
            # If the game is paused, unpause it and hide the menu
            get_tree().paused = false
            pause_menu.hide()
        else:
            # If the game is not paused, pause it and show the menu
            get_tree().paused = true
            pause_menu.show()
