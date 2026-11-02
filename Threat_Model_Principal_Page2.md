Page 2: From threat model to directive

The six threats on page 1 come from one root cause: every team can pull anything from anywhere, straight into a shared cluster. Patching each risk separately won't hold. The fix is to make the safe path the only path.

1. One way in for models (enforced, not advised)
- A single internal model registry is the only source of models and datasets. It accepts safetensors only, runs a Fickling scan, records the hash and the upstream commit, and converts or rejects everything else. This retires threat 1 and most of threat 3 at the source.
- The cluster can't bypass it. Admission policies (OPA/Gatekeeper) require signed images, non-root, no host mounts, and the registry's read-only model volume. A network policy blocks direct egress to the Hugging Face Hub. Note: admission control can't see files a job downloads at runtime, which is exactly why the egress block and the registry have to work together.
- Provenance by default. Every model carries a signed record of where it came from and what it was trained on: model signing via Sigstore/OpenSSF, and an ML-BOM (CycloneDX) per training run. This gives threat 4 an audit trail instead of a guess.

2. Blast radius in business terms
- Client and partner IP. A single compromised job on shared storage can expose other teams' proprietary weights and data. That is a contractual breach, not just a security incident. Separate storage per team, and per-team credentials scoped to it.
- Regulatory exposure. Training data provenance and personal data in datasets carry legal obligations (privacy law, and emerging AI regulation for model providers). The ML-BOM doubles as the compliance record.
- Exfiltration and cost. Cap and alert on per-job egress volume. It limits data theft and stops a compromised job from turning into a large cloud bill.

3. Ownership and rollout
- Owners: platform team owns the registry and policies; security owns scanning rules and detections; each team owns its exception requests.
- Exceptions: time-limited, approved by security, logged. No permanent "just this once".
- Rollout: (1) registry plus scanning in audit mode, (2) egress block and admission policies, enforced for new jobs, (3) all jobs.
- How I'll know it works: percent of models loaded through the registry (target 100%), number of pickle files reaching the cluster (target 0), time to patch the driver and container toolkit, and open exceptions trending down. These measure risk removed, not bugs found.
