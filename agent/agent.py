"""
Phase 5 — Agentic DevOps AI Agent (OpenAI Version)
Uses OpenAI gpt-4o-mini with function calling

3 Levels:
  Level 1 → Natural language commands (deploy, scale, status)
  Level 2 → Auto-scaler (monitors CPU, scales automatically)
  Level 3 → AI Troubleshooter (reads logs, explains errors)

Usage:
  python agent.py          → interactive chat mode
  python agent.py --watch  → auto-scaler mode (monitors every 30s)
"""

import os
import time
import json
import argparse
from openai import OpenAI
import tools

# ── Setup ──────────────────────────────────────────────────────
# Load API key from .env file or environment variable
def load_env():
    """Load .env file manually"""
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value

load_env()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL  = "gpt-4o-mini"

SYSTEM = """You are an expert DevOps AI agent managing a Kubernetes cluster.
You help users deploy apps, scale pods, monitor resources, and troubleshoot issues.
When something fails, explain the error clearly in simple language and suggest a fix.
Always confirm what action you took and show the result."""

# ── Tool Definitions (OpenAI function calling format) ──────────
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_pod_status",
            "description": "Get status of all pods in the Kubernetes cluster",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "scale_deployment",
            "description": "Scale a Kubernetes deployment to a specific number of replicas",
            "parameters": {
                "type": "object",
                "properties": {
                    "deployment": {"type": "string", "description": "Name of the deployment"},
                    "replicas":   {"type": "integer", "description": "Number of replicas"}
                },
                "required": ["deployment", "replicas"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "deploy_image",
            "description": "Deploy a new Docker image to a deployment",
            "parameters": {
                "type": "object",
                "properties": {
                    "deployment": {"type": "string", "description": "Deployment name"},
                    "image":      {"type": "string", "description": "Full Docker image name with tag"}
                },
                "required": ["deployment", "image"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_deployments",
            "description": "List all Kubernetes deployments",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_services",
            "description": "List all Kubernetes services",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "rollback_deployment",
            "description": "Rollback a deployment to its previous version",
            "parameters": {
                "type": "object",
                "properties": {
                    "deployment": {"type": "string", "description": "Deployment name to rollback"}
                },
                "required": ["deployment"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_cpu_usage",
            "description": "Get CPU and memory usage of all pods",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_pod_logs",
            "description": "Get recent logs from a specific pod",
            "parameters": {
                "type": "object",
                "properties": {
                    "pod_name": {"type": "string", "description": "Full pod name"},
                    "lines":    {"type": "integer", "description": "Number of log lines to fetch"}
                },
                "required": ["pod_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "describe_pod",
            "description": "Get detailed info about a pod including events and error reasons",
            "parameters": {
                "type": "object",
                "properties": {
                    "pod_name": {"type": "string", "description": "Full pod name"}
                },
                "required": ["pod_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_events",
            "description": "Get recent Kubernetes cluster events including warnings and errors",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_crashed_pods",
            "description": "Find pods that are crashed, in error state, or not running",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_replica_count",
            "description": "Get current replica count for a deployment",
            "parameters": {
                "type": "object",
                "properties": {
                    "deployment": {"type": "string", "description": "Deployment name"}
                },
                "required": ["deployment"]
            }
        }
    },
]

# ── Tool Dispatcher ────────────────────────────────────────────
def call_tool(name: str, args: dict) -> str:
    """Call the right tool function based on name."""
    tool_map = {
        "get_pod_status":      lambda: tools.get_pod_status(),
        "scale_deployment":    lambda: tools.scale_deployment(args["deployment"], args["replicas"]),
        "deploy_image":        lambda: tools.deploy_image(args["deployment"], args["image"]),
        "get_deployments":     lambda: tools.get_deployments(),
        "get_services":        lambda: tools.get_services(),
        "rollback_deployment": lambda: tools.rollback_deployment(args["deployment"]),
        "get_cpu_usage":       lambda: tools.get_cpu_usage(),
        "get_pod_logs":        lambda: tools.get_pod_logs(args["pod_name"], args.get("lines", 50)),
        "describe_pod":        lambda: tools.describe_pod(args["pod_name"]),
        "get_events":          lambda: tools.get_events(),
        "get_crashed_pods":    lambda: tools.get_crashed_pods(),
        "get_replica_count":   lambda: tools.get_replica_count(args["deployment"]),
    }
    fn = tool_map.get(name)
    return fn() if fn else f"Unknown tool: {name}"


# ── Agent Core ─────────────────────────────────────────────────
def run_agent(user_message: str, history: list = []) -> str:
    """
    Agentic loop using OpenAI:
    User → GPT thinks → GPT calls tool → GPT sees result → GPT responds
    """
    messages = [{"role": "system", "content": SYSTEM}]
    messages += list(history)
    messages.append({"role": "user", "content": user_message})

    # Agentic loop — GPT can call multiple tools in sequence
    while True:
        response = client.chat.completions.create(
            model=MODEL,
            tools=TOOLS,
            messages=messages
        )

        message = response.choices[0].message
        messages.append(message)

        # If GPT is done (no tool calls) → return final text
        if not message.tool_calls:
            return message.content or "Done."

        # Process tool calls
        for tool_call in message.tool_calls:
            name   = tool_call.function.name
            args   = json.loads(tool_call.function.arguments)
            print(f"  Calling tool: {name}({args})")
            result = call_tool(name, args)
            messages.append({
                "role":         "tool",
                "tool_call_id": tool_call.id,
                "content":      result
            })


# ══════════════════════════════════════════════════════════════
#  LEVEL 2: AUTO-SCALER
# ══════════════════════════════════════════════════════════════
def auto_scaler(deployment: str = "flask-app", cpu_threshold: int = 70, interval: int = 30):
    """Monitor CPU every N seconds and auto-scale."""
    print(f"\nAuto-Scaler Started (OpenAI)")
    print(f"   Deployment    : {deployment}")
    print(f"   CPU threshold : {cpu_threshold}%")
    print(f"   Interval      : {interval}s")
    print("   Press Ctrl+C to stop\n")

    while True:
        try:
            print(f"[{time.strftime('%H:%M:%S')}] Checking cluster...")
            prompt = f"""
Check CPU usage of all pods for deployment '{deployment}'.
If any pod CPU usage is above {cpu_threshold}%, scale up by 1 replica (max 5).
If all pods CPU usage is below 20%, scale down by 1 replica (min 1).
Otherwise keep current replicas.
Tell me what you decided and why.
"""
            response = run_agent(prompt)
            print(f"Agent: {response}\n")
            time.sleep(interval)

        except KeyboardInterrupt:
            print("\nAuto-scaler stopped.")
            break


# ══════════════════════════════════════════════════════════════
#  LEVEL 1 + 3: INTERACTIVE CHAT MODE
# ══════════════════════════════════════════════════════════════
def interactive_mode():
    print("\n" + "="*50)
    print("Agentic DevOps Assistant (OpenAI)")
    print("="*50)
    print("Level 1 — Commands:")
    print("  → 'Show all pods'")
    print("  → 'Scale flask-app to 3 replicas'")
    print("  → 'Deploy aarushgupta15/phase1-app:v2 to flask-app'")
    print("  → 'Rollback flask-app'")
    print()
    print("Level 3 — Troubleshooting:")
    print("  → 'Why is my app crashing?'")
    print("  → 'Get logs from pod flask-app-xxx'")
    print("  → 'Find crashed pods and explain why'")
    print()
    print("Type 'exit' to quit")
    print("="*50 + "\n")

    history = []

    while True:
        user_input = input("You: ").strip()
        if not user_input or user_input.lower() == "exit":
            print("Goodbye!")
            break

        print("  Thinking...")
        try:
            response = run_agent(user_input, history)
            print(f"\nAgent: {response}\n")

            # Keep last 6 messages as context
            history.append({"role": "user",      "content": user_input})
            history.append({"role": "assistant",  "content": response})
            history = history[-6:]

        except Exception as e:
            print(f"Error: {e}\n")


# ── Entry Point ────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agentic DevOps Assistant (OpenAI)")
    parser.add_argument("--watch",      action="store_true", help="Run auto-scaler mode")
    parser.add_argument("--deployment", default="flask-app", help="Deployment to watch")
    parser.add_argument("--threshold",  type=int, default=70, help="CPU threshold %")
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        print("Error: Set your OpenAI API key in agent/.env:")
        print("   OPENAI_API_KEY=your-key-here")
        exit(1)

    if args.watch:
        auto_scaler(args.deployment, args.threshold)
    else:
        interactive_mode()
