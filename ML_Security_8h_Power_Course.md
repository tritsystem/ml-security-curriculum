# ML systems security: 8-hour power course

*Condensed from the reference library in this folder: Volume I (~1,740 h), Volume II (~22,900 h) and the
senior/principal guide. Eight modules of 60 minutes: **Learn** (the core ideas, written out here), **Read** (verified
links, a few minutes each), **Do** (a hands-on exercise on your own machine, against your own code), **Check** (answers
at the end). Item IDs (A1, R15…) point back into the reference volumes for depth.*

| # | Module | Minutes | Library depth |
|---|---|---|---|
| 1 | The ML stack as an attack surface, and evidence discipline | 60 | Vol I F, J; Guide §1, §8 |
| 2 | Model serialization: pickle → `weights_only` → "safe" formats | 60 | Vol I E; Vol II S4 |
| 3 | Native code and memory safety | 60 | Vol I A, B8; Vol II Q, V1–V2 |
| 4 | GPUs and kernels | 60 | Vol I C; Vol II R13–R16 |
| 5 | Fuzzing and variant analysis | 60 | Vol I B; Vol II U2–U3 |
| 6 | Numerical integrity as security | 60 | Vol I H; Vol II P19, V10, S7 |
| 7 | Serving, supply chain and LLM-app attacks | 60 | Vol I E, G, I; Vol II T5 |
| 8 | From finding to disclosure to principal judgment | 60 | Vol I J; Vol II S, V5–V9 |

---

## Module 1: The ML stack as an attack surface, and evidence discipline (60 min)

**Learn (20 min)**
- The stack, top to bottom: **data and checkpoints → loaders → framework ops and compilers → native kernels → GPU and
  driver → serving and cluster → build and distribution.**
- For each layer ask four questions:
  1. Who controls the input?
  2. What native code touches it?
  3. Where is the trust boundary?
  4. What does failure look like: a crash, RCE, a data leak, or a silently wrong number?
- **The ML twist:** huge untrusted binary inputs (models), lots of fast but unchecked native code, accelerators with
  weak isolation, research-grade cluster software that assumes a trusted network, and integrity failures that are
  *silent*.
- **Evidence ladder:**
  - **T0** a tool hit, **T1** a code reading, **T2** a harness run: all three are leads.
  - **T3** reproduced through the real entry point: the minimum to call something a finding.
  - **T4** T3 plus a fix that flips the repro red → green, with the project's tests still green.
  - **Never round up.** Most bad security reports are T1 claims dressed as T3.
- **Validate the instrument:** any oracle, sanitizer setup or scanner must *fire on a planted bug* and *stay quiet on
  clean code* before you trust its silence.

**Read (25 min)**
- [MITRE ATLAS](https://atlas.mitre.org/): skim the matrix and read 2 case studies.
- [Microsoft: threat modeling AI/ML](https://learn.microsoft.com/en-us/security/engineering/threat-modeling-aiml): the
  question lists.

**Do (15 min)**
Write a one-page threat model for *"a team downloads Hugging Face models and fine-tunes them on a shared GPU server."*
Cover assets, entry points, the top 5 risks, one control and one detection for each.

**Check**
1. Why is a sanitizer report from a hand-built harness T2 and not T3?
2. Name two ML-stack failure modes that produce no crash and no log.

---

## Module 2: Model serialization (60 min)

**Learn (20 min)**
- **`pickle` = code execution.** `__reduce__` returns a callable plus its arguments, and the unpickler calls it. So
  `torch.load` (zip + pickle), joblib, `np.load(allow_pickle=True)` and Keras Lambda layers all execute what's inside
  the file.
- **Defenses, weakest to strongest:**
  1. "Don't load untrusted files" (documentation, which doesn't protect anyone).
  2. Scanning pickle opcodes (GLOBAL/REDUCE). Useful, but bypassable.
  3. A restricted unpickler: `weights_only=True`, an allowlist of tensor and container types. PyTorch made it the
     default in 2.6; older versions had a bypass advisory.
  4. Code-free formats (safetensors).
  5. Loading inside a sandbox.
- **"Safe" formats are still parsers.** safetensors, GGUF and ONNX read *sizes, offsets, shapes and dtypes from the
  file.* The bug classes:
  - a header length or offset past the end of the file → OOB read;
  - shape × dtype-size overflow → undersized allocation → heap overflow;
  - a shape that doesn't match the data length, with kernels trusting the shape;
  - protobuf nesting deep enough to exhaust the stack.
- **Heuristic:** tensors assigned wholesale from a state dict often skip shape checks. That's your bitsandbytes
  #2106/#2107 pattern.
- **Remote code by design:** `trust_remote_code=True` and custom ops are opt-in RCE. Policy: pin model revisions by
  commit hash, mirror internally, and review remote code before enabling it.

**Read (20 min)**
- [Trail of Bits: "Never a dill moment"](https://blog.trailofbits.com/2021/03/15/never-a-dill-moment-exploiting-machine-learning-pickle-files/)
- [PyTorch serialization notes (`weights_only`)](https://docs.pytorch.org/docs/stable/notes/serialization.html)
- [GGUF spec](https://github.com/ggml-org/ggml/blob/master/docs/gguf.md): read it as an attacker and circle every
  size and offset field.

**Do (20 min)**
1. In a scratch folder, build a pickle whose `__reduce__` only calls `print("ran")`. Save it with `torch.save`.
2. Load it with `weights_only=False` (it prints) and with `weights_only=True` (it refuses).
3. Run `python -m pickletools` on the file and find the GLOBAL/REDUCE opcodes.

**Check**
3. Why does safetensors still need bounds checks?
4. Which is the real fix, documentation or a changed default? Why?

---

## Module 3: Native code and memory safety (60 min)

**Learn (20 min)**
| Bug class | ML-shaped example | How you prove it |
|---|---|---|
| Integer overflow in sizes/indices | `numel > 2^31` with int32 offsets (long context, big embeddings) | test at 2^31±1 |
| Size arithmetic | 4-bit packing with floor division undersizing a buffer (your bnb #2105) | sanitizer + exact-size allocation |
| Missing bounds on indices | gather/scatter/embedding/CTC with untrusted indices | fuzz the index tensor |
| Uninitialized memory | `torch.empty` exposed, padding reads | MSan / compute-sanitizer initcheck |
| Races | atomics, shared memory, missing barriers | TSan / racecheck |
| Unchecked allocation | ignoring a NULL from `calloc` (your miniupnp #922) | review + fault injection |

- **Sanitizers:** ASan (OOB, use-after-free), UBSan (integer/UB), MSan (uninitialized), TSan (races). **Caching
  allocators hide OOB.** An overrun lands inside a bigger cached block, so the sanitizer sees nothing. For CUDA, set
  `PYTORCH_NO_CUDA_MEMORY_CACHING=1` when hunting.
- **Severity is contextual:** who controls the input, and is the process multi-tenant? A project's own SECURITY.md
  decides classification. bitsandbytes counts GPU OOB as correctness, not security.

**Read (20 min)**
- [Google sanitizers wiki](https://github.com/google/sanitizers/wiki): the ASan and MSan pages.
- [SEI CERT C: integer rules (INT30–INT32)](https://wiki.sei.cmu.edu/confluence/display/c/SEI+CERT+C+Coding+Standard)

**Do (20 min)**
1. Write a 20-line C (or Python C-extension) function that copies `n * elem_size` bytes, with a 32-bit multiply.
2. Compile with `-fsanitize=address,undefined` and feed it values that overflow.
3. Watch UBSan catch the multiply and ASan catch the overrun. Fix it with a checked multiply.

**Check**
5. Why can an OOB write on the GPU go undetected without disabling the caching allocator?
6. Give one input-control question that decides whether a GPU OOB is "security".

---

## Module 4: GPUs and kernels (60 min)

**Learn (20 min)**
- **The CUDA model:** a grid of blocks of threads. Global index = `blockIdx.x * blockDim.x + threadIdx.x`. **The
  bugs:**
  - the tail mask (`if (i < n)`) missing or off by one;
  - int32 index × stride overflow (pytorch #202434: offsets above 2^31 in memory-efficient attention);
  - shared-memory races without `__syncthreads()`.
- **Triton** hides threads behind block programs, but masks (`mask=offs < n`) and `int64` offsets
  (`pid.to(tl.int64)`) are still yours to get right. You saw Unsloth's `LONG_INDEXING` switch for exactly this.
- **compute-sanitizer:** `memcheck` (OOB), `racecheck`, `initcheck`, `synccheck`. Expect 10–100× slowdowns, so run
  small shapes that still cross the boundaries.
- **Isolation ladder:** time-slicing → MPS (shared context, weak) → MIG (hardware partitions) → a dedicated GPU →
  confidential computing.
  - **Residual memory:** LeftoverLocals read another process's GPU local memory.
  - **Cache side channels:** prefix/KV-cache sharing across tenants can leak prompts through timing.

**Read (20 min)**
- [CUDA Programming Guide: thread hierarchy and memory hierarchy sections](https://docs.nvidia.com/cuda/cuda-c-programming-guide/)
- [Trail of Bits: LeftoverLocals](https://blog.trailofbits.com/2024/01/16/leftoverlocals-listening-to-llm-responses-through-leaked-gpu-local-memory/)
- [Compute Sanitizer docs: memcheck](https://docs.nvidia.com/compute-sanitizer/)

**Do (20 min)**
1. On your RTX 5060, write a Triton kernel with the tail mask deliberately wrong (`offs <= n`).
2. Run it with `PYTORCH_NO_CUDA_MEMORY_CACHING=1 compute-sanitizer --tool memcheck python kernel.py` and read the
   report.
3. Fix the mask; confirm the report is clean *and* the output matches a float64 CPU reference.

**Check**
7. Why does shrinking the head count and head dim not help you fit the #202434 repro into 8 GB?
8. MPS vs MIG: which one actually separates memory?

---

## Module 5: Fuzzing and variant analysis (60 min)

**Learn (15 min)**
- **Coverage-guided fuzzing** (libFuzzer, AFL++, Atheris for Python) mutates inputs and keeps the ones that reach new
  code. Pair it with sanitizers so silent memory errors become crashes.
- **Good ML targets:** model-format headers (safetensors/GGUF/ONNX), tokenizers, image/audio decoders in data loaders,
  custom-op argument parsing.
- **Structure-aware fuzzing:** for formats with checksums or nested lengths, generate structurally valid inputs, or
  mutate fields, not raw bytes.
- **Variant analysis:** one confirmed bug → a query (CodeQL/semgrep) for the same pattern everywhere. Sweeping sibling
  code is where the second and third findings come from. Your `fp8_linear` bias lead started as exactly this kind of
  sibling question.

**Read (20 min)**
- [The Fuzzing Book: "Introduction to Fuzzing" and "Coverage" chapters](https://www.fuzzingbook.org/)
- [Atheris README](https://github.com/google/atheris)

**Do (25 min)**
1. Write a tiny safetensors-style header parser in pure Python: an 8-byte length, then JSON with offsets. Leave out
   one bounds check on purpose.
2. Fuzz it with Atheris for 10 minutes and time how long until the crash.
3. Fix the check and re-fuzz.
4. Write a one-line semgrep rule for `torch.load(` without `weights_only=True`, and run it on one of your cloned repos.

**Check**
9. Why does fuzzing without sanitizers miss many memory bugs?
10. What makes a good variant-analysis query: too narrow or too broad? How do you tell?

---

## Module 6: Numerical integrity as security (60 min)

**Learn (20 min)**
- **A silent wrong answer is an integrity failure:** no crash, no alert, a quietly worse model. Your specialty, and
  increasingly what ML-infrastructure teams probe in interviews.
- **Floating point in one breath:** relative spacing ε (fp32 2^-23, bf16 2^-7, fp16 2^-10); catastrophic
  cancellation when subtracting near-equal numbers; summation error grows with n unless you use pairwise, Kahan or
  cascade summation; overflow and underflow at the extremes.
- **Patterns you've measured:**
  - **Derivative from a rounded output:** sigmoid′ = y(1−y) cancels once y rounds to 1. In bf16 it's more than 1%
    wrong from |x|≈1.7. (Your autograd study: real in bf16, negligible in fp64 practice.)
  - **Perf heuristics exposing latent bugs:** pytorch #201473. A tail-vectorization heuristic routed masked tails to a
    scalar kernel that shared one Welford helper, silently dropping 4096-element chunks (variance 50–100% wrong).
  - **Silent defaults:** Unsloth turns fp32 training into bf16 autocast silently. Intended, so a convention, not a bug.
- **The oracle method:**
  - The reference is float64 (or mpmath).
  - The bar is *the plain framework in the same dtype*: you're asking whether the fast path is worse than the normal
    path.
  - Validate with planted bugs.
  - **Sensitivity trap:** in bf16, normal rounding noise (~1%) hides 2–5% formula bugs. Test formulas in fp32 and
    precision in bf16.

**Read (20 min)**
- [Goldberg: *What Every Computer Scientist Should Know About Floating-Point*](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html):
  the sections on rounding error and cancellation.
- [PyTorch numerical accuracy notes](https://docs.pytorch.org/docs/stable/notes/numerical_accuracy.html)

**Do (20 min)**
1. Reuse `oracle.py` from `OSS Assessment\Unsloth_Stage1_harness\`.
2. Point it at any `torch.compile`d function of your choice.
3. Plant a 1% scale bug and confirm it's caught in fp32 but *not* reliably in bf16. That's the sensitivity lesson made
   concrete.

**Check**
11. Why must an oracle's tolerance be relative to the same-dtype baseline, not to zero error?
12. How did Inductor's cache almost fake a "fix didn't work" result, and how do you rule that out?

---

## Module 7: Serving, supply chain and LLM-app attacks (60 min)

**Learn (25 min)**
- **Cluster software assumes a trusted network.** Ray's job API, TorchServe's management API, and Jupyter, TensorBoard
  or MLflow exposed to the internet have all been exploited. The vendor's threat model ("put it on a private network")
  becomes your control requirement. **RPC that pickles** (torch.distributed.rpc, Celery with pickle) is
  deserialization over the network.
- **Supply chain:**
  - Dependency confusion: torchtriton (2022), where a public package shadowed an internal nightly dependency.
  - Malicious pickles on model hubs.
  - CI `pull_request_target` "pwn requests" and expression injection.
  - Self-hosted GPU runners shared with forks.
  - Mitigations: provenance (SLSA), signing (Sigstore), pinning by hash, internal mirrors.
- **LLM applications:**
  - **Indirect prompt injection:** untrusted content (web pages, emails, documents) carries instructions to an agent
    with tools.
  - **Data exfiltration through rendered links and images.**
  - **System-prompt leaks.**
  - **Systems-level controls:** least-privilege tools, human confirmation for side effects, audit logs, rate limits,
    allowlists. Your `mcp-gateway` is an example. Prompt filters alone are not enough.

**Read (20 min)**
- [Oligo: ShadowRay](https://www.oligo.security/blog/shadowray-attack-ai-workloads-actively-exploited-in-the-wild)
- [PyTorch: compromised nightly dependency](https://pytorch.org/blog/compromised-nightly-dependency/)
- [Greshake et al., indirect prompt injection (abstract and section 1)](https://arxiv.org/abs/2302.12173)

**Do (15 min)**
Audit one of your own MCP servers or agents. List every tool that has side effects (file writes, network, git, email).
For each, write down what stops an injected instruction from triggering it. Any tool where the answer is "nothing"
is your top fix.

**Check**
13. Why is "Ray says it's by design" not the end of the analysis for you?
14. Name two controls for indirect prompt injection that don't depend on detecting the injection.

---

## Module 8: From finding to disclosure to principal judgment (60 min)

**Learn (25 min)**
- **The finding bar:**
  1. It runs, with a minimal repro.
  2. It's reached through the real entry point (T3).
  3. It's an error, not rounding (fp64 control).
  4. The failure mode is classified.
  5. The root cause is located at a file and line.
  6. It's not a documented convention.
  7. It's not a duplicate: issues *and* PRs, open *and* closed, and read every comment for claims. #49978 taught this
     one: the claim was the last line of the issue body.
  8. For a fix: a red→green regression test plus a sweep of sibling code.
- **Channel:** read SECURITY.md first. Security → private advisory or the security email. Correctness → a public issue
  or PR. **Never pitch services into a disclosure channel**; disclosure is never conditional on business.
- **Gates:** many projects require a triage label before a PR (PyTorch's `actionable`). The right move is evidence in
  a comment first, as you did on #201473.
- **AI policy:** disclose and contain AI-generated content, add human commentary, and stand behind every claim.
- **Principal judgment:**
  - Kill bug *classes*: secure defaults, paved roads, lint rules.
  - Measure programme outcomes: classes eliminated, time to patch, coverage, not bug counts.
  - Know when "won't fix" is right. Your autograd study is the model: measure the impact and the cost, then recommend.

**Read (15 min)**
- [CERT Guide to Coordinated Vulnerability Disclosure (intro and "Principles")](https://certcc.github.io/CERT-Guide-to-CVD/)
- [PyTorch SECURITY.md](https://github.com/pytorch/pytorch/blob/main/SECURITY.md)

**Do (20 min)**
1. Tell two of your case studies out loud in 3 minutes each, using the structure: *context → mechanism → evidence tier
   → fix/decision → what it taught.* Use #201473 and the bitsandbytes OOB.
2. Then answer the principal question: *"Design secure model ingestion for a 500-engineer company"* in 5 bullets.

**Check**
15. When is filing a GPU OOB publicly correct, and when is it a mistake?
16. What metric shows a security programme is working, beyond the number of bugs found?

---

## Answer key
1. The harness bypasses the real caller and its state; the product may never deliver those inputs (T2 ≠ reachable).
2. Any two of: silent numeric corruption (e.g. #201473), a dropped bias or gradient, data poisoning, a cache leak
   between tenants, a wrong default dtype.
3. The header's sizes, offsets and shapes are attacker-controlled; the parser and the kernels behind it can read or
   write out of bounds.
4. A changed default. Most users never read docs; secure-by-default removes the whole class (`weights_only=True` in 2.6).
5. The overrun lands inside a larger cached block the allocator owns, so no fault is raised and the sanitizer sees a
   valid access.
6. Does an attacker control the input (e.g. a downloaded checkpoint)? Is the GPU shared with other tenants?
7. The tensor size needed to cross 2^31 elements stays the same; shrinking H×D only raises the sequence length needed.
8. MIG. MPS shares one context.
9. Many memory errors corrupt silently and never crash; sanitizers turn them into crashes the fuzzer can see.
10. Tune it until it finds the known bug plus a manageable set of hits. Too narrow misses variants; too broad buries
    you in noise.
11. Every dtype has inherent rounding error. The question is whether the fast path is *worse than the normal path*,
    not whether it is exact.
12. The compiled-kernel cache served pre-fix kernels with identical outputs. Rerun with
    `TORCHINDUCTOR_FORCE_DISABLE_CACHES=1` and check the generated code itself.
13. Real deployments expose it anyway, so your controls (network policy, authentication proxies) must cover the gap
    the vendor won't.
14. Least-privilege tools; human confirmation for side effects; blocking outbound links and images; separating
    untrusted content from instructions.
15. Correct when the project's own security policy classifies it as correctness *and* there is no plausible
    multi-tenant or attacker-input exploit path. A mistake when untrusted input reaches it in shared deployments: go
    private.
16. Bug classes eliminated, time to patch, sanitizer and fuzzing coverage in CI, adoption of safe-by-default APIs.

---

**After the 8 hours:** Volume I phases 1–2 (~700 h) are the natural next step. Use Volume II as the long-term reference
library.
