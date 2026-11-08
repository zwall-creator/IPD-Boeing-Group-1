# Simulation network API

The frontend sends the editable Cytoscape graph as JSON. The computation service validates it, fills safe defaults, assigns deterministic IPv4 addresses when a device does not have one, and creates the state string expected by the simulation model.

## Prepare a network without running it

`POST http://localhost:8000/simulation/prepare`

```json
{
  "topology": {
    "nodes": [
      {"id": "n1", "device_type": "Router", "label": "Gateway"},
      {"id": "n2", "device_type": "Server", "label": "App Server"}
    ],
    "edges": [
      {"id": "e1", "source": "n1", "target": "n2", "connection_type": "TCP", "source_port": 443}
    ]
  }
}
```

The response contains `topology` in normalized form and `state_string`, which can be passed to the simulation service. Invalid device types, IP addresses, node references, or connection types return HTTP 400 with an error message.

## Run a simulation

`POST http://localhost:8000/simulation/run` accepts the same `topology` object alongside `solver` and the optimization weights. The response includes the normalized topology and state string, and the SSE `simulation.started` event includes both values for logging and downstream consumers.

The frontend's **Prepare network API payload** button exercises `/simulation/prepare`; **Run current scenario** sends the same topology to `/simulation/run`.
