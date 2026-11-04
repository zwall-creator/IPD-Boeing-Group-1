"""Translate frontend network graphs into the simulation service state format."""

from __future__ import annotations

import ipaddress
import re
from typing import Any


VALID_DEVICE_TYPES = {"PC", "Laptop", "Cell Phone", "Mobile", "Router", "Switch", "Server"}
DEVICE_TYPE_ALIASES = {"Cell Phone": "Mobile"}
VALID_CONNECTION_TYPES = {"TCP", "UDP"}
DEFAULT_IP_PREFIX = ipaddress.ip_address("10.0.0.0")


def _number(value: Any, field: str, *, integer: bool = False) -> int | float:
    if value is None or value == "":
        return 0 if integer else 0.0
    try:
        parsed = int(value) if integer else float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be a number") from exc
    if parsed < 0:
        raise ValueError(f"{field} must be non-negative")
    return parsed


def _ip(value: Any, fallback_index: int) -> list[int]:
    raw = value or str(DEFAULT_IP_PREFIX + fallback_index)
    try:
        parsed = ipaddress.ip_address(str(raw))
    except ValueError as exc:
        raise ValueError(f"device_ip must be a valid IPv4 address: {raw}") from exc
    if parsed.version != 4:
        raise ValueError("device_ip must be an IPv4 address")
    return list(parsed.packed)


def _safe_identifier(value: Any, fallback: str) -> str:
    identifier = str(value or fallback)
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", identifier):
        raise ValueError(f"identifier contains unsupported characters: {identifier}")
    return identifier


def normalize_topology(topology: dict[str, Any] | None) -> dict[str, list[dict[str, Any]]]:
    """Validate and normalize Cytoscape JSON into a simulation-ready graph."""
    if not isinstance(topology, dict):
        raise ValueError("topology must be an object containing nodes and edges")

    raw_nodes = topology.get("nodes", [])
    raw_edges = topology.get("edges", [])
    if not isinstance(raw_nodes, list) or not isinstance(raw_edges, list):
        raise ValueError("topology.nodes and topology.edges must be arrays")

    nodes: list[dict[str, Any]] = []
    node_ids: set[str] = set()
    for index, raw in enumerate(raw_nodes, start=1):
        data = raw.get("data", raw) if isinstance(raw, dict) else {}
        node_id = _safe_identifier(data.get("id"), f"n{index}")
        if node_id in node_ids:
            raise ValueError(f"duplicate node id: {node_id}")
        node_ids.add(node_id)
        device_type = data.get("device_type", "PC")
        if device_type not in VALID_DEVICE_TYPES:
            raise ValueError(f"unsupported device_type: {device_type}")
        simulation_device_type = DEVICE_TYPE_ALIASES.get(device_type, device_type)
        device_ip = _ip(data.get("device_ip"), index)
        nodes.append({
            "id": node_id,
            "label": str(data.get("label") or f"{device_type} {index}"),
            "device_type": simulation_device_type,
            "device_ip": ".".join(map(str, device_ip)),
            "base_sec_level": _number(data.get("base_sec_level"), "base_sec_level"),
            "risk_level": _number(data.get("risk_level"), "risk_level"),
        })

    edges: list[dict[str, Any]] = []
    for index, raw in enumerate(raw_edges, start=1):
        data = raw.get("data", raw) if isinstance(raw, dict) else {}
        source = _safe_identifier(data.get("source"), "")
        target = _safe_identifier(data.get("target"), "")
        if source not in node_ids or target not in node_ids:
            raise ValueError(f"edge {index} references an unknown node")
        connection_type = str(data.get("connection_type") or "TCP").upper()
        if connection_type not in VALID_CONNECTION_TYPES:
            raise ValueError(f"unsupported connection_type: {connection_type}")
        source_port = data.get("source_port")
        if source_port in (None, ""):
            source_port = 10000 + index
        edges.append({
            "id": _safe_identifier(data.get("id"), f"e{index}"),
            "source": source,
            "target": target,
            "cost": _number(data.get("cost"), "cost", integer=True),
            "bandwidth": _number(data.get("bandwidth"), "bandwidth", integer=True),
            "connection_type": connection_type,
            "source_port": int(_number(source_port, "source_port", integer=True)),
        })

    return {"nodes": nodes, "edges": edges}


def to_state_string(topology: dict[str, list[dict[str, Any]]], sim_id: str = "frontend") -> str:
    """Create the state string consumed by ``Simulation_Service``/``NW_Node``."""
    by_id = {node["id"]: node for node in topology["nodes"]}
    connections_by_source: dict[str, list[dict[str, Any]]] = {node["id"]: [] for node in topology["nodes"]}
    for edge in topology["edges"]:
        target = by_id[edge["target"]]
        connections_by_source[edge["source"]].append({
            "ip": target["device_ip"].split("."),
            "cost": edge["cost"],
            "bandwidth": edge["bandwidth"],
            "connection_type": edge["connection_type"],
            "source_port": edge["source_port"],
        })

    node_strings = []
    for node in topology["nodes"]:
        connections = []
        for connection in connections_by_source[node["id"]]:
            ip = ",".join(connection["ip"])
            connections.append(
                f"([{ip}],{connection['cost']},{connection['bandwidth']},"
                f"{connection['connection_type']},{connection['source_port']})"
            )
        node_strings.append(
            f"{node['device_type']},[{node['device_ip']}],{node['base_sec_level']},"
            f"{node['base_sec_level']},{node['risk_level']},[{','.join(connections)}];"
        )
    return f"{sim_id},frontend,[{''.join(node_strings)}]"


def prepare_network(topology: dict[str, Any] | None, sim_id: str = "frontend") -> dict[str, Any]:
    normalized = normalize_topology(topology)
    return {"topology": normalized, "state_string": to_state_string(normalized, sim_id)}
