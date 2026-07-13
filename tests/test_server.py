from devmon import config
from devmon.server import _deploy_flow, _deploy_path, create_app


def test_index_renders_title():
    app = create_app()
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"Dev Monitor" in response.data


def test_unknown_target_is_rejected():
    app = create_app()
    client = app.test_client()

    response = client.get("/api/traffic-flow?target=unknown")

    assert response.status_code == 400
    assert response.get_json()["ok"] is False


def test_head_routes_are_available():
    app = create_app()
    client = app.test_client()

    assert client.head("/").status_code == 200
    assert client.head("/api/traffic-flow").status_code == 200
    assert client.head("/api/deploy-flow").status_code == 200


def test_main_deploy_path_uses_configured_dockerhub_namespace(monkeypatch):
    monkeypatch.setattr(config, "DOCKERHUB_NAMESPACE", "example")

    assert _deploy_path("devmon", "example/devmon:abc123") == "GitHub -> DockerHub -> Minikube"
    assert _deploy_path("devmon", "docker.io/example/devmon:abc123") == "GitHub -> DockerHub -> Minikube"


def test_branch_deploy_path():
    assert _deploy_path("branch-devmon", "branch-devmon:latest") == "GitHub CI branch -> Minikube"


def test_other_workload_deploy_path():
    assert _deploy_path("hello-world", "hello-world:latest") == "existing Minikube workload"


def test_deploy_flow_groups_multiple_deployments_by_namespace():
    class Result:
        def __init__(self, command, stdout):
            self.command = command
            self.stdout = stdout

    results = [
        Result(
            config.DEPLOY_COMMANDS[0],
            "NAMESPACE NAME IMAGE READY AVAILABLE\n"
            "progress-tracker backend image/backend:1 3 3\n"
            "progress-tracker frontend image/frontend:1 3 3\n",
        ),
        Result(config.DEPLOY_COMMANDS[1], "NAMESPACE NAME READY STATUS RESTARTS IMAGE\n"),
        Result(config.DEPLOY_COMMANDS[2], "NAMESPACE NAME TYPE CLUSTER-IP PORT\n"),
        Result(config.DEPLOY_COMMANDS[3], "NAMESPACE NAME CLASS HOSTS ADDRESS\n"),
        Result(config.DEPLOY_COMMANDS[4], ""),
    ]

    flow = _deploy_flow(results)

    assert flow.count("+ progress-tracker") == 1
    assert "backend" in flow
    assert "frontend" in flow
