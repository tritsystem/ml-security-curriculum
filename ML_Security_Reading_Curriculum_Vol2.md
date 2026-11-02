# ML systems security curriculum, Volume II: depth and archives (~22,900 hours)

*Built 2026-10-30. Continues Volume I (`ML_Security_Reading_Curriculum_1000h.md`, ~1,740 h, parts A–K), so the
combined total is ~24,650 hours, about 14× Volume I. Every link was checked live on 2026-10-30. Links marked ⓑ
returned 403/406 to an automated check: they block bots but are the official pages (ACM DL, Intel, Black Hat, OpenAI,
OST2). **Hours are estimates.** For archives (proceedings, talk libraries, blogs) the content is effectively unbounded,
so the hours are a budget for **selective, deep reading** of the ML-, systems- and security-relevant part, not reading
everything.*

## Index

| Part | Topic | Items | Est. hours |
|---|---|---|---|
| [L](#l-conference-proceedings-the-research-frontier) | Conference proceedings | L1–L10 | 5,010 |
| [M](#m-talk-archives) | Talk archives | M1–M4 | 3,300 |
| [N](#n-journals-zines-and-long-form) | Journals, zines, long-form | N1–N6 | 1,250 |
| [O](#o-free-textbooks) | Free textbooks | O1–O19 | 1,800 |
| [P](#p-university-courses) | University courses | P1–P20 | 1,680 |
| [Q](#q-wargames-and-hands-on) | Wargames and hands-on | Q1–Q11 | 1,540 |
| [R](#r-kernels-compilers-hardware-and-ml-runtimes) | Kernels, compilers, hardware, ML runtimes | R1–R19 | 1,820 |
| [S](#s-vulnerability-data-and-catalogs) | Vulnerability data and catalogs | S1–S7 | 660 |
| [T](#t-research-blogs-ongoing) | Research blogs (ongoing) | T1–T28 | 2,165 |
| [U](#u-curated-paper-indexes) | Curated paper indexes | U1–U8 | 3,200 |
| [V](#v-secure-coding-standards-and-verification) | Secure coding, standards, verification | V1–V13 | 480 |
| | **Volume II total** | **168 links** | **~22,905** |
| | **Volumes I + II** | **262 links** | **~24,650** |

## How Volume II fits on top of Volume I

| Track | When | Draw from |
|---|---|---|
| **Foundations deepening** (years 1–2, alongside Vol I phases 1–3) | after Vol I part A | O1, O14, O19, P5, P18–P21, R4–R7, V1–V2 |
| **Vulnerability research craft** (years 2–4) | after Vol I parts A–B | Q1–Q11, R1–R3, R19, S1–S2, N1–N2, M1–M4, U2–U3 |
| **ML systems depth** (years 2–5) | after Vol I parts C–D | O4–O9, P7–P14, R8–R18, L6–L7, L9, U4 |
| **ML security research** (years 3–6) | after Vol I parts E–G | U1, U5–U8, L1–L5, L8, L10, T5–T7, T22–T28 |
| **Numerics specialty** (any time after Vol I part H) | | O15, P20, V10–V11, S7 |
| **Principal breadth** (ongoing) | | N3–N6, T1–T4, T15–T21, V3–V9 |

Rule of thumb for archives: read **one paper or talk properly** (notes, three takeaways, one thing to try on your own
code) rather than five skimmed.

---

## L. Conference proceedings (the research frontier)

| ID | Resource | Hours | Focus |
|---|---|---|---|
| L1 | USENIX Security programs: [2025](https://www.usenix.org/conference/usenixsecurity25/technical-sessions) · [2024](https://www.usenix.org/conference/usenixsecurity24/technical-sessions) · [2023](https://www.usenix.org/conference/usenixsecurity23/technical-sessions) · [2022](https://www.usenix.org/conference/usenixsecurity22/technical-sessions) · [2021](https://www.usenix.org/conference/usenixsecurity21/technical-sessions) · [2020](https://www.usenix.org/conference/usenixsecurity20/technical-sessions) | 1,080 | About 60 relevant papers a year: ML security, fuzzing, memory safety, side channels |
| L2 | [IEEE S&P (Oakland) index](https://www.ieee-security.org/TC/SP-Index.html) | 600 | The top venue; "SoK" papers are the best entry points |
| L3 | [ACM CCS](https://www.sigsac.org/ccs.html) + [ACM DL: CCS](https://dl.acm.org/conference/ccs) ⓑ | 600 | Systems and applied crypto, ML-privacy attacks |
| L4 | NDSS programs: [2025](https://www.ndss-symposium.org/ndss-program/symposium-2025/) · [2024](https://www.ndss-symposium.org/ndss-program/symposium-2024/) · [2023](https://www.ndss-symposium.org/ndss-program/symposium-2023/) | 450 | Network and distributed-systems security, fuzzing |
| L5 | USENIX WOOT (offensive tech): [2025](https://www.usenix.org/conference/woot25/technical-sessions) · [2024](https://www.usenix.org/conference/woot24/technical-sessions) | 80 | Practical attacks, short and dense |
| L6 | Systems: [OSDI '25](https://www.usenix.org/conference/osdi25/technical-sessions) · [OSDI '24](https://www.usenix.org/conference/osdi24/technical-sessions) · [OSDI '23](https://www.usenix.org/conference/osdi23/technical-sessions) · [NSDI '24](https://www.usenix.org/conference/nsdi24/technical-sessions) · [ATC '24](https://www.usenix.org/conference/atc24/technical-sessions) | 400 | How the ML infrastructure you attack is built |
| L7 | [MLSys proceedings](https://proceedings.mlsys.org/) | 400 | Compilers, serving, kernels, distributed training |
| L8 | [IEEE SaTML (Secure and Trustworthy ML)](https://satml.org/) | 150 | A venue for exactly this field |
| L9 | ACM DL: [SOSP](https://dl.acm.org/conference/sosp) ⓑ · [ASPLOS](https://dl.acm.org/conference/asplos) ⓑ · [PLDI](https://dl.acm.org/conference/pldi) ⓑ | 450 | OS, architecture/accelerators, compilers and verification |
| L10 | ML venues: [NeurIPS](https://neurips.cc/) · [ICML](https://icml.cc/) · [ICLR](https://iclr.cc/) · [OpenReview](https://openreview.net/) | 800 | Read only the robustness, privacy and security tracks; OpenReview shows the reviews too |

## M. Talk archives

| ID | Resource | Hours | Focus |
|---|---|---|---|
| M1 | [DEF CON (official YouTube)](https://www.youtube.com/@DEFCONConference) | 1,200 | Main stage plus the AI Village and other village talks |
| M2 | [Black Hat archives](https://www.blackhat.com/html/archives.html) ⓑ | 800 | Briefings with slides and white papers |
| M3 | [media.ccc.de (Chaos Communication Congress)](https://media.ccc.de/) | 1,200 | Deep hardware, firmware and side-channel talks |
| M4 | [OffensiveCon](https://www.offensivecon.org/) | 100 | Elite exploitation talks |

## N. Journals, zines and long-form

| ID | Resource | Hours | Focus |
|---|---|---|---|
| N1 | [Phrack](https://phrack.org/) | 300 | The classic exploitation journal, all issues |
| N2 | PoC‖GTFO: [mirror](https://www.alchemistowl.org/pocorgtfo/) · [GitHub archive](https://github.com/angea/pocorgtfo) | 150 | File formats, polyglots, deep tricks |
| N3 | [USENIX ;login: online](https://www.usenix.org/publications/loginonline) | 100 | Practitioner essays |
| N4 | [ACM Queue](https://queue.acm.org/) ⓑ | 150 | Systems practice from industry |
| N5 | [Communications of the ACM](https://cacm.acm.org/) ⓑ | 150 | Research highlights and surveys |
| N6 | [LWN.net](https://lwn.net/) | 400 | Linux kernel and security reporting; the best of its kind |

## O. Free textbooks

| ID | Resource | Hours | Focus |
|---|---|---|---|
| O1 | [OSTEP: *Operating Systems: Three Easy Pieces*](https://pages.cs.wisc.edu/~remzi/OSTEP/) | 50 | Processes, memory, concurrency, persistence |
| O2 | [*Static Program Analysis* (Møller & Schwartzbach)](https://cs.au.dk/~amoeller/spa/) | 60 | The theory behind CodeQL/semgrep-style tools |
| O3 | [*Software Foundations* (Coq)](https://softwarefoundations.cis.upenn.edu/) | 200 | Formal reasoning about programs |
| O4 | [*Deep Learning* (Goodfellow, Bengio, Courville)](https://www.deeplearningbook.org/) | 100 | The math under every model |
| O5 | [*Dive into Deep Learning*](https://d2l.ai/) | 150 | Runnable notebooks, PyTorch and JAX |
| O6 | [*Understanding Deep Learning* (Prince)](https://udlbook.github.io/udlbook/) | 80 | Modern and clear |
| O7 | [*Mathematics for Machine Learning*](https://mml-book.github.io/) | 80 | Linear algebra, calculus, probability |
| O8 | [*Probabilistic Machine Learning* (Murphy)](https://probml.github.io/pml-book/) | 200 | The reference text |
| O9 | [*The Elements of Statistical Learning*](https://hastie.su.domains/ElemStatLearn/) | 120 | Classical ML depth |
| O10 | [*Linux Device Drivers*, 3rd ed.](https://lwn.net/Kernel/LDD3/) | 60 | Kernel code that GPU drivers resemble |
| O11 | [Boneh & Shoup, *A Graduate Course in Applied Cryptography*](https://toc.cryptobook.us/) | 150 | Crypto you'll meet in signing and confidential computing |
| O12 | [*The Joy of Cryptography* (Rosulek)](https://joyofcryptography.com/) | 60 | A gentler crypto foundation |
| O13 | [*Reverse Engineering for Beginners* (Yurichev)](https://beginners.re/) | 120 | Reading compiled code |
| O14 | [Drepper: *What Every Programmer Should Know About Memory*](https://people.freebsd.org/~lstewart/articles/cpumemory.pdf) | 15 | Caches, NUMA: the base for side channels |
| O15 | [*Numerical Recipes*](http://numerical.recipes/book.html) | 150 | Practical numerical algorithms |
| O16 | [*The Rust Programming Language*](https://github.com/rust-lang/book) | 40 | The memory-safe alternative |
| O17 | [The Rustonomicon (unsafe Rust)](https://doc.rust-lang.org/nomicon/) | 15 | Where Rust's guarantees end |
| O18 | [Google's Comprehensive Rust](https://github.com/google/comprehensive-rust) | 30 | Course-style Rust |
| O19 | [Nand2Tetris](https://www.nand2tetris.org/) | 120 | Build a computer from gates up |

## P. University courses

| ID | Resource | Hours | Focus |
|---|---|---|---|
| P1 | [Stanford CS155 Computer Security](https://cs155.stanford.edu/) | 60 | Survey with labs |
| P2 | [Berkeley CS161 Computer Security](https://cs161.org/) | 60 | Memory safety, crypto, web |
| P3 | [Berkeley CS162 Operating Systems](https://cs162.org/) | 100 | OS internals with projects |
| P4 | [MIT 6.824/6.5840 Distributed Systems](https://pdos.csail.mit.edu/6.824/) | 120 | Raft and friends: what clusters rely on |
| P5 | [MIT 6.S081/6.1810 Operating System Engineering (xv6)](https://pdos.csail.mit.edu/6.S081/) | 120 | Write kernel code yourself |
| P6 | [CMU 15-418 Parallel Computer Architecture](https://www.cs.cmu.edu/~418/) | 100 | GPUs, SIMD, memory consistency |
| P7 | [Stanford CS229 Machine Learning](https://cs229.stanford.edu/) | 100 | ML foundations |
| P8 | [Stanford CS231n](https://cs231n.stanford.edu/) | 100 | Vision and backprop by hand |
| P9 | [Stanford CS224n](https://web.stanford.edu/class/cs224n/) | 100 | NLP and transformers |
| P10 | [Berkeley CS294/194 LLM Agents (F24)](https://rdi.berkeley.edu/llm-agents/f24) | 40 | Agent architectures: the next attack surface |
| P11 | [MIT 6.5940 TinyML and Efficient DL](https://hanlab.mit.edu/courses/2024-fall-65940) ([course hub](https://efficientml.ai/)) | 80 | Quantization, pruning: where numerics break |
| P12 | [Stanford CS336 Language Modeling from Scratch](https://stanford-cs336.github.io/spring2025/) | 120 | Build an LLM stack: tokenizer, kernels, training |
| P13 | [Karpathy: Neural Networks Zero to Hero](https://karpathy.ai/zero-to-hero.html) | 40 | Code-first intuition |
| P14 | [fast.ai Practical Deep Learning](https://course.fast.ai/) | 60 | Applied DL |
| P15 | [Northeastern CS5770 Software Vulnerabilities](https://course.ccs.neu.edu/cs5770/) | 60 | Vulnerability classes and exploitation |
| P16 | [MIT 6.858 Computer Systems Security (OCW 2014 lectures)](https://ocw.mit.edu/courses/6-858-computer-systems-security-fall-2014/) | 60 | Recorded lectures that pair with Vol I A3 |
| P17 | [MIT 6.006 Introduction to Algorithms](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/) | 80 | Complexity: algorithmic DoS and asymptotics |
| P18 | [MIT 18.06 Linear Algebra (Strang)](https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/) | 80 | The language of ML |
| P19 | [MIT 18.335J Numerical Methods](https://ocw.mit.edu/courses/18-335j-introduction-to-numerical-methods-spring-2019/) | 100 | Floating-point error analysis at graduate level |
| P20 | [MIT 6.004 Computation Structures](https://ocw.mit.edu/courses/6-004-computation-structures-spring-2017/) | 100 | Hardware from the ground up |

## Q. Wargames and hands-on

| ID | Resource | Hours | Focus |
|---|---|---|---|
| Q1 | [OpenSecurityTraining2](https://ost2.fyi/) ⓑ | 400 | Free deep courses: x86, debuggers, firmware, RE |
| Q2 | [Exploit Education](https://exploit.education/) | 100 | Phoenix, Nebula, Fusion VMs |
| Q3 | [ROP Emporium](https://ropemporium.com/) | 30 | Return-oriented programming |
| Q4 | [OverTheWire wargames](https://overthewire.org/wargames/) | 150 | From bandit to the advanced games |
| Q5 | [Microcorruption](https://microcorruption.com/) | 40 | Embedded exploitation |
| Q6 | [CryptoHack](https://cryptohack.org/) | 150 | Applied crypto attacks |
| Q7 | [Cryptopals](https://cryptopals.com/) | 80 | The classic crypto challenges |
| Q8 | [PortSwigger Web Security Academy](https://portswigger.net/web-security) | 150 | Web attacks; ML apps are web apps too |
| Q9 | [picoCTF](https://picoctf.org/) | 100 | Broad CTF practice |
| Q10 | [CTFtime (events and write-ups)](https://ctftime.org/) | 300 | Study write-ups of hard pwn challenges |
| Q11 | [Google kCTF](https://google.github.io/kctf/) | 40 | Kubernetes-based CTF infrastructure, and Google's kernel exploit VRP |

## R. Kernels, compilers, hardware and ML runtimes

| ID | Resource | Hours | Focus |
|---|---|---|---|
| R1 | [Linux kernel documentation](https://docs.kernel.org/) | 300 | Memory management, drivers, security modules |
| R2 | [xairy: Linux kernel exploitation index](https://github.com/xairy/linux-kernel-exploitation) | 150 | Curated kernel-exploitation write-ups |
| R3 | [syzkaller](https://github.com/google/syzkaller) | 40 | Kernel fuzzing; read the docs and found bugs |
| R4 | [Intel 64 and IA-32 SDM](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html) ⓑ | 400 | Reference: paging, privilege, virtualization |
| R5 | [x86 instruction reference (felixcloutier)](https://www.felixcloutier.com/x86/) | 50 | Quick instruction lookup |
| R6 | [Agner Fog: microarchitecture guide (PDF)](https://www.agner.org/optimize/microarchitecture.pdf) | 40 | Pipelines, predictors, caches |
| R7 | [Spectre/Meltdown papers](https://spectreattack.com/) | 20 | Transient execution |
| R8 | [Compiler Explorer](https://godbolt.org/) | 50 | Practice: read what your C++/CUDA compiles to |
| R9 | [LLVM documentation](https://llvm.org/docs/) | 150 | IR, passes, sanitizers' implementation |
| R10 | [MLIR](https://mlir.llvm.org/) | 80 | ML compilers' shared infrastructure |
| R11 | [OpenXLA / XLA](https://openxla.org/xla) | 40 | JAX/TF compiler |
| R12 | [Apache TVM docs](https://tvm.apache.org/docs/) | 60 | An open ML compiler |
| R13 | [PTX ISA](https://docs.nvidia.com/cuda/parallel-thread-execution/) | 60 | What Triton and CUDA actually emit |
| R14 | [Nsight Compute](https://docs.nvidia.com/nsight-compute/) | 20 | Kernel profiling |
| R15 | [CUTLASS](https://github.com/NVIDIA/cutlass) | 80 | Production GEMM kernels: read the index math |
| R16 | [AMD ROCm docs](https://rocm.docs.amd.com/) | 80 | The other GPU stack (HIP) |
| R17 | [vLLM docs](https://docs.vllm.ai/) | 40 | Production LLM serving: paged attention, prefix caching |
| R18 | [llama.cpp](https://github.com/ggml-org/llama.cpp) | 100 | Read the GGUF loader and quant kernels as an attacker |
| R19 | [Ghidra](https://ghidra-sre.org/) | 60 | Reverse-engineering closed-source extensions and drivers |

## S. Vulnerability data and catalogs

| ID | Resource | Hours | Focus |
|---|---|---|---|
| S1 | [Project Zero issue tracker](https://project-zero.issues.chromium.org/) | 200 | Raw bug reports with PoCs, the best training data for your eye |
| S2 | [Project Zero: 0days in the wild](https://googleprojectzero.github.io/0days-in-the-wild/) | 80 | Root-cause analyses of exploited bugs |
| S3 | [CVE.org](https://www.cve.org/) · [NVD](https://nvd.nist.gov/) · [OSV](https://osv.dev/) | 60 | Learn to search them; OSV covers PyPI packages |
| S4 | [CWE](https://cwe.mitre.org/) | 80 | Bug-class taxonomy (CWE-190, -787, -502…) |
| S5 | [MITRE ATT&CK](https://attack.mitre.org/) | 60 | Adversary behaviour; pairs with ATLAS (Vol I F1) |
| S6 | [CISA Known Exploited Vulnerabilities](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) | 30 | What attackers actually use |
| S7 | [PyTorch: "module: correctness (silent)" issues](https://github.com/pytorch/pytorch/issues?q=label%3A%22module%3A+correctness+%28silent%29%22) | 150 | Your numerics specialty as a live dataset; read root causes, not just reports |

## T. Research blogs (ongoing)

| ID | Resource | Hours | ID | Resource | Hours |
|---|---|---|---|---|---|
| T1 | [Google Security Blog](https://security.googleblog.com/) | 100 | T15 | [Cloudflare blog](https://blog.cloudflare.com/) | 150 |
| T2 | [MSRC blog](https://msrc.microsoft.com/blog/) | 80 | T16 | [Julia Evans](https://jvns.ca/) | 40 |
| T3 | [GitHub Security Lab research](https://securitylab.github.com/research/) | 80 | T17 | [Dan Luu](https://danluu.com/) | 60 |
| T4 | [NCC Group research](https://www.nccgroup.com/research-blog/) | 100 | T18 | [Brendan Gregg (performance)](https://www.brendangregg.com/) | 80 |
| T5 | [Embrace The Red (LLM app attacks)](https://embracethered.com/blog/) | 60 | T19 | [Schneier on Security](https://www.schneier.com/) | 100 |
| T6 | [Wiz research blog](https://www.wiz.io/blog) | 60 | T20 | [Krebs on Security](https://krebsonsecurity.com/) | 80 |
| T7 | [HiddenLayer research](https://hiddenlayer.com/research/) | 40 | T21 | [D. J. Bernstein's papers](https://cr.yp.to/papers.html) | 100 |
| T8 | [Lilian Weng](https://lilianweng.github.io/) | 60 | T22 | [Distill](https://distill.pub/) | 40 |
| T9 | [Chip Huyen](https://huyenchip.com/blog/) | 30 | T23 | [Transformer Circuits](https://transformer-circuits.pub/) | 80 |
| T10 | [Horace He: "Making DL go brrr"](https://horace.io/brrr_intro.html) | 5 | T24 | [Anthropic research](https://www.anthropic.com/research) | 80 |
| T11 | [Tim Dettmers](https://timdettmers.com/) | 20 | T25 | [Google DeepMind publications](https://deepmind.google/research/publications/) | 150 |
| T12 | [Sebastian Raschka](https://magazine.sebastianraschka.com/) | 80 | T26 | [OpenAI research](https://openai.com/research/) ⓑ | 80 |
| T13 | [PyTorch blog](https://pytorch.org/blog/) | 60 | T27 | [Alignment Forum](https://www.alignmentforum.org/) | 100 |
| T14 | [NVIDIA developer blog](https://developer.nvidia.com/blog/) | 150 | T28 | [LessWrong (AI posts)](https://www.lesswrong.com/) | 100 |

## U. Curated paper indexes

| ID | Resource | Hours | Focus |
|---|---|---|---|
| U1 | [Carlini: "A complete list of all (arXiv) adversarial example papers"](https://nicholas.carlini.com/writing/2019/all-adversarial-example-papers.html) | 1,500 | The full literature, kept updated; read the most-cited first |
| U2 | [FuzzingPaper (wcventure)](https://github.com/wcventure/FuzzingPaper) | 300 | Fuzzing research by venue and year |
| U3 | [Awesome-Fuzzing](https://github.com/secfigo/Awesome-Fuzzing) | 100 | Books, courses and tools |
| U4 | [Awesome System for Machine Learning](https://github.com/HuaizhengZhang/Awesome-System-for-Machine-Learning) | 300 | ML-systems papers by topic |
| U5 | [awesome-MLSecOps](https://github.com/RiccardoBiosas/awesome-MLSecOps) | 100 | ML security operations tooling and papers |
| U6 | [awesome-adversarial-machine-learning](https://github.com/yenchenlin/awesome-adversarial-machine-learning) | 100 | The early adversarial-ML canon |
| U7 | [arXiv cs.CR (cryptography and security)](https://arxiv.org/list/cs.CR/recent) | 500 | Weekly scan; read 2–3 papers a week in depth |
| U8 | [arXiv cs.LG (machine learning)](https://arxiv.org/list/cs.LG/recent) | 300 | Filter for robustness, privacy and systems |

Tool for all of this: [Semantic Scholar](https://www.semanticscholar.org/) for citation graphs (budgeted inside the items).

## V. Secure coding, standards and verification

| ID | Resource | Hours | Focus |
|---|---|---|---|
| V1 | [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines) | 60 | The rules C++ kernels break |
| V2 | [SEI CERT C Coding Standard](https://wiki.sei.cmu.edu/confluence/display/c/SEI+CERT+C+Coding+Standard) | 80 | Integer, memory and API rules with examples |
| V3 | [OWASP Top 10 (web)](https://owasp.org/www-project-top-ten/) | 10 | Baseline for serving endpoints |
| V4 | [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/) | 60 | Concrete defensive patterns (deserialization, SSRF…) |
| V5 | [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework) | 20 | Principal-level program language |
| V6 | [NIST SSDF (secure software development)](https://csrc.nist.gov/projects/ssdf) | 15 | Secure development practices, as a standard |
| V7 | [OpenSSF guides](https://openssf.org/resources/guides/) | 30 | Practical OSS security guidance |
| V8 | [OpenSSF: Securing Software Repositories WG](https://github.com/ossf/wg-securing-software-repos) | 10 | PyPI, npm and model-registry policy |
| V9 | [CISA Secure by Design](https://www.cisa.gov/securebydesign) | 15 | The secure-defaults argument (cf. `weights_only`) |
| V10 | [Herbie (floating-point accuracy repair)](https://herbie.uwplse.org/) | 20 | Automatically rewrites formulas like sigmoid′ for accuracy |
| V11 | [FPBench](https://fpbench.org/) | 20 | Floating-point benchmarks and tools community |
| V12 | [Dafny](https://dafny.org/) | 60 | Verified programming you can actually use |
| V13 | [seL4](https://sel4.systems/) | 80 | A formally verified kernel: what "proved secure" means |
