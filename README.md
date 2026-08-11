# Undercroft

A self-hosted LLM inference platform built to demonstrate production-grade
deployment practices on constrained infrastructure. Ollama sits behind a
rate-limited FastAPI gateway, deployed on k3s via GitOps (Argo CD), with
automated vulnerability scanning, sealed secrets, network isolation, and
Prometheus/Grafana observability — all running on a self-provisioned
Oracle Cloud ARM instance.

## Why this exists
The goal wasn't "a model behind an API" — it was building the CI/CD,
security, and operational scaffolding that makes a service safe to run
and safe to change.

## Architecture
```
GitHub push -> GitHub Actions (lint, test, Trivy scan, build)
            -> GHCR (image registry)
            -> bump k8s/base/deployment.yaml, commit
            -> Argo CD detects drift, auto-syncs cluster
            -> k3s (Oracle Cloud A1, ARM) runs:
                 gateway (FastAPI, auth + rate limiting + metrics)
                 ollama (inference backend, NetworkPolicy-isolated)
```

## Components
- `gateway/` — FastAPI service in front of Ollama: API key auth, request
  concurrency limiting (protects the constrained ARM box from overload),
  Prometheus metrics, health check used by k8s probes and deploy gating
- `k8s/base/` — Deployment/Service manifests for gateway + Ollama, plus a
  NetworkPolicy restricting Ollama ingress to the gateway only
- `k8s/argocd/` — Argo CD Application manifest — apply once, then `git push`
  is the deploy mechanism from then on
- `.github/workflows/ci.yml` — lint -> test -> build -> Trivy scan
  (fails on HIGH/CRITICAL vulns) -> push to GHCR -> bump manifest for
  GitOps sync

## Build plan
See [docs/PLAN.md](docs/PLAN.md) for the day-by-day build plan and
[docs/LOG.md](docs/LOG.md) for the running dev log.

## Local dev
```bash
cd gateway
pip install -r requirements.txt
export OLLAMA_URL=http://localhost:11434
export GATEWAY_API_KEY=dev-key
uvicorn main:app --reload
```

## Scope notes
Progressive delivery (canary rollout via Argo Rollouts) was designed for
but not implemented in this iteration — see docs/PLAN.md for the reasoning
and what a v2 would add.
"# Undercroft" 
