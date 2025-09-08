# MapService.gd
extends Node

signal map_fetched(map_data)

var http_request = HTTPRequest.new()

func _ready():
    add_child(http_request)
    http_request.request_completed.connect(_on_request_completed)

func fetch_map():
    print("Fetching map from orchestrator...")
    var error = http_request.request("http://127.0.0.1:8000/generate_map")
    if error != OK:
        print("An error occurred in the HTTP request.")

func _on_request_completed(result, response_code, headers, body):
    if response_code == 200:
        var json = JSON.parse_string(body.get_string_from_utf8())
        if json:
            var map_data = json.get("map")
            if map_data:
                print("Map data fetched successfully.")
                map_fetched.emit(map_data)
            else:
                print("Error: 'map' key not found in JSON response.")
        else:
            print("Error: Could not parse JSON response.")
    else:
        print("Error: HTTP request failed with code " + str(response_code))
