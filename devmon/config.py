import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ServerTarget:
    name: str
    host: str
    user: str


PROJECT_NAME = "DevMon"
APP_NAME = "devmon"
DISPLAY_TITLE = "Dev Monitor"
DOCKERHUB_NAMESPACE = os.getenv("DOCKERHUB_NAMESPACE", "mahamah")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY", "mahamahseb/DevMon")
APP_BRANCH = os.getenv("APP_BRANCH", "local")
APP_VERSION = os.getenv("APP_VERSION", "dev")

SERVERS = {
    "lab1": ServerTarget(
        name="lab1",
        host=os.getenv("LAB1_HOST", "192.168.239.141"),
        user=os.getenv("LAB1_USER", "mah"),
    )
}

SSH_PASSWORD_ENV = "LAB1_SSH_PASSWORD"
SSH_KEY_PATH_ENV = "LAB1_SSH_KEY_PATH"

SYSTEM_NAMESPACES = {
    "default",
    "kube-system",
    "kube-public",
    "kube-node-lease",
    "ingress-nginx",
}

TRAFFIC_COMMANDS = [
    "hostname",
    "kubectl config current-context",
    "minikube ip",
    "kubectl get nodes -o wide",
    "kubectl get ingress -A",
    "kubectl get svc -A",
    "kubectl get pods -A -o wide",
    "kubectl get pvc -A",
    "systemctl is-active lab1-ingress-80.service",
    "systemctl is-active lab1-ingress-443.service",
]

DEPLOY_COMMANDS = [
    "kubectl get deployment -A -o custom-columns=NAMESPACE:.metadata.namespace,NAME:.metadata.name,IMAGE:.spec.template.spec.containers[0].image,READY:.status.readyReplicas,AVAILABLE:.status.availableReplicas",
    "kubectl get pods -A -o custom-columns=NAMESPACE:.metadata.namespace,NAME:.metadata.name,READY:.status.containerStatuses[0].ready,STATUS:.status.phase,RESTARTS:.status.containerStatuses[0].restartCount,IMAGE:.spec.containers[0].image",
    "kubectl get svc -A -o custom-columns=NAMESPACE:.metadata.namespace,NAME:.metadata.name,TYPE:.spec.type,CLUSTER-IP:.spec.clusterIP,PORT:.spec.ports[0].port",
    "kubectl get ingress -A -o custom-columns=NAMESPACE:.metadata.namespace,NAME:.metadata.name,CLASS:.spec.ingressClassName,HOSTS:.spec.rules[*].host,ADDRESS:.status.loadBalancer.ingress[0].ip",
    "pgrep -fa '/home/mah/actions-runner-devmon/.*/Runner.Listener|/home/mah/actions-runner-devmon/bin/Runner.Listener' || true",
]
