extends Node

const ORCHESTRATOR_URL = "http://127.0.0.1:8000"

# This function would be called from a UI element, like a chat box.
func send_command(player_id: String, command_text: String, context: Dictionary):
    var http_request = HTTPRequest.new()
    add_child(http_request)
    http_request.request_completed.connect(self._on_request_completed)

    var body = JSON.stringify({
        "player_id": player_id,
        "request_text": command_text,
        "game_context": context
    })
    var headers = ["Content-Type: application/json"]
    var error = http_request.request(ORCHESTRATOR_URL + "/assistive_ai_command", headers, HTTPClient.METHOD_POST, body)
    if error != OK:
        print("An error occurred in the HTTP request.")

func _on_request_completed(result, response_code, headers, body):
    if response_code == 200:
        var json = JSON.parse_string(body.get_string_from_utf8())
        print("Assistive AI says: ", json.response_text)
        # Here you would display the response in the game's UI.
    else:
        print("Failed to get response from Assistive AI. Response code: ", response_code)
