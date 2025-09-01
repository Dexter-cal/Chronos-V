extends Node

# This manager would be attached to an NPC scene that has a 3D model with blend shapes and an AnimationPlayer

const ORCHESTRATOR_URL = "http://127.0.0.1:8000"

@onready var facial_mesh = $Path/To/FacialMesh # Path to the MeshInstance3D with blend shapes
@onready var animation_player = $Path/To/AnimationPlayer # Path to the AnimationPlayer for body animations

var viseme_queue = []
var animation_trigger_queue = []
var current_time = 0.0

func _process(delta):
    current_time += delta
    _process_viseme_queue()
    _process_animation_trigger_queue()

func request_animation(text: String, emotional_context: String, narrative_context: String):
    var http_request = HTTPRequest.new()
    add_child(http_request)
    http_request.request_completed.connect(self._on_request_completed)

    var body = JSON.stringify({
        "text": text,
        "emotional_context": emotional_context,
        "narrative_context": narrative_context
    })
    var headers = ["Content-Type: application/json"]
    var error = http_request.request(ORCHESTRATOR_URL + "/generate_animation", headers, HTTPClient.METHOD_POST, body)
    if error != OK:
        print("An error occurred in the HTTP request.")

func _on_request_completed(result, response_code, headers, body):
    if response_code == 200:
        var json = JSON.parse_string(body.get_string_from_utf8())
        viseme_queue = json.visemes
        animation_trigger_queue = json.animation_triggers
        current_time = 0.0 # Reset the timer for the new animation sequence
    else:
        print("Failed to get response from Animation AI. Response code: ", response_code)

func _process_viseme_queue():
    if viseme_queue.empty():
        return

    var next_viseme = viseme_queue.front()
    if current_time >= next_viseme.timestamp:
        _apply_viseme(next_viseme.viseme_name)
        viseme_queue.pop_front()

func _process_animation_trigger_queue():
    if animation_trigger_queue.empty():
        return

    var next_trigger = animation_trigger_queue.front()
    if current_time >= next_trigger.timestamp:
        _play_body_animation(next_trigger.animation_name)
        animation_trigger_queue.pop_front()

func _apply_viseme(viseme_name: String):
    # This function would set the blend shape weights on the facial_mesh
    # to create the desired lip shape.
    # For example:
    # for i in range(facial_mesh.get_blend_shape_count()):
    #     facial_mesh.set_blend_shape_weight(i, 0.0)
    # var viseme_index = facial_mesh.find_blend_shape_by_name(viseme_name)
    # if viseme_index != -1:
    #     facial_mesh.set_blend_shape_weight(viseme_index, 1.0)
    print(f"Applying viseme: {viseme_name} at time {current_time}")

func _play_body_animation(animation_name: String):
    # This function would play the specified animation on the animation_player.
    if animation_player.has_animation(animation_name):
        animation_player.play(animation_name)
    print(f"Playing body animation: {animation_name} at time {current_time}")
