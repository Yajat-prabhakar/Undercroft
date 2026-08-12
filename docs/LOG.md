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

## Day 5 — [date]

## Day 6 — [date]

## Day 7 — [date]

## Day 8 — [date]

## Day 9 — [date]
