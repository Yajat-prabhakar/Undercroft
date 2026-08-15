# Dev Log

Keep this updated daily. Short entries are fine — the point is having a
real record of decisions and problems for interview answers, not prose.

## Day 1 — [date]

- Built:
- Broke:
- Decided:

## Day 2 — [date]

ubuntu@undercroft-main:/Undercroft/gateway$ git pull
remote: Enumerating objects: 7, done.
remote: Counting objects: 100% (7/7), done.
remote: Compressing objects: 100% (1/1), done.
remote: Total 4 (delta 3), reused 4 (delta 3), pack-reused 0 (from 0)
Unpacking objects: 100% (4/4), 510 bytes | 510.00 KiB/s, done.
From https://github.com/Yajat-prabhakar/Undercroft
fc7d3a5..8032e5a  main       -> origin/main
Updating fc7d3a5..8032e5a
Fast-forward
gateway/test_main.py | 5 ++++-
1 file changed, 4 insertions(+), 1 deletion(-)
ubuntu@undercroft-main:/Undercroft/gateway$ python3 -m pytest -v
/home/ubuntu/.local/lib/python3.10/site-packages/pytest_asyncio/plugin.py:208: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture caching scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to function scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session"

warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
=========================================================================== test session starts ============================================================================
platform linux -- Python 3.10.12, pytest-8.3.3, pluggy-1.6.0 -- /usr/bin/python3
cachedir: .pytest_cache
rootdir: /home/ubuntu/Undercroft/gateway
plugins: anyio-4.14.2, asyncio-0.24.0
asyncio: mode=strict, default_loop_scope=None
collected 6 items

test_main.py::test_generate_requires_api_key PASSED                                                                                                                  [ 16%]
test_main.py::test_generate_rejects_bad_api_key PASSED                                                                                                               [ 33%]
test_main.py::test_metrics_endpoint_exposed PASSED                                                                                                                   [ 50%]
test_main.py::test_health_reports_ollama_status PASSED                                                                                                               [ 66%]
test_main.py::test_generate_missing_prompt_field_is_rejected PASSED                                                                                                  [ 83%]
test_main.py::test_metrics_track_request_count PASSED                                                                                                                [100%]

============================================================================ 6 passed in 0.31s =============================================================================
ubuntu@undercroft-main:~/Undercroft/gateway$

## Day 3 — [date]

* Installed k3s (lightweight Kubernetes) as a single-node cluster on the Oracle box
* Fixed a real permissions issue with `kubectl` config access (`KUBECONFIG` env var, persisted to `~/.bashrc`)
* Built the gateway's Docker image locally and imported it directly into k3s's container storage (`docker save | k3s ctr images import -`) — this is a temporary shortcut for local testing; Day 4's CI pipeline replaces this with a proper registry (GHCR)
* Created a Kubernetes Secret to hold the API key (currently plaintext/base64 — Day 6 fixes this properly with Sealed Secrets)
* Deployed both Ollama and the gateway as Kubernetes Deployments, each with their own Service (a stable internal network name)
* Watched the gateway self-heal automatically (one restart) because its health check correctly detected Ollama wasn't ready yet — a live demo of Kubernetes' self-healing behavior
* Discovered and fixed that the new Ollama pod needed its model pulled fresh, since container storage doesn't carry over from your old systemd-based setup — reinforces the concept that containers are ephemeral unless given persistent storage
* Confirmed full request flow works end-to-end using Kubernetes-internal networking (`http://ollama:11434`), not `localhost` shortcuts

## Day 4 — [date]

**NOTES — real troubleshooting log for your interview, all legitimate:**

1. Trivy found 3 real HIGH-severity CVEs in `starlette` (transitive dependency via fastapi) — fixed by loosening the fastapi version pin so pip resolves a patched version automatically
2. A pinned Trivy action version (`@0.24.0`) had been deleted/renamed upstream — fixed by switching to `@master` to always track the latest stable release
3. GHCR (Docker registries generally) require lowercase image names — GitHub repo names can have capitals, so had to add an explicit lowercase-conversion step and pass it between jobs via GitHub Actions' **job outputs** mechanism (since environment variables don't carry across separate jobs)
4. A flake8 style rule caught a missing trailing newline — trivial but shows the linter catches real formatting conventions
5. A FastAPI version upgrade changed which exact HTTP status code (401 vs 403) fires for a missing auth header — fixed the test to assert the actual security property (rejection) rather than the exact status code, since the guarantee mattered more than the implementation detail

## Day 5 — [date]

* Argo CD installed and running (all 7 components healthy)
* Connected to your GitHub repo, watching the `main` branch
* Full GitOps loop proven live: code push → CI builds/tests/scans/pushes image → Argo CD auto-detects the change → auto-deploys → confirmed with a real curl response
* Cleaned up the old duplicate Day 3 resources so `undercroft` namespace is the single source of truth
* You have actual video proof of the whole chain working, which is more than most people bother to capture

## Day 6 — [date]

**Day 6 is complete.** Confirmed:

* Sealed Secrets controller installed and running
* `kubeseal` CLI installed
* API key re-created as an encrypted SealedSecret, committed to git safely
* Old plaintext version deleted
* Full request chain re-verified working with the new encrypted secret

## Day 7 — [date]


- Installed Helm (package manager for Kubernetes), then installed the   kube-prometheus-stack chart (bundles Prometheus, Grafana, Alertmanager)   into the undercroft namespace via \`helm install monitoring   prometheus-community/kube-prometheus-stack -n undercroft\`  - Created a ServiceMonitor (gateway-metrics) to tell Prometheus to scrape   the gateway's /metrics endpoint every 15s  - Bug: Prometheus showed "0/0 up" / "No targets" for gateway-metrics even   though the metric existed (confirmed via direct curl to /metrics) and   the Service had real Endpoints. Root cause: a ServiceMonitor's   \`selector.matchLabels\` matches a Service's own \`metadata.labels\` — not   its \`spec.selector\`, which only controls pod routing. The gateway   Service had a selector but no labels of its own, so Prometheus couldn't   find it via discovery even though it worked fine for normal traffic.  - Diagnosed by: checking raw metrics at the source -> inspecting   Prometheus's live scrape config via /config -> checking the Service's   Endpoints (ruled out networking) -> isolating the label mismatch  - Fix: added \`metadata.labels: app: gateway\` to the gateway Service   (separate from spec.selector, which was already correct) — one line,   auto-deployed via Argo CD once pushed  - Confirmed fix via Prometheus's own Targets UI: gateway-metrics -> 1/1 up  - Built a Grafana dashboard ("Undercroft Gateway") with a live "Request   Rate" panel (rate(gateway\_requests\_total[5m])) showing real traffic   from test curls, plus a Queue Depth panel  - Access pattern for local dev: kubectl port-forward for Prometheus (9090),   Grafana (3000), and the gateway (8080), each tunneled out to Windows via   SSH -L flags — four persistent terminals total during active dev/testing

## Day 8 — [date]

## Day 9 — [date]
