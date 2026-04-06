"""
Phase 5 — DevOps Agent Tools
Each function = one action the AI agent can call
"""

import subprocess
import json


def _run(cmd: list, timeout: int = 30) -> str:
    """Helper to run shell commands safely."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip() if result.returncode == 0 else f"ERROR: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "ERROR: Command timed out"
    except FileNotFoundError:
        return f"ERROR: Command not found: {cmd[0]}"


# ── Level 1 Tools: Natural Language Commands ──────────────────

def get_pod_status() -> str:
    """Get status of all pods in the cluster."""
    return _run(["kubectl", "get", "pods", "-o", "wide"])


def scale_deployment(deployment: str, replicas: int) -> str:
    """Scale a deployment to N replicas."""
    result = _run(["kubectl", "scale", "deployment", deployment, f"--replicas={replicas}"])
    if "ERROR" not in result:
        return f"✅ Scaled '{deployment}' to {replicas} replicas."
    return result


def deploy_image(deployment: str, image: str) -> str:
    """Deploy a new image to a deployment."""
    result = _run(["kubectl", "set", "image", f"deployment/{deployment}", f"{deployment}={image}"])
    if "ERROR" not in result:
        return f"✅ Updated '{deployment}' to image: {image}"
    return result


def get_deployments() -> str:
    """List all deployments and their status."""
    return _run(["kubectl", "get", "deployments"])


def get_services() -> str:
    """List all services in the cluster."""
    return _run(["kubectl", "get", "services"])


def rollback_deployment(deployment: str) -> str:
    """Rollback a deployment to previous version."""
    result = _run(["kubectl", "rollout", "undo", f"deployment/{deployment}"])
    if "ERROR" not in result:
        return f"✅ Rolled back '{deployment}' to previous version."
    return result


def get_rollout_status(deployment: str) -> str:
    """Check rollout status of a deployment."""
    return _run(["kubectl", "rollout", "status", f"deployment/{deployment}", "--timeout=60s"])


# ── Level 2 Tools: Auto-Scaler ────────────────────────────────

def get_cpu_usage() -> str:
    """Get CPU and memory usage of all pods."""
    result = _run(["kubectl", "top", "pods"])
    if "ERROR" in result:
        return "Metrics server not available. Install with: kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml"
    return result


def get_node_usage() -> str:
    """Get CPU and memory usage of all nodes."""
    return _run(["kubectl", "top", "nodes"])


def get_replica_count(deployment: str) -> str:
    """Get current replica count for a deployment."""
    result = _run(["kubectl", "get", "deployment", deployment, "-o", "json"])
    if "ERROR" in result:
        return result
    try:
        data = json.loads(result)
        current = data["spec"]["replicas"]
        ready   = data["status"].get("readyReplicas", 0)
        return f"Deployment '{deployment}': {ready}/{current} replicas ready"
    except Exception:
        return result


# ── Level 3 Tools: AI Troubleshooter ─────────────────────────

def get_pod_logs(pod_name: str, lines: int = 50) -> str:
    """Get recent logs from a specific pod."""
    return _run(["kubectl", "logs", pod_name, f"--tail={lines}"])


def get_pod_logs_previous(pod_name: str) -> str:
    """Get logs from a previously crashed pod container."""
    return _run(["kubectl", "logs", pod_name, "--previous", "--tail=50"])


def describe_pod(pod_name: str) -> str:
    """Get detailed info about a pod including events and errors."""
    return _run(["kubectl", "describe", "pod", pod_name])


def describe_deployment(deployment: str) -> str:
    """Get detailed info about a deployment."""
    return _run(["kubectl", "describe", "deployment", deployment])


def get_events() -> str:
    """Get recent cluster events — shows warnings and errors."""
    return _run(["kubectl", "get", "events", "--sort-by=.lastTimestamp"])


def get_crashed_pods() -> str:
    """Find pods that are not running (CrashLoopBackOff, Error, etc)."""
    result = _run(["kubectl", "get", "pods"])
    if "ERROR" in result:
        return result
    # Filter for non-running pods
    lines  = result.split("\n")
    header = lines[0] if lines else ""
    bad    = [l for l in lines[1:] if l and "Running" not in l and "Completed" not in l]
    if not bad:
        return "✅ All pods are healthy!"
    return "\n".join([header] + bad)
