extends Node

const ORCHESTRATOR_URL = "http://127.0.0.1:8000"

var current_difficulty_settings = {}

func _ready():
    # Fetch initial difficulty settings when the manager is ready
    fetch_difficulty_settings()

func send_player_event(event_type: String, payload: Dictionary):
    var http_request = HTTPRequest.new()
    add_child(http_request)
    # Not connecting the completed signal for fire-and-forget events

    var body = JSON.stringify({"event_type": event_type, "payload": payload})
    var headers = ["Content-Type: application/json"]
    http_request.request(ORCHESTRATOR_URL + "/player_event", headers, HTTPClient.METHOD_POST, body)

func fetch_difficulty_settings():
    var http_request = HTTPRequest.new()
    add_child(http_request)
    http_request.request_completed.connect(self._on_fetch_completed)
    http_request.request(ORCHESTRATOR_URL + "/difficulty_settings")

func _on_fetch_completed(result, response_code, headers, body):
    if response_code == 200:
        var json = JSON.parse_string(body.get_string_from_utf8())
        current_difficulty_settings = json
        print("Difficulty settings updated: ", current_difficulty_settings)
        # Here you would apply these settings to the game
    else:
        print("Failed to fetch difficulty settings. Response code: ", response_code)
