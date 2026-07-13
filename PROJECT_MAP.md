# Project Map

```text
DevMon/
  app.py
  requirements.txt
  Dockerfile
  compose.yaml
  run.ps1
  README.md
  PRD.md
  PROJECT_MAP.md
  devmon/
    __init__.py
    config.py
    server.py
    ssh.py
    templates.py
  k8s/
    devmon.yaml
    branch-devmon.yaml
  scripts/
    deploy-minikube.sh
    verify-minikube-app.sh
  .github/
    workflows/
      ci.yml
      ci-branch.yml
```

## Runtime Flow

Browser requests `/api/traffic-flow` or `/api/deploy-flow`.

The Flask backend validates `target=lab1`, connects to `192.168.239.141` with Paramiko, runs only allowlisted read-only commands, then returns a summarized text flow and raw command results as JSON.
