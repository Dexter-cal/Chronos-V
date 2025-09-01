extends Node

const ORCHESTRATOR_URL = "http://127.0.0.1:8000"

# Signal to notify other nodes when a physics query is complete
signal physics_query_completed(response)

func query_is_area_clear(position: Vector3):
    var query_params = {
        "position": {"x": position.x, "y": position.y, "z": position.z}
    }
    _send_physics_query("is_area_clear", query_params)

func query_surface_material(position: Vector3):
    var query_params = {
        "position": {"x": position.x, "y": position.y, "z": position.z}
    }
    _send_physics_query("get_surface_material", query_params)

func query_trajectory(start_point: Vector3, end_point: Vector3):
    var query_params = {
        "start": {"x": start_point.x, "y": start_point.y, "z": start_point.z},
        "end": {"x": end_point.x, "y": end_point.y, "z": end_point.z}
    }
    _send_physics_query("calculate_trajectory", query_params)

func _send_physics_query(query_type: String, parameters: Dictionary):
    var http_request = HTTPRequest.new()
    add_child(http_request)
    http_request.request_completed.connect(self._on_request_completed)

    var body = JSON.stringify({
        "query_type": query_type,
        "parameters": parameters
    })
    var headers = ["Content-Type: application/json"]
    var error = http_request.request(ORCHESTRATOR_URL + "/physics_query", headers, HTTPClient.METHOD_POST, body)
    if error != OK:
        print("An error occurred in the HTTP request.")

func _on_request_completed(result, response_code, headers, body):
    if response_code == 200:
        var json = JSON.parse_string(body.get_string_from_utf8())
        emit_signal("physics_query_completed", json)
    else:
        print("Failed to get response from Physics AI. Response code: ", response_code)
        emit_signal("physics_query_completed", {"success": false, "result": null})
