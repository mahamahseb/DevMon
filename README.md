# DevMon

DevMon is a read-only Dev Monitor web app for the `lab1` Minikube environment.

It connects only to `lab1` at `192.168.239.141` through SSH and uses allowlisted read-only commands to show Kubernetes traffic and deployment state in a browser.

## Local Development

```powershell
cd DevMon
.\run.ps1
```

Open:

```text
http://localhost:8000/
```

SSH credentials must be provided outside git:

```powershell
$env:LAB1_SSH_PASSWORD="..."
```

or:

```powershell
$env:LAB1_SSH_KEY_PATH="C:\path\to\key"
```

## Validation

```powershell
python -m compileall app.py devmon
python -m pytest
```

## Docker

```powershell
docker build -t devmon:local .
docker compose up --build
```

## GitHub Secrets

Add these repository secrets in GitHub:

```text
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
```

Do not put token values in source files.

## Kubernetes Secret

Create SSH secret on `lab1` manually when needed:

```bash
kubectl create secret generic devmon-ssh \
  -n devmon \
  --from-literal=LAB1_SSH_PASSWORD='REPLACE_ME'
```

For the branch namespace:

```bash
kubectl create secret generic branch-devmon-ssh \
  -n branch-devmon \
  --from-literal=LAB1_SSH_PASSWORD='REPLACE_ME'
```

## Deployment URLs

```text
https://devmon.mah.com/
https://devmon.192.168.239.141.sslip.io/
https://branch-devmon.mah.com/
https://branch-devmon.192.168.239.141.sslip.io/
```
