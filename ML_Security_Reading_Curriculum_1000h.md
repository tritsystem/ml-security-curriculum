# ML systems security: indexed reading curriculum (~1,700 hours)

*Built 2026-10-30. Every link was checked live that day (HTTP 200, and arXiv IDs matched against their real titles).
Two publisher sites block automated checks (H2 SIAM, A10 Agner Fog); both are the official pages. Hours are
realistic **estimates** for careful study with notes and exercises, not skim time. Companion:
`ML_Systems_Security_Senior_Principal_Guide.md` in this folder.*

## Index

| Part | Topic | Items | Est. hours |
|---|---|---|---|
| [A](#a-systems-and-exploitation-foundations) | Systems and exploitation foundations | A1–A10 | 510 |
| [B](#b-fuzzing-sanitizers-and-program-analysis) | Fuzzing, sanitizers, program analysis | B1–B10 | 177 |
| [C](#c-gpus-cuda-and-kernels) | GPUs, CUDA, kernels | C1–C7 | 141 |
| [D](#d-ml-framework-internals) | ML framework internals | D1–D7 | 193 |
| [E](#e-model-serialization-and-supply-chain) | Model serialization and supply chain | E1–E15 | 53 |
| [F](#f-threat-modeling-and-ai-security-frameworks) | Threat modeling and AI-security frameworks | F1–F8 | 67 |
| [G](#g-adversarial-ml-and-llm-security) | Adversarial ML and LLM security | G1–G12 | 147 |
| [H](#h-numerical-correctness) | Numerical correctness | H1–H6 | 116 |
| [I](#i-serving-and-distributed-infrastructure) | Serving and distributed infrastructure | I1–I4 | 22 |
| [J](#j-vulnerability-research-and-disclosure) | Vulnerability research and disclosure | J1–J9 | 251 |
| [K](#k-hands-on-ranges) | Hands-on ranges | K1–K4 | 65 |
| | **Total** | **94 links** | **~1,742** |

## Suggested order (four phases; about 10 h/week ≈ 3.3 years, 20 h/week ≈ 1.7 years)

| Phase | Hours | Read | Goal |
|---|---|---|---|
| 1. Core | ~300 | A1–A2, A5 (first modules), B1, B5–B8, E1–E7, H1, F1–F3 | You can exploit a memory bug, fuzz a parser, and explain why pickle is RCE |
| 2. ML stack | ~400 | C1, C3–C5, D1–D6, E8–E15, H4–H6, I1–I4 | You can read a kernel, a PyTorch op and a model-loading path, and find where the trust ends |
| 3. Depth | ~500 | A3–A4, A6–A10, B2–B4, B9–B10, C2, C6–C7, G1–G12, H2–H3 | Senior-level depth: memory corruption, static analysis, numerics, adversarial ML |
| 4. Research and principal | ~550 | D7, F4–F8, J1–J9, K1–K4 | You can threat-model an org, judge severity, and write disclosure-quality reports |

---

## A. Systems and exploitation foundations

| ID | Resource | Hours | Why |
|---|---|---|---|
| A1 | [CS:APP, *Computer Systems: A Programmer's Perspective*](https://csapp.cs.cmu.edu/) | 60 | Memory layout, linking, the stack: the base for every native-code bug |
| A2 | [CMU 15-213 course site (labs + lectures)](https://www.cs.cmu.edu/~213/) | 30 | The labs (bomb, attack, malloc) make A1 concrete |
| A3 | [MIT 6.5660 Computer Systems Security (2026)](https://css.csail.mit.edu/6.5660/2026/) | 60 | Isolation, privilege separation, the classic papers |
| A4 | [Ross Anderson, *Security Engineering*, 3rd ed. (free chapters)](https://www.cl.cam.ac.uk/~rja14/book.html) | 50 | Principal-level breadth: economics, policy, systems |
| A5 | [pwn.college](https://pwn.college/) | 150 | The best structured hands-on exploitation path |
| A6 | [Nightmare (binary exploitation via CTF)](https://guyinatuxedo.github.io/) | 40 | Worked exploitation write-ups by bug class |
| A7 | [how2heap (shellphish)](https://github.com/shellphish/how2heap) | 20 | Heap exploitation techniques, with runnable code |
| A8 | [LiveOverflow (YouTube)](https://www.youtube.com/@LiveOverflow) | 25 | How researchers think, out loud |
| A9 | [MIT 6.172 Performance Engineering (OCW)](https://ocw.mit.edu/courses/6-172-performance-engineering-of-software-systems-fall-2018/) | 50 | Why kernels are written the way they are (and where speed hides bugs) |
| A10 | [Agner Fog's optimization manuals](https://www.agner.org/optimize/) | 25 | CPU microarchitecture; background for side channels |

## B. Fuzzing, sanitizers and program analysis

| ID | Resource | Hours | Why |
|---|---|---|---|
| B1 | [*The Fuzzing Book*](https://www.fuzzingbook.org/) | 60 | Interactive textbook covering grammar, coverage and search-based fuzzing |
| B2 | [*The Debugging Book*](https://www.debuggingbook.org/) | 40 | Delta debugging, slicing, root-causing: your T3→T4 step |
| B3 | [google/fuzzing (tutorials and docs)](https://github.com/google/fuzzing) | 15 | libFuzzer tutorial, structure-aware fuzzing |
| B4 | [OSS-Fuzz documentation](https://google.github.io/oss-fuzz/) | 10 | How mature targets are fuzzed continuously |
| B5 | [libFuzzer](https://llvm.org/docs/LibFuzzer.html) | 3 | Reference |
| B6 | [AFL++ docs](https://aflplus.plus/docs/) | 10 | The other major engine |
| B7 | [Atheris (Python fuzzing)](https://github.com/google/atheris) | 3 | Fuzz Python loaders and parsers, and native extensions under them |
| B8 | [Sanitizers wiki (ASan, MSan, UBSan, TSan)](https://github.com/google/sanitizers/wiki) | 5 | What each sanitizer catches and its overhead |
| B9 | [CodeQL documentation](https://codeql.github.com/docs/) | 25 | Variant analysis: find every sibling of one bug |
| B10 | [Semgrep docs](https://semgrep.dev/docs/) | 6 | Fast pattern rules for sinks (e.g. `torch.load` without `weights_only`) |

## C. GPUs, CUDA and kernels

| ID | Resource | Hours | Why |
|---|---|---|---|
| C1 | [CUDA C++ Programming Guide](https://docs.nvidia.com/cuda/cuda-c-programming-guide/) | 40 | The memory model, indexing, synchronization |
| C2 | [CUDA C++ Best Practices Guide](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/) | 15 | Where performance shortcuts come from |
| C3 | [Compute Sanitizer](https://docs.nvidia.com/compute-sanitizer/) | 5 | memcheck/racecheck/initcheck: how your bitsandbytes OOBs were proven |
| C4 | [Triton tutorials](https://triton-lang.org/main/getting-started/tutorials/index.html) | 15 | The kernel language behind Unsloth and Inductor |
| C5 | [GPU MODE lectures](https://github.com/gpu-mode/lectures) | 60 | Community lecture series on GPU programming, kernels and profiling |
| C6 | [Trail of Bits: LeftoverLocals](https://blog.trailofbits.com/2024/01/16/leftoverlocals-listening-to-llm-responses-through-leaked-gpu-local-memory/) | 2 | A cross-process GPU memory leak exposing LLM responses |
| C7 | [NVIDIA MIG user guide](https://docs.nvidia.com/datacenter/tesla/mig-user-guide/) | 4 | Hardware partitioning for multi-tenant isolation |

## D. ML framework internals

| ID | Resource | Hours | Why |
|---|---|---|---|
| D1 | [ezyang: PyTorch internals](http://blog.ezyang.com/2019/05/pytorch-internals/) | 3 | Tensors, dispatch, autograd: the map of PyTorch's code |
| D2 | [PyTorch developer wiki](https://github.com/pytorch/pytorch/wiki) | 20 | How the codebase and processes work |
| D3 | [torch.compiler docs (Dynamo, Inductor)](https://docs.pytorch.org/docs/stable/torch.compiler.html) | 15 | Where #201473 lived: compiled-code correctness |
| D4 | [PyTorch dev-discuss forum](https://dev-discuss.pytorch.org/) | 25 | Design notes straight from the core developers |
| D5 | [JAX documentation](https://docs.jax.dev/) | 20 | A second framework design (XLA, tracing) to compare |
| D6 | [CMU Deep Learning Systems (10-414/714)](https://dlsyscourse.org/) | 80 | Build a framework yourself: autograd, kernels, hardware |
| D7 | [Princeton COS 597G: Understanding LLMs](https://www.cs.princeton.edu/courses/archive/fall22/cos597G/) | 30 | A paper course on the models you're securing |

## E. Model serialization and supply chain

| ID | Resource | Hours | Why |
|---|---|---|---|
| E1 | [Python `pickle` docs (read the warning)](https://docs.python.org/3/library/pickle.html) | 1 | Where it all starts |
| E2 | [PyTorch serialization notes](https://docs.pytorch.org/docs/stable/notes/serialization.html) | 2 | `weights_only` and the allowlist mechanism |
| E3 | [Trail of Bits: "Never a dill moment" (exploiting ML pickles)](https://blog.trailofbits.com/2021/03/15/never-a-dill-moment-exploiting-machine-learning-pickle-files/) | 2 | The canonical write-up |
| E4 | [Fickling](https://github.com/trailofbits/fickling) | 5 | Pickle decompiler and scanner; read the code |
| E5 | [safetensors docs](https://huggingface.co/docs/safetensors/index) + [repo](https://github.com/huggingface/safetensors) | 5 | Format design: no code, but still a parser (header bounds) |
| E6 | [HF Hub security](https://huggingface.co/docs/hub/security) + [pickle scanning](https://huggingface.co/docs/hub/security-pickle) | 3 | How a model hub defends itself |
| E7 | [ProtectAI modelscan](https://github.com/protectai/modelscan) | 3 | A multi-format model scanner |
| E8 | [GGUF specification](https://github.com/ggml-org/ggml/blob/master/docs/gguf.md) | 3 | Read it as an attacker: every size and offset field |
| E9 | [ONNX concepts and format](https://onnx.ai/onnx/intro/) | 6 | Protobuf-based models and custom ops |
| E10 | [PyTorch: compromised nightly dependency (torchtriton)](https://pytorch.org/blog/compromised-nightly-dependency/) | 1 | A real dependency-confusion incident, from the source |
| E11 | [GitHub Security Lab: preventing pwn requests](https://securitylab.github.com/resources/github-actions-preventing-pwn-requests/) | 2 | CI attack surface (your act finding lives here) |
| E12 | [SLSA](https://slsa.dev/) | 10 | Build provenance levels |
| E13 | [Sigstore docs](https://docs.sigstore.dev/) | 6 | Signing artifacts, and soon models |
| E14 | [OpenSSF Scorecard](https://github.com/ossf/scorecard) | 3 | Measure a project's supply-chain hygiene |
| E15 | [PyTorch SECURITY.md](https://github.com/pytorch/pytorch/blob/main/SECURITY.md) | 1 | What PyTorch itself counts as a vulnerability (read every target's) |

## F. Threat modeling and AI-security frameworks

| ID | Resource | Hours | Why |
|---|---|---|---|
| F1 | [MITRE ATLAS](https://atlas.mitre.org/) | 15 | ATT&CK-style tactics and case studies for AI systems |
| F2 | [OWASP ML Security Top 10](https://owasp.org/www-project-machine-learning-security-top-10/) | 5 | A shared vocabulary |
| F3 | [OWASP Top 10 for LLM applications](https://genai.owasp.org/llm-top-10/) | 5 | The same, for LLM apps |
| F4 | [NIST AI 100-2 E2025: adversarial ML taxonomy](https://csrc.nist.gov/pubs/ai/100/2/e2025/final) | 15 | The authoritative taxonomy |
| F5 | [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework) | 10 | Principal-level governance language |
| F6 | [Google Secure AI Framework (SAIF)](https://saif.google/) | 4 | One large company's control framework |
| F7 | [Microsoft: threat modeling AI/ML systems](https://learn.microsoft.com/en-us/security/engineering/threat-modeling-aiml) | 3 | Practical threat-modeling questions |
| F8 | [Shostack: threat modeling resources](https://shostack.org/resources/threat-modeling) | 10 | The method itself, from its leading teacher |

## G. Adversarial ML and LLM security

| ID | Resource | Hours | Why |
|---|---|---|---|
| G1 | [Nicholas Carlini's papers](https://nicholas.carlini.com/) | 60 | The most rigorous body of attack research; read his evaluation methodology |
| G2 | [Adversarial Robustness: Theory and Practice (tutorial)](https://adversarial-ml-tutorial.org/) | 15 | Hands-on foundations |
| G3 | [Simon Willison: prompt-injection series](https://simonwillison.net/series/prompt-injection/) | 20 | The clearest running account of LLM-app security |
| G4 | [Greshake et al., indirect prompt injection (2302.12173)](https://arxiv.org/abs/2302.12173) | 4 | Agents and tool use as an attack surface |
| G5 | [Extracting training data from LLMs (2012.07805)](https://arxiv.org/abs/2012.07805) | 4 | Memorization and privacy |
| G6 | [Universal and transferable adversarial attacks, GCG (2307.15043)](https://arxiv.org/abs/2307.15043) | 4 | Optimization-based jailbreaks |
| G7 | [Stealing part of a production LM (2403.06634)](https://arxiv.org/abs/2403.06634) | 4 | Model extraction through an API |
| G8 | [Poisoning web-scale training datasets is practical (2302.10149)](https://arxiv.org/abs/2302.10149) | 4 | Supply chain of the data |
| G9 | [Sleeper Agents (2401.05566)](https://arxiv.org/abs/2401.05566) | 4 | Backdoors that survive safety training |
| G10 | [PLeak: prompt leaking attacks (2405.06823)](https://arxiv.org/abs/2405.06823) | 4 | System-prompt extraction |
| G11 | [SmoothLLM: defending against jailbreaks (2310.03684)](https://arxiv.org/abs/2310.03684) | 4 | A defense paper, to learn how defenses get evaluated |
| G12 | [awesome-llm-security (index)](https://github.com/corca-ai/awesome-llm-security) | 20 | Jumping-off index; pick papers from it after G1–G11 |

## H. Numerical correctness

| ID | Resource | Hours | Why |
|---|---|---|---|
| H1 | [Goldberg: *What Every Computer Scientist Should Know About Floating-Point*](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html) | 8 | Required |
| H2 | [Higham: *Accuracy and Stability of Numerical Algorithms* (SIAM)](https://epubs.siam.org/doi/book/10.1137/1.9780898718027) | 80 | The reference for rounding analysis (summation, Welford-style algorithms) |
| H3 | [William Kahan's papers and notes](https://people.eecs.berkeley.edu/~wkahan/) | 20 | From the architect of IEEE 754 |
| H4 | [PyTorch: numerical accuracy notes](https://docs.pytorch.org/docs/stable/notes/numerical_accuracy.html) | 2 | What PyTorch promises (and doesn't) |
| H5 | [Mixed Precision Training (1710.03740)](https://arxiv.org/abs/1710.03740) | 3 | Loss scaling and fp32 master weights |
| H6 | [FP8 Formats for Deep Learning (2209.05433)](https://arxiv.org/abs/2209.05433) | 3 | E4M3/E5M2: the formats your Unsloth FP8 tests used |

## I. Serving and distributed infrastructure

| ID | Resource | Hours | Why |
|---|---|---|---|
| I1 | [Ray security docs](https://docs.ray.io/en/latest/ray-security/index.html) | 3 | The vendor's threat model ("trusted network") |
| I2 | [Oligo: ShadowRay](https://www.oligo.security/blog/shadowray-attack-ai-workloads-actively-exploited-in-the-wild) | 2 | What happens when that assumption meets the internet |
| I3 | [Oligo: ShellTorch (TorchServe)](https://www.oligo.security/blog/shelltorch-explained-multiple-vulnerabilities-in-pytorch-model-server) | 2 | Model-server attack chain |
| I4 | [Kubernetes security concepts](https://kubernetes.io/docs/concepts/security/) | 15 | Where most training and serving clusters run |

## J. Vulnerability research and disclosure

| ID | Resource | Hours | Why |
|---|---|---|---|
| J1 | [Google Project Zero blog](https://googleprojectzero.blogspot.com/) | 60 | The gold standard for root-cause write-ups |
| J2 | [Trail of Bits blog](https://blog.trailofbits.com/) | 40 | Strong ML-security and tooling coverage |
| J3 | [google/security-research (advisories)](https://github.com/google/security-research) | 20 | Real advisories with proofs of concept |
| J4 | [huntr (AI/ML bug bounty)](https://huntr.com/) | 20 | Read disclosed ML-library reports for patterns |
| J5 | [GitHub advisories: PyTorch](https://github.com/advisories?query=pytorch) | 10 | Then repeat for transformers, vllm, onnx, … |
| J6 | [CVSS v4.0 specification](https://www.first.org/cvss/v4.0/specification-document) | 4 | Scoring severity defensibly |
| J7 | [CERT Guide to Coordinated Vulnerability Disclosure](https://certcc.github.io/CERT-Guide-to-CVD/) | 12 | The disclosure process, properly |
| J8 | [Google Bug Hunters](https://bughunters.google.com/) | 5 | VRP rules and what counts |
| J9 | [USENIX Security proceedings](https://www.usenix.org/conferences/byname/108) | 80 | Pick ML-systems papers each year; the field's frontier |

## K. Hands-on ranges

| ID | Resource | Hours | Why |
|---|---|---|---|
| K1 | [Lakera Gandalf](https://gandalf.lakera.ai/) | 5 | A quick prompt-injection warm-up |
| K2 | [Dreadnode Crucible](https://crucible.dreadnode.io/) | 40 | AI-security CTF challenges |
| K3 | [Microsoft PyRIT](https://github.com/Azure/PyRIT) | 10 | Red-teaming automation framework; read and run it |
| K4 | [NVIDIA garak](https://github.com/NVIDIA/garak) | 10 | LLM vulnerability scanner |

---

## Tracking template (copy per item)
```
ID:        Started:        Finished:        Hours actual:
3 takeaways:
1 thing to try on my own code (GPU lab, Unsloth harness, Dungeon Slayer, ...):
Links to my case studies (★ in the guide):
```
