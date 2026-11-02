# Gemini's original draft (kept for comparison)

*Captured 2026-10-30 from https://share.gemini.google/5OSxqrQHtqFK. The corrected version is Threat_Model_HF_Models_Shared_GPU_Cluster.md.*

1-Page Threat Model: Hugging Face Models on Shared GPU Clusters

Scope: Evaluating the severity and blast radius of running unvetted external models and pipelines on multi-tenant, shared GPU infrastructure.

Severity Ranking Matrix

Rank

	

Severity

	

Threat Item

	

Primary Vector

	

Impact / Blast Radius

1

	

Critical

	

#3 & #6 Unchecked Native Code / Untrusted Binary Input

	

Unsafe deserialization (pickle), malicious custom C++/CUDA ops

	

Immediate Remote Code Execution (RCE), host compromise

2

	

High

	

#4 Research-Grade Cluster Software

	

Unauthenticated schedulers (Slurm/Ray), plaintext IPC (NCCL/MPI)

	

Cluster-wide lateral movement, full tenant takeover

3

	

High

	

#2 Accelerators with Weak Isolation

	

Shared GPU VRAM, absence of MIG, dirty memory retention

	

Cross-tenant data leakage (weights, activations), DoS

4

	

Medium–High

	

#1 Model Training Data Corruption

	

Data poisoning, backdoor triggers in downloaded checkpoints

	

Downstream inference compromise, persistent model bias

5

	

Medium

	

#5 Silent Integrity Failures

	

Silent Data Corruption (SDC), uncorrected ECC bit-flips, non-determinism

	

Wasted GPU hours, degraded convergence (non-adversarial)

Detailed Threat Breakdown
1. [CRITICAL] Untrusted Binary Input & Unchecked Native Code (#6 & #3)

Risk Mechanism: Older PyTorch checkpoints (.bin, .pt) rely on Python's pickle engine, allowing arbitrary OS-level payload execution upon calling torch.load(). Furthermore, loading repositories requiring trust_remote_code=True allows unchecked execution of arbitrary Python, C++, or inline CUDA code.

Why it ranks #1: Provides immediate initial access and execution capabilities with the privileges of the running container or host service account.

Key Mitigations:

Enforce serialization formats using safetensors exclusively.

Ban trust_remote_code=True in production pipelines; audit all custom CUDA kernels.

2. [HIGH] Research-Grade Cluster Software with Implicit Network Trust (#4)

Risk Mechanism: Orchestration engines (Ray, unauthenticated Slurm, Kubeflow) and distributed communications libraries (NCCL, OpenMPI) are traditionally engineered for raw throughput rather than zero-trust security. Inter-node communications are frequently unencrypted and lack mutual TLS (mTLS).

Why it ranks #2: Once initial execution is achieved via Threat #1, research software allows trivial lateral pivot across the InfiniBand/RoCE network to compromise all co-located workloads.

Key Mitigations:

Implement strict network policies (Kubernetes NetworkPolicies / VPC segmentation).

Enable Ray token authentication and mTLS across control and data planes.

3. [HIGH] Accelerators with Weak Isolation (#2)

Risk Mechanism: Standard GPU virtualization often leaves memory spaces shared across time-sliced containers without zero-initialization guarantees between allocations, or leaves physical PCIe/NVLink interconnects vulnerable to cache/timing side-channel inspection.

Why it ranks #3: Enables adjacent tenants to extract proprietary model weights, residual training gradients, or proprietary prompt embeddings from dirty VRAM.

Key Mitigations:

Enforce hardware-level partitioning (NVIDIA Multi-Instance GPU / MIG).

Require runtime memory wiping policies between job cycles.

4. [MEDIUM–HIGH] Model Training Data Corruption (#1)

Risk Mechanism: Downloaded base weights or auxiliary training corpora may be subtly modified to contain trigger backdoors or poisoned gradients that activate specific outputs on specific inputs without dropping general validation benchmarks.

Why it ranks #4: Compromises algorithmic integrity and inference trustworthiness, though it does not compromise the underlying compute infrastructure directly.

Key Mitigations:

Verify SHA-256 commit hashes on Hugging Face Hub releases.

Conduct offline behavioral evaluation and data provenance tracking.

5. [MEDIUM] Silent Integrity Failures (#5)

Risk Mechanism: Transient hardware errors (e.g., Silent Data Corruption in ALU/HBM), failing memory cells not caught by ECC, or non-deterministic floating-point reduction order across thousands of GPU cores.

Why it ranks #5: While costly in terms of compute efficiency and debugging overhead, this is predominantly an operational and reliability failure rather than an active adversarial attack vector.

Key Mitigations:

Enable strict ECC monitoring with automated node cordoning on multi-bit error thresholds.

Implement regular deterministic checkpointing and loss anomaly detection.

