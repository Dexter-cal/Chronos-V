# MapScene.gd
extends Node2D

var map_service = load("res://MapService.gd").new()

func _ready():
    add_child(map_service)
    map_service.map_fetched.connect(_on_map_fetched)

    print("MapScene ready. Requesting map...")
    map_service.fetch_map()

func _on_map_fetched(map_data):
    print("Map received in MapScene! Printing map:")
    for y in range(map_data.size()):
        var row_str = ""
        for x in range(map_data[y].size()):
            row_str += map_data[y][x]
        print(row_str)
