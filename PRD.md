# PRD: DevMon

## Product Goal

Give developers a small read-only browser view of traffic and deployment state for the `lab1` Minikube lab.

## Users

- Developers checking app routing and deployment state.
- Infra maintainers checking whether shared ingress forwarding is alive.

## MVP Scope

- [x] Web UI titled `Dev Monitor`.
- [x] Branch/version metadata below the title.
- [x] Traffic Flow tab.
- [x] Deploy Flow tab.
- [x] Server dropdown containing only `lab1`.
- [x] Refresh button with loading spinner.
- [x] Read-only SSH command allowlist.
- [x] JSON APIs for traffic and deployment views.
- [x] Dockerfile, compose file, Kubernetes manifests, scripts, and GitHub Actions.

## Out of Scope

- Kubernetes write actions from the browser.
- Arbitrary shell execution.
- Login system.
- Database.
- Secret storage in git.
