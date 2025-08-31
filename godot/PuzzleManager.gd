extends Node

const ORCHESTRATOR_URL = "http://127.0.0.1:8000"

func request_puzzle(context: Dictionary) -> void:
    var http_request = HTTPRequest.new()
    add_child(http_request)
    http_request.request_completed.connect(self._on_request_completed)

    var body = JSON.stringify(context)
    var headers = ["Content-Type: application/json"]
    var error = http_request.request(ORCHESTRATOR_URL + "/generate_puzzle", headers, HTTPClient.METHOD_POST, body)
    if error != OK:
        print("An error occurred in the HTTP request.")

func _on_request_completed(result, response_code, headers, body):
    if response_code == 200:
        var json = JSON.parse_string(body.get_string_from_utf8())
        print("Puzzle received: ", json)
        # Here we would instantiate the puzzle in the game world based on the received data.
    else:
        print("Failed to get puzzle. Response code: ", response_code)
