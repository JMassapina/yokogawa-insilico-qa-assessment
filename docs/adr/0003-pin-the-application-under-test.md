# ADR-0003: Pin Frontend E2E Targets to Local Node Modules
**Status:** Accepted  

### Context
Driving end-to-end browser automation scripts directly against a live public URL introduces external infrastructure variables into our local integration checks. If the remote site suffers an outage, network slowdown, or unannounced version deployment, the integration pipeline breaks—making it impossible to tell a real codebase regression from an external service flake.

### Decision
We isolate our E2E web automation testing signal by pinning the frontend execution target to a static, localized package dependency (`escher: 1.8.2`) pulled straight from `node_modules`. We serve this build headlessly inside our container space on port `8899` using a zero-dependency native Node standard library wrapper (`serve.mjs`).

### Consequences
Our testing pipeline operates fully detached from external network interfaces, guaranteeing reproducible, deterministic runtimes. Public site changes are monitored separately via a separate, non-blocking nightly scheduled job configured to detect application drift.
