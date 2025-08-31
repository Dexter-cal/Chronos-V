extends Node

const ORCHESTRATOR_URL = "http://127.0.0.1:8000"

# This would be triggered when the game detects the player is struggling
func request_hint(player_id: String, context: Dictionary):
    var http_request = HTTPRequest.new()
    add_child(http_request)
    http_request.request_completed.connect(self._on_hint_request_completed)

    var body = JSON.stringify({"player_id": player_id, "context": context})
    var headers = ["Content-Type: application/json"]
    http_request.request(ORCHESTRATOR_URL + "/get_hint", headers, HTTPClient.METHOD_POST, body)

func _on_hint_request_completed(result, response_code, headers, body):
    if response_code == 200:
        var json = JSON.parse_string(body.get_string_from_utf8())
        print("Hint received: ", json.hint_text)
        # Here you would display the hint in the UI
    else:
        print("Failed to get hint. Response code: ", response_code)
