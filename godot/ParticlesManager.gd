extends Node

const ORCHESTRATOR_URL = "http://127.0.0.1:8000"

# This manager could be a singleton (autoload) to be accessible from anywhere in the game.

func request_particle_effect(effect_type: String, position: Vector3, context: Dictionary = {}):
    var http_request = HTTPRequest.new()
    add_child(http_request)
    # We pass the position as metadata to the request completed signal
    http_request.request_completed.connect(self._on_request_completed.bind(position))

    var body = JSON.stringify({
        "effect_type": effect_type,
        "context": context
    })
    var headers = ["Content-Type: application/json"]
    var error = http_request.request(ORCHESTRATOR_URL + "/generate_particle_effect", headers, HTTPClient.METHOD_POST, body)
    if error != OK:
        print("An error occurred in the HTTP request.")

func _on_request_completed(result, response_code, headers, body, position: Vector3):
    if response_code == 200:
        var json = JSON.parse_string(body.get_string_from_utf8())
        _create_particle_effect(json.parameters, position)
    else:
        print("Failed to get response from Particles AI. Response code: ", response_code)

func _create_particle_effect(params: Dictionary, position: Vector3):
    # This function creates and configures a GPUParticles3D node based on the received parameters.
    var particles_node = GPUParticles3D.new()

    # Configure the particles node with the parameters from the AI
    particles_node.amount = params.get("amount", 100)
    particles_node.lifetime = params.get("lifetime", 2.0)
    # ... set other properties like process_material, draw_pass_mesh, etc.

    # Set the position of the particle effect
    particles_node.global_transform.origin = position

    # Add the particle effect to the scene
    get_tree().root.add_child(particles_node)

    # The particles should start emitting automatically
    particles_node.emitting = true

    # Optional: Set the node to free itself after all particles have finished
    var timer = Timer.new()
    timer.wait_time = particles_node.lifetime * 2 # A bit longer than lifetime to be safe
    timer.one_shot = true
    timer.timeout.connect(particles_node.queue_free)
    particles_node.add_child(timer)
    timer.start()

    print(f"Created particle effect at position: {position}")
