# Low-level ML systems security: study guide, senior and principal level

*Written 2026-10-30. Case studies marked ★ come from your own verified work. CVE numbers and dates for public incidents
are as recalled, so check each against NVD or the vendor advisory before quoting it in an interview or document.*

---

## 0. What the role actually is

"ML security" splits into two very different jobs:

| Model-level (ML research security) | Systems-level (this guide) |
|---|---|
| adversarial examples, poisoning, extraction, jailbreaks | the code that loads, runs, serves and ships models |
| measured in accuracy and attack success rate | measured in RCE, memory corruption, data exposure, integrity |
| AI red team | product/infrastructure security, with an ML stack as the target |

Systems-level ML security is classic low-level security (parsers, memory safety, deserialization, IPC, supply chain,
isolation) applied to a stack with unusual properties:
- **Huge untrusted binary inputs.** Checkpoints and datasets run to gigabytes, often fetched from public hubs.
- **Native code everywhere.** C++/CUDA/Triton kernels, written for speed, with few bounds checks.
- **Accelerators with weak isolation.** GPU memory, shared hardware and vendor drivers.
- **Research-grade distributed systems.** Built for trusted clusters, then exposed to networks.
- **Silent wrong answers.** An integrity bug can be invisible: a model just gets worse.

**Senior** = you find, prove, fix and prevent bugs in a component, end to end.
**Principal** = you set the threat model and the secure defaults for a whole stack or org, and move upstream projects.

---

## 1. The ML stack as an attack surface (memorize this map)

```
[Data / checkpoints / tokenizers]  -> loaders, parsers, deserializers     (§2, §3)
[Framework: PyTorch / JAX / TF]    -> ops, autograd, compilers (Inductor)  (§3, §7)
[Kernels: CUDA / Triton / CPU]     -> index math, allocation, sync         (§3)
[Accelerator + driver]             -> memory isolation, side channels      (§4)
[Serving / training cluster]       -> RPC, schedulers, dashboards, agents  (§5)
[Build + distribution]             -> wheels, extensions, hubs, CI         (§6)
```

For each layer, ask:
1. **Who controls the input?**
2. **What native code touches it?**
3. **What is the trust boundary?**
4. **What does failure look like: a crash, RCE, a leak, or a silently wrong number?**

---

## 2. Model serialization: the number-one systems risk

### 2.1 Pickle and its relatives
- `pickle` runs arbitrary callables at load (`__reduce__`), so loading an untrusted pickle *is* code execution.
- Affected formats: `torch.load` (zip file plus pickle), joblib (scikit-learn), `numpy.load(allow_pickle=True)`,
  older Keras/TF formats with Lambda layers, and any "just pickle the object" cache.
- **Mitigations:**
  - restricted unpicklers (`weights_only=True`: an allowlist of tensor and container types);
  - formats with no code (safetensors);
  - scanning (pickle opcode analysis, e.g. Trail of Bits' *Fickling*);
  - sandboxed loading.
- **Know the history.** PyTorch made `weights_only=True` the default for `torch.load` in 2.6. Before that, there was an
  advisory showing `weights_only=True` could itself be bypassed in older versions (recalled as CVE-2025-32434, ≤2.5.1;
  verify).
- **Principal lesson: flipping a default is the real fix.** Docs that say "don't load untrusted files" do not protect
  users.

★ **Case study (details withheld until the advisory is published).** A library wrapped `torch.load` on user-supplied
paths without `weights_only`. You filed it as a private advisory.
- **Talking points:** why a static scanner (langrisk) missed it (one dangerous call; volume-based scanners can't see
  single sinks); how you proved reachability; why GHSA and not a public issue.

### 2.2 "Safe" formats are still parsers
safetensors, GGUF, ONNX (protobuf) and TFRecord carry no code, but the loader still reads **sizes, offsets, shapes and
dtypes from the file**. The bug classes:
- **header length or offset** past the end of the file, leading to an out-of-bounds (OOB) read;
- **shape × dtype-size overflow**, so the allocation is too small and the next write overflows the heap;
- **shape that doesn't match the data length**, so a kernel trusts the shape;
- **recursion or nesting depth** (protobuf), leading to stack exhaustion.

★ **Case study: bitsandbytes `dequantize_4bit` OOB read (#2106/#2107)**, from an untrusted checkpoint's shape.
- Sanitizer-confirmed at T4.
- **Talking points:**
  - **The heuristic:** tensors assigned wholesale from a state dict skip shape checks.
  - **The disclosure choice:** the repo's own security guide down-classifies GPU OOB to correctness/reliability, so you
    filed publicly. Read the target's SECURITY.md before choosing a channel.

★ **Case study: bitsandbytes `quantize_4bit` under-allocation (PR #2105).** Floor division undersizes the packed buffer
for wide `quant_storage`, so the CUDA kernel writes out of bounds.
- **The bug class:** size arithmetic.
- **The proof:** compute-sanitizer memcheck.

### 2.3 Remote code by design
`trust_remote_code=True` (Hugging Face), Keras Lambda layers, custom ops in checkpoints, and TorchScript/ONNX custom
ops. **Senior:** know where each executes and how to disable it. **Principal:** an org policy that pins revisions,
mirrors internally and reviews remote code.

---

## 3. Native code: kernels, extensions, index math

### 3.1 Bug classes
| Class | ML-specific shape | Detection |
|---|---|---|
| 32-bit index overflow | `numel > 2^31` in long-context attention, big embeddings, int32 stride × index | tests at 2^31±1; read pointer arithmetic |
| Size arithmetic | packing (4-bit, 2 values per byte), floor division, `ceil_div` mistakes | sanitizer with exact-size allocations |
| Missing bounds on indices | gather/scatter/embedding with untrusted indices; CTC targets | fuzz the indices; `TORCH_CHECK` audit |
| Uninitialized memory | `torch.empty` returned or exposed; a padding read | compute-sanitizer **initcheck** |
| Races | atomics, shared memory, missing `__syncthreads` | compute-sanitizer **racecheck**/**synccheck** |
| Unchecked allocation | `calloc`/`malloc` NULL ignored | review; fault injection |

★ **Case study: miniupnp unchecked `calloc` (PR #922).** Not ML, but the same pattern as unchecked allocation in native
extensions, verified at T4 on 8 of 9 sites.
- **Talking point:** robustness vs security grading.

### 3.2 Tools to be fluent in
- **NVIDIA compute-sanitizer:** `memcheck`, `racecheck`, `initcheck`, `synccheck`. Know the overhead, and that you need
  exact-size allocations (caching allocators hide OOB; set `PYTORCH_NO_CUDA_MEMORY_CACHING=1`).
- **ASan/UBSan** on CPU extensions; **libFuzzer/atheris** for parsers; **CodeQL/semgrep** for sink-finding.
- **Differential oracles:** CPU vs GPU, eager vs compiled, fp64 reference. Most memory bugs in kernels first show up as
  wrong numbers.

---

## 4. Accelerators and isolation

- **Residual memory:** GPU memory and on-chip local/shared memory may not be cleared between tenants or kernels.
  *LeftoverLocals* (Trail of Bits, 2024, CVE-2023-4969; verified) showed reading another process's GPU local memory on AMD, Apple, Qualcomm and Imagination GPUs. NVIDIA and Arm said they were not affected. **Talking point:** why that matters for multi-tenant LLM serving.
- **Isolation options, weakest to strongest:** time-slicing → MPS (shared context, weak isolation) → MIG (hardware
  partitions) → a whole GPU per tenant → confidential computing (H100 CC mode; verify what's in scope).
- **Side channels:** timing and power, KV-cache or prefix-cache sharing across tenants (prompt leakage by cache-hit
  timing), and speculative decoding behaviour.
- **Driver and firmware:** a large kernel-mode attack surface; patch cadence is part of the threat model.

**Principal question:** "Design multi-tenant inference on shared GPUs." The answer is a ladder of isolation against
cost, plus cache-partitioning policy, plus a zeroing guarantee and how you'd *test* it.

---

## 5. Serving and distributed training

- **Unauthenticated control planes built for trusted clusters.**
  - **Ray:** the job API was exposed with no auth; "ShadowRay", recalled as CVE-2023-48022, was disputed by the vendor
    as "by design", which is itself a lesson in vendor threat models.
  - **TorchServe "ShellTorch":** management API exposure, SSRF and deserialization, recalled as CVE-2023-43654
    plus others.
  - **Jupyter, TensorBoard, MLflow and Kubeflow** exposed on the internet.
- **RPC that pickles:** `torch.distributed.rpc`, multiprocessing queues, Celery with a pickle serializer.
- **Collective communication:** NCCL/Gloo assume a trusted network; a rogue rank can corrupt gradients (integrity) or
  crash peers.
- **Agent and tool surfaces:** MCP servers, function calling, notebooks run by agents. **Principal:** treat
  tool-calling agents as untrusted input routed to privileged APIs: audit logs, rate limits, allowlists. Your own
  `mcp-gateway` package is a working example of this.

---

## 6. Supply chain

- **Dependency confusion:** the *torchtriton* incident (PyTorch nightly, Dec 2022). A public PyPI package shadowed an
  internal nightly dependency and exfiltrated data.
- **Model hubs:** malicious pickles uploaded as models; typosquatted model names; revision pinning by commit hash.
- **Compiled wheels and CUDA extensions:** build provenance (SLSA), reproducible builds, signing (Sigstore).
- **CI/CD:**
  - `pull_request_target` "pwn requests";
  - secret exfiltration via expression injection;
  - self-hosted GPU runners shared across forks (very common in ML repos).
- ★ **Case study: act (GitHub Actions runner) coercion leading to secret exfiltration.** You found it independently;
  it turned out to duplicate an open PR, so you verified their fix rather than filing.
  **Talking point:** the dedup discipline.

---

## 7. Numerical integrity is a security property

Silent wrong answers are an integrity failure: no crash, no alert, a degraded model. Interviewers at ML infra companies
increasingly probe this.

- **Classes:**
  - dtype loss;
  - accumulation precision;
  - singular points;
  - reduced-precision backward;
  - compiler miscompiles;
  - nondeterminism.
- ★ **Case study: PyTorch #201473.** Inductor CPU silently drops whole 4096-element chunks of a Welford reduction (var,
  std, layer_norm): 50–100% wrong.
  - **Bisected trigger:** a performance heuristic (#178243) routed masked tails to a scalar kernel, exposing a latent
    shared-helper bug.
  - **Minimal fix verified T4** (833 tests passing), with an honest precision trade-off and three design options left
    for the maintainers.
  - **Talking points:** perf heuristics expose latent correctness bugs; caches can fake a "fix didn't work" (disable
    the Inductor caches); instruments must be validated.
- ★ **Case study: an autograd tail-derivative study.**
  - **Showed:** a cluster of "bugs" was practically negligible in fp64/fp32, but real in bf16.
  - **Measured:** the fix cost (+0% to +26% saved memory, depending on the pattern).
  - **Talking point:** a well-measured "this isn't serious" is principal-level judgment.
- ★ **Case study: the Unsloth assessment.**
  - **Coverage:** 603 fp64 differential checks; no bugs found. You validated the instrument by catching planted bugs
    first.
  - **Talking points:** a validated negative result; mixed-precision defaults that are silent but intended (convention
    vs bug).

---

## 8. Methodology (how you work: say this in interviews)

1. **Threat model first:** assets, inputs, trust boundaries, failure impact.
2. **Evidence tiers** (your T0–T4 ladder):
   - **T0–T2 are leads:** a scanner hit, a code reading, a harness run.
   - **T3 is the minimum for a finding:** it reproduces through the real entry point.
   - **T4 is a verified fix:** red → green, with the project's own tests still passing.
   - **Never round up.**
3. **Validate the instrument:** an oracle or sanitizer setup must fire on a planted bug and stay quiet on clean code.
4. **Dedup before filing:** issues *and* PRs, open *and* closed; read every comment for claims.
5. **Choose the disclosure channel from the target's SECURITY.md:** security → private advisory; correctness →
   public issue/PR. Never pitch into a disclosure inbox.
6. **Fix the class, not the instance:** sweep sibling code; add a lint or detector; change the default.

---

## 9. Senior vs principal: what each level must show

| Dimension | Senior | Principal |
|---|---|---|
| Scope | a component or library | a stack, product line or org |
| Output | bugs found → proven → fixed → tested | threat models, secure defaults, paved roads, policy |
| Technique | sanitizers, fuzzers, kernel reading, exploit proof | choosing which classes to kill and how; cost–benefit |
| Influence | upstream PRs, reviews | changing upstream defaults (e.g. `weights_only`), cross-org standards |
| Judgment | severity of one bug | portfolio risk; when "won't fix" is right; measuring program effectiveness |
| Communication | clear repro and fix | exec-level risk framing; precise public disclosure |

---

## 10. Practice labs (run on your own machine, against your own code)

1. **Pickle loading:**
   - Write a model file whose `__reduce__` only prints a message.
   - Show that `torch.load(weights_only=False)` runs it and `weights_only=True` refuses it.
   - Then write an opcode scanner that flags the GLOBAL/REDUCE opcodes.
2. **Fuzz a parser:** use atheris on a minimal safetensors-style header parser you write yourself, with deliberately
   missing bounds checks. Measure time-to-crash, then fix and re-fuzz.
3. **OOB kernel and sanitizer:**
   - Write a Triton or CUDA kernel with an off-by-one in the tail mask.
   - Show the wrong output, then the `compute-sanitizer memcheck` report.
   - Then turn off the caching allocator and see the difference.
4. **2^31 boundary:** a toy kernel with an int32 offset; derive the minimum tensor size that triggers it, and check
   whether it fits in 8 GB (the reasoning you just did for pytorch #202434).
5. **Differential oracle:** take your `oracle.py` from the Unsloth harness, plant a bug, and confirm it's caught. Then
   apply it to a new kernel library.
6. **Threat-model write-up:** one page for "a team downloads Hugging Face models and fine-tunes them on a shared GPU
   cluster". Cover assets, entry points, top 5 risks, controls and detection.

---

## 11. Interview questions, with answer sketches

**Senior**
1. *"Is safetensors safe?"* No code execution, but the loader still trusts header sizes, offsets and shapes. Check
   bounds, overflow and shape against byte length; fuzz the parser.
2. *"A CUDA kernel returns wrong results only for very large inputs. How do you investigate?"*
   - Suspect int32 index math, and test at 2^31±1.
   - Use compute-sanitizer with caching disabled.
   - Read the pointer arithmetic and run a differential test against CPU.
3. *"How would you prove a deserialization bug is reachable?"* Through the product's real load path (T3), not a harness.
   Show the call chain actually running, with a benign payload.
4. *"GPU OOB: security or correctness?"* It depends on the attacker's control and the deployment. Read the project's
   own security policy. bitsandbytes classifies it as correctness; you explain why that is defensible and where it
   isn't (multi-tenant).

**Principal**
1. *"Design secure model ingestion for the company."*
   - Internal mirror, revision pinning by hash, format allowlist (safetensors), conversion in a sandbox.
   - Scanning for pickles, provenance attestation, `trust_remote_code` review, monitoring.
2. *"Multi-tenant GPU inference: what isolation do you buy?"* Walk through the isolation ladder against cost, cache
   partitioning, a zeroing guarantee and a test plan; know where MIG/CC aren't enough.
3. *"A maintainer says your bug isn't worth fixing because of the perf cost. What do you do?"* Measure impact and cost
   (your autograd study); propose a targeted fix (dtype-gated, opt-in); accept "won't fix" when the data says so.
4. *"How do you measure whether an ML security program works?"* Classes eliminated (not bugs found), time to patch,
   coverage of fuzzing and sanitizers in CI, default-safe API adoption, incident trends.

---

## 12. Reading list (canonical sources: verify links and current versions)
- PyTorch docs: `torch.load` / serialization security notes, and the `weights_only` change in 2.6.
- The safetensors design notes (Hugging Face).
- Trail of Bits blog: *Fickling* (pickle analysis), *LeftoverLocals* (GPU local memory leak).
- NVIDIA compute-sanitizer documentation.
- OWASP Machine Learning Security Top 10; OWASP Top 10 for LLM Applications.
- MITRE ATLAS (adversarial threat landscape for AI systems).
- NIST AI 100-2 (adversarial ML taxonomy); Google's Secure AI Framework (SAIF).
- OpenSSF / SLSA (supply-chain levels); Sigstore.
- GitHub Security Lab write-ups on `pull_request_target` and Actions injection.
- Protect AI / Hugging Face posts on malicious models on hubs.

---

## 13. Your 4-week plan
| Week | Focus | Deliverable |
|---|---|---|
| 1 | §2 serialization + Labs 1–2 | pickle scanner + a fuzzed parser, written up |
| 2 | §3–4 kernels/GPU + Labs 3–4 | a sanitizer-proven OOB demo and an int32 boundary note |
| 3 | §5–6 serving and supply chain + Lab 6 | threat model for shared-cluster fine-tuning |
| 4 | §7–9 + mock interviews (§11) | 6 case-study stories (★) told in 3 minutes each, with tiers stated |
