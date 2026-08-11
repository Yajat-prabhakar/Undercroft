# 9-Day Build Plan

Scope cut for the deadline: no Argo Rollouts / canary traffic-splitting.
Say so honestly in interviews — "I designed for progressive delivery but
prioritized GitOps + observability + security given the timeline" is a
strong answer, a fake canary demo is not.

## Day 1 — Foundation
- Push this scaffold to a new GitHub repo (rename YOUR_GITHUB_USERNAME everywhere)
- Confirm Ollama already running on the Oracle A1 instance, pull a small model (llama3.2:1b or phi3:mini — stay small, it's a free-tier ARM box)
- Run the gateway locally against it (`uvicorn main:app --reload`), confirm `/v1/generate` works end to end
- Note in your dev log: what broke, what you changed

## Day 2 — Gateway hardening
- Confirm auth + rate limiting behave correctly under load (use `hey` or `ab` to hit it with concurrency > MAX_CONCURRENT_REQUESTS, verify it queues instead of falling over)
- Add 2-3 more real tests
- `docker build` locally, run the container, hit /health and /v1/generate through it

## Day 3 — k3s on the Oracle instance
- Install k3s (single binary, lightweight — this matters on a free-tier box)
- `kubectl apply -f k8s/base/` manually first (before GitOps) — get gateway + ollama running as pods, confirm the NetworkPolicy doesn't break gateway->ollama traffic
- This is the day most likely to eat extra time — budget slack

## Day 4 — CI pipeline
- Push `.github/workflows/ci.yml`, fix whatever breaks (it will)
- Set repo secret `GITOPS_PAT` (a GitHub PAT with repo write scope)
- Confirm: PR triggers lint+test, merge to main triggers build -> Trivy scan -> push to GHCR -> manifest bump commit

## Day 5 — Argo CD (GitOps)
- Install Argo CD on the cluster
- Apply `k8s/argocd/application.yaml`
- Confirm the loop end to end: change code -> push -> CI builds & bumps manifest -> Argo CD auto-syncs -> new pod running
- This loop working is the single most important demo for the interview

## Day 6 — Secrets
- Install Sealed Secrets controller (or SOPS, pick one, don't do both)
- Replace the plaintext `gateway-secrets` reference with a real sealed secret
- Confirm: no plaintext secret ever touches the git repo — this is a specific claim you can show a reviewer the commit history for

## Day 7 — Observability
- Prometheus + Grafana (kube-prometheus-stack via Helm is fastest)
- Dashboard: request latency, queue depth, error rate — the metrics are already exposed at /metrics
- Screenshot the dashboard under load for your portfolio/resume

## Day 8 — Polish
- Architecture diagram (draw.io or excalidraw, keep it simple)
- README rewrite: what it is, why each piece exists, what you'd add with more time (mention canary here — shows you know the next step)
- Load test, capture numbers (p50/p95 latency, max sustained concurrency) — real numbers beat vague claims

## Day 9 — Buffer + interview prep
- Assume day 3 or 5 ran over — this day absorbs it
- Write the resume bullet (see below)
- Write 3-4 sentences per component you can say out loud without notes: why k3s not raw Docker, why GitOps not direct SSH deploy, why the NetworkPolicy, why Sealed Secrets

## Resume bullet (only write this once it's actually true)
> Designed and deployed a self-hosted LLM inference platform on k3s with a
> full GitOps pipeline (GitHub Actions -> GHCR -> Argo CD) featuring
> automated Trivy vulnerability scanning, sealed secrets management, network
> policy isolation, and Prometheus/Grafana observability — running on
> self-provisioned Oracle Cloud infrastructure.

## Dev log
Keep a running `docs/LOG.md` as you go — date, what you built, what broke,
what you'd do differently. This is your source material for interview
answers and for writing the bullet honestly at the end.
