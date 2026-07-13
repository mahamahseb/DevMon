from devmon import config
from devmon.server import _deploy_path, create_app


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


def test_main_deploy_path_uses_configured_dockerhub_namespace(monkeypatch):
    monkeypatch.setattr(config, "DOCKERHUB_NAMESPACE", "example")

    assert _deploy_path("devmon", "example/devmon:abc123") == "GitHub -> DockerHub -> Minikube"
    assert _deploy_path("devmon", "docker.io/example/devmon:abc123") == "GitHub -> DockerHub -> Minikube"


def test_branch_deploy_path():
    assert _deploy_path("branch-devmon", "branch-devmon:latest") == "GitHub CI branch -> Minikube"


def test_other_workload_deploy_path():
    assert _deploy_path("hello-world", "hello-world:latest") == "existing Minikube workload"
