from collections import defaultdict

from flask import Flask, jsonify, request

from . import config
from .ssh import ReadOnlySSHClient
from .templates import INDEX_HTML


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def index():
        return INDEX_HTML.format(
            title=config.DISPLAY_TITLE,
            branch=config.APP_BRANCH,
            version=config.APP_VERSION,
        )

    @app.head("/")
    def index_head():
        return "", 200

    @app.get("/health")
    def health():
        return jsonify({"ok": True, "app": config.APP_NAME})

    @app.get("/api/traffic-flow")
    def traffic_flow():
        target_name, error = _validated_target()
        if error:
            return error
        target = config.SERVERS[target_name]
        command_results = ReadOnlySSHClient(target).run_commands(config.TRAFFIC_COMMANDS)
        return jsonify(_api_response(target, {"flow": _traffic_flow(command_results), "commands": [r.__dict__ for r in command_results]}))

    @app.head("/api/traffic-flow")
    def traffic_flow_head():
        return "", 200

    @app.get("/api/deploy-flow")
    def deploy_flow():
        target_name, error = _validated_target()
        if error:
            return error
        target = config.SERVERS[target_name]
        command_results = ReadOnlySSHClient(target).run_commands(config.DEPLOY_COMMANDS)
        return jsonify(_api_response(target, {"flow": _deploy_flow(command_results), "commands": [r.__dict__ for r in command_results]}))

    @app.head("/api/deploy-flow")
    def deploy_flow_head():
        return "", 200

    return app


def _validated_target():
    target = request.args.get("target", "lab1")
    if target not in config.SERVERS:
        return None, (jsonify({"ok": False, "error": f"Unknown target: {target}"}), 400)
    return target, None


def _api_response(target, result):
    return {
        "ok": True,
        "servers": {
            name: {"host": server.host, "user": server.user}
            for name, server in config.SERVERS.items()
        },
        "result": {
            "target": target.name,
            "host": target.host,
            **result,
        },
    }


def _result_by_command(results):
    return {result.command: result.stdout for result in results}


def _traffic_flow(results):
    data = _result_by_command(results)
    ingress = data.get("kubectl get ingress -A", "")
    services = data.get("kubectl get svc -A", "")
    pods = data.get("kubectl get pods -A -o wide", "")
    pvc = data.get("kubectl get pvc -A", "")
    minikube_ip = data.get("minikube ip", "unknown")
    http = data.get("systemctl is-active lab1-ingress-80.service", "unknown")
    https = data.get("systemctl is-active lab1-ingress-443.service", "unknown")
    return f"""Traffic Flow

HTTPS:
Browser
  -> sslip.io DNS / mah.com DNS
  -> lab1:443 ({https})
  -> socat forwarder
  -> minikube ingress {minikube_ip}:443
  -> NGINX Ingress Controller
  -> host branches
  -> namespace
  -> ingress
  -> service
  -> pods

HTTP:
Browser
  -> lab1:80 ({http})
  -> socat forwarder
  -> minikube ingress {minikube_ip}:80
  -> NGINX redirects HTTP to HTTPS
  -> lab1:443 path

Ingress:
{ingress}

Services:
{services}

Pods:
{pods}

PVC:
{pvc}
"""


def _deploy_flow(results):
    data = _result_by_command(results)
    deployments = _parse_table(data.get(config.DEPLOY_COMMANDS[0], ""))
    pods = _group_rows(_parse_table(data.get(config.DEPLOY_COMMANDS[1], "")))
    services = _group_rows(_parse_table(data.get(config.DEPLOY_COMMANDS[2], "")))
    ingresses = _group_rows(_parse_table(data.get(config.DEPLOY_COMMANDS[3], "")))
    runner = data.get(config.DEPLOY_COMMANDS[4], "")
    sections = ["Deploy Flow", "", f"Runner: {runner or 'not detected'}", ""]
    for row in deployments:
        namespace = row.get("NAMESPACE", "")
        if namespace in config.SYSTEM_NAMESPACES:
            continue
        image = row.get("IMAGE", "")
        sections.append(f"+ {namespace}")
        sections.append(f"  Deploy path: {_deploy_path(namespace, image)}")
        sections.append(f"  Source: GitHub {config.GITHUB_REPOSITORY}")
        sections.append(f"  DockerHub: {config.DOCKERHUB_NAMESPACE}/devmon when using main deployment")
        sections.append("  lab1 self-hosted runner: devmon-minikube")
        sections.append(f"  Minikube namespace: {namespace}")
        sections.append(f"  Deployment image: {image}")
        sections.append(f"  Deployment status: ready={row.get('READY', '')} available={row.get('AVAILABLE', '')}")
        sections.append(f"  Pods: {_format_rows(pods.get(namespace, []))}")
        sections.append(f"  Services: {_format_rows(services.get(namespace, []))}")
        sections.append(f"  Ingress: {_format_rows(ingresses.get(namespace, []))}")
        sections.append(f"  Browser endpoints: https://{namespace}.mah.com/ and https://{namespace}.192.168.239.141.sslip.io/")
        sections.append("")
    return "\n".join(sections).strip()


def _deploy_path(namespace, image):
    if namespace == "devmon" and image.startswith(("mahamah/devmon:", "docker.io/mahamah/devmon:")):
        return "GitHub -> DockerHub -> Minikube"
    if namespace == "branch-devmon" and image.startswith("branch-devmon:"):
        return "GitHub CI branch -> Minikube"
    return "existing Minikube workload"


def _parse_table(text):
    lines = [line for line in text.splitlines() if line.strip()]
    if len(lines) < 2:
        return []
    headers = lines[0].split()
    rows = []
    for line in lines[1:]:
        values = line.split(maxsplit=len(headers) - 1)
        values += [""] * (len(headers) - len(values))
        rows.append(dict(zip(headers, values)))
    return rows


def _group_rows(rows):
    grouped = defaultdict(list)
    for row in rows:
        grouped[row.get("NAMESPACE", "")].append(row)
    return grouped


def _format_rows(rows):
    if not rows:
        return "none"
    return "; ".join(", ".join(f"{key}={value}" for key, value in row.items()) for row in rows)
