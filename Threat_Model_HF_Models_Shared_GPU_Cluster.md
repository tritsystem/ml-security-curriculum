# Threat model: Hugging Face models on a shared GPU cluster (corrected)

*Module 1 exercise. This revises a Gemini draft (original kept as `Threat_Model_HF_Shared_GPU_Gemini_original.md`).
Corrections and additions are listed at the end. Facts checked 2026-10-30 against Trail of Bits, Wiz and the Ray docs;
items marked "verify" are not yet checked.*

**Scenario:** teams download models (and sometimes code) from the Hugging Face Hub and fine-tune or serve them on a
multi-tenant GPU cluster (Kubernetes or Slurm, with shared storage, and Ray or torchrun for distributed jobs).

## Assets
- Other tenants' **proprietary weights, training data, prompts and outputs** (on shared storage and in GPU memory)
- **Credentials:** Hugging Face tokens, cloud keys, W&B/MLflow keys, SSH keys, Kubernetes service-account tokens
- **The cluster itself:** nodes, the GPU driver and runtime, the scheduler/control plane
- **Model integrity:** that what you train and ship is what you think it is (no backdoor, no silent corruption)
- **GPU time** (cryptomining after compromise is the most common real-world outcome)

## Entry points
1. Model files loaded by jobs: `.bin`/`.pt` (pickle), safetensors, GGUF, ONNX
2. `trust_remote_code=True` repos, and custom CUDA/C++ ops compiled at load time
3. Python dependencies installed by jobs (`pip install` of public packages)
4. **The shared model cache and shared storage** (e.g. a common `HF_HOME`, NFS datasets)
5. Cluster control planes: Ray dashboard/job API, Slurm, Jupyter/TensorBoard/MLflow UIs
6. The GPU stack: driver, container runtime (NVIDIA Container Toolkit), shared GPU contexts (MPS, time-slicing)

## Ranked risks (each with control and detection)

| # | Severity | Risk | Entry | Impact |
|---|---|---|---|---|
| 1 | Critical | Code execution from model artifacts and remote code | 1, 2 | RCE as the job's identity; first foothold |
| 2 | Critical | **Shared-cache / shared-storage poisoning** | 4 | One tenant plants a malicious model or file that other tenants then load |
| 3 | High | Lateral movement through cluster software that assumes a trusted network | 5 | Cluster-wide takeover from a single job |
| 4 | High | Container escape through the GPU stack | 6 | Host compromise; reach every tenant on the node |
| 5 | High | Credential theft after any RCE | 1–5 | Blast radius extends off-cluster (Hub, cloud) |
| 6 | Medium–High | Cross-tenant leakage through shared GPU contexts and serving caches | 6 | Weights, activations or prompts exposed |
| 7 | Medium–High | Malicious or poisoned models (backdoors) | 1, 3 | Compromised model behaviour downstream |
| 8 | Medium–High | Dependency / package supply chain | 3 | RCE through a public package |
| 9 | Medium | Silent integrity failures, hardware **and software** | – | Wrong models with no alert |

### 1. Code execution from model artifacts and remote code (Critical)
- **Mechanism:**
  - `torch.load` on pickle files runs code embedded in the file.
  - `trust_remote_code=True` runs the repo's Python.
  - Custom CUDA/C++ ops compile and run native code.
- **"Safe" formats are not a complete fix.** safetensors, GGUF and ONNX run no code, but loaders still trust sizes,
  offsets and shapes from the file. Example: the bitsandbytes `dequantize_4bit` out-of-bounds read from an untrusted
  checkpoint shape (#2106).
- **Controls:**
  - Prefer safetensors.
  - For legacy files, load with `torch.load(..., weights_only=True)`, the default since PyTorch 2.6 (check that
    pinned old versions don't silently revert this).
  - Ban `trust_remote_code` by default; allow it only for reviewed, revision-pinned repos run in a sandbox.
  - Convert untrusted checkpoints in an isolated, network-less job.
- **Detection:**
  - Scan pickles before load (Fickling / modelscan).
  - Alert on process spawns, outbound connections or file writes from a loader process.

### 2. Shared-cache and shared-storage poisoning (Critical; missing from the original)
- **Mechanism:** if tenants share a Hugging Face cache or dataset volume with write access, one tenant (or one
  compromised job) can replace a cached model file. Every other team then loads it, bypassing whatever checks the
  original download had.
- **Controls:**
  - Per-tenant caches, or a **read-only, centrally populated mirror**.
  - Shared storage writable only by the ingestion service.
  - Integrity check (hash) of files at load time, not just at download.
- **Detection:**
  - File-integrity monitoring on the mirror.
  - Alert on writes to shared model paths by anything but the ingestion service.

### 3. Lateral movement through cluster software (High)
- **Mechanism:** Ray, Slurm and Kubeflow-era tooling, and the NCCL/MPI collectives, were built for throughput on
  trusted networks.
  - **NCCL traffic is not authenticated or encrypted.**
  - **Ray's token authentication exists (Ray ≥ 2.52.0) but is off by default** (`RAY_AUTH_MODE=token` enables it).
  - Exposed Ray job APIs have been exploited in the wild (the ShadowRay campaign).
- **Controls:**
  - Network segmentation (Kubernetes NetworkPolicies / VPC rules) per tenant.
  - Enable Ray token auth; never expose dashboards publicly (use SSH or `kubectl port-forward`).
  - Isolate the collective-communication network per job.
- **Detection:**
  - Alert on job submissions from unexpected identities.
  - Flag connections from job pods to other tenants' pods, or to the control plane.

### 4. Container escape through the GPU stack (High; missing from the original)
- **Mechanism:** the GPU driver and the NVIDIA Container Toolkit run with host privileges.
  - **CVE-2024-0132** (critical, 9.0) was a race condition (TOCTOU) in how the toolkit mounts files. In versions
    ≤ 1.16.1 a crafted container image could reach the host filesystem.
  - A later bypass was tracked as **CVE-2025-23359**.
- **Controls:**
  - Keep the NVIDIA Container Toolkit at **1.17.4 or newer** and the driver patched.
  - Use only trusted, signed base images.
  - Run untrusted workloads in stronger isolation (gVisor/Kata-style sandboxes or a dedicated node).
- **Detection:** runtime monitoring for host-path access and unexpected mounts from GPU containers.

### 5. Credential theft after any RCE (High; missing from the original)
- **Mechanism:** the blast radius of risks 1–4 is whatever the job can reach: Hub tokens (which can push models), cloud
  keys, service-account tokens.
- **Controls:**
  - Short-lived, least-privilege credentials per job.
  - Read-only Hub tokens for training jobs.
  - No long-lived keys in images or environment variables; workload identity instead.
- **Detection:** alert on token use from unexpected IPs or for unexpected actions (e.g. a training token pushing a model).

### 6. Cross-tenant leakage through shared GPU contexts and serving caches (Medium–High)
- **Correction to the original:** "dirty VRAM between containers" is overstated for NVIDIA. In the LeftoverLocals
  disclosure (CVE-2023-4969), Trail of Bits confirmed leaks of GPU local memory on **AMD, Apple, Qualcomm and
  Imagination** GPUs, while **NVIDIA and Arm said they were not affected**. On NVIDIA the realistic risks are:
  - shared contexts (**MPS** and time-slicing give weak isolation);
  - **prefix/KV-cache sharing** in inference servers, which can leak prompts through timing;
  - driver bugs.
- **Controls:**
  - **MIG** where available. It is data-centre only (A100/H100 class); consumer cards have no MIG.
  - Otherwise, a dedicated GPU per tenant.
  - Disable cross-tenant prefix caching.
- **Detection:** hard to detect directly; audit GPU-sharing configuration (MPS, time-slicing) per tenant.

### 7. Malicious or poisoned models (Medium–High)
- **Mechanism:** backdoored weights pass general benchmarks but misbehave on triggers.
- **Correction:** Hugging Face revisions are **git commit hashes (SHA-1, 40 hex characters)**; SHA-256 appears only
  as the object IDs for large files. Pin `revision=<commit hash>`.
- **Pinning stops a model changing under you. It does not detect a malicious original.**
- **Controls:**
  - Pin revisions.
  - Allowlist publishers.
  - Behavioural evaluation on held-out and trigger-probe sets before promotion.
  - Provenance records.
- **Detection:** regression and behavioural tests in CI for every model promotion; drift monitoring in production.

### 8. Dependency / package supply chain (Medium–High; missing from the original)
- **Mechanism:**
  - Dependency confusion and typosquatting. The torchtriton incident (PyTorch nightly, December 2022): a public package
    shadowed an internal one.
  - Malicious package versions.
- **Controls:**
  - Internal package mirror with an allowlist.
  - Hash-pinned lockfiles (`pip install --require-hashes`).
  - No ad-hoc `pip install` inside jobs.
- **Detection:** alert on installs outside the lockfile; SBOM diffing per image.

### 9. Silent integrity failures, hardware and software (Medium)
- **Correction:** the original treated this purely as hardware (silent data corruption, ECC). **Software
  silent-correctness bugs** are a separate, real class. Example: PyTorch #201473, where `torch.compile` on CPU returned
  variance 50–100% wrong with no error.
  - Crafted inputs can trigger these paths, so they are not purely non-adversarial.
  - Non-deterministic reduction order is *non-reproducibility*, not a failure.
- **Controls:**
  - Pin framework versions per job.
  - Run differential checks (compiled vs eager, against a float64 reference) for critical kernels.
  - ECC monitoring and node cordoning for hardware faults.
- **Detection:**
  - Loss and gradient-norm anomaly alerts.
  - Canary evaluations between checkpoints.
  - ECC error-rate monitoring.

## What changed vs the Gemini draft
1. **Fixed:** "SHA-256 commit hashes" → git commit hashes (SHA-1); and pinning doesn't catch a malicious original.
2. **Fixed:** "safetensors exclusively" was presented as sufficient → it also needs loader bounds checks, plus
   `weights_only=True` for legacy files.
3. **Corrected:** cross-tenant "dirty VRAM" → LeftoverLocals did not affect NVIDIA; real NVIDIA risks are shared
   contexts, serving caches and drivers. MIG is data-centre only.
4. **Corrected:** silent integrity covers software bugs too, and can be adversarially triggered.
5. **Kept and verified:** Ray token auth exists (≥ 2.52.0), with the added note that it is **off by default**.
6. **Added risks:** shared-cache poisoning (#2), GPU-stack container escape (#4, CVE-2024-0132 / CVE-2025-23359),
   credential theft (#5), package supply chain (#8).
7. **Added:** assets and entry points, and a **detection** for every risk (the exercise asked for one per risk).

**Sources:** [Trail of Bits: LeftoverLocals](https://blog.trailofbits.com/2024/01/16/leftoverlocals-listening-to-llm-responses-through-leaked-gpu-local-memory/) ·
[Wiz: CVE-2024-0132 deep dive](https://wiz.io/blog/nvidia-ai-vulnerability-deep-dive-cve-2024-0132) ·
[Ray token authentication](https://docs.ray.io/en/latest/ray-security/token-auth.html) ·
[PyTorch: compromised nightly dependency](https://pytorch.org/blog/compromised-nightly-dependency/) ·
[PyTorch serialization notes](https://docs.pytorch.org/docs/stable/notes/serialization.html)
