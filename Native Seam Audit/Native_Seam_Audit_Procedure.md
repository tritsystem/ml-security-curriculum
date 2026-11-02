# Native Runtime Seam Audit — Procedure, Tool Validation, and Target Ranking

*Written 2026-11-01. Rules V-1..V-6 in Mastermind Protocols.md. Everything here was run on this PC unless labelled Estimated.*

## 1. The idea in one paragraph

A **seam** is any boundary where one component hands data to another and each side assumes the other validated it:
Python to C, host to GPU kernel launch, thread to thread, library to library, and the small size arithmetic
(`count * itemsize`) that connects a number to an allocation. Hidden memory bugs live at seams because the
invariant is assumed on both sides and enforced on neither. We look for them with tools that emit a
**mechanistic signal** (a sanitizer report naming the exact byte, operation, or pair of racing accesses), so the
evidence is something a tool shows, not an argument.

## 2. Order of work (each step can stop the hunt cheaply)

1. **Validate the instruments** (V-1). Planted-bug positive control must fire; correct-code negative control must
   stay silent. A tool failing either is unavailable.
2. **Scope** (V-3). Read the target's SECURITY.md. If it disclaims the bug class, it is at most a regular bug.
3. **Dedup** (V-4). Issues, PRs, advisories, with the repo's real (post-rename) name. Errors are not empty results.
4. **Rank** (V-5). Likelihood x criticality, 1-5 each, basis written down.
5. **Hunt** the top seam with the matching tool (V-2 blind spots in mind).
6. **Climb the tiers**: T1 reading, T2 harness, T3 real entry point, T4 fix red-to-green with valid inputs proven
   still working. Never round up.
7. **Route** per the repo's channel, with the user's yes on exact text (C-1).

## 3. Tool validation results (run 2026-11-01)

Files: `Documents/seam-audit/toolcheck/` (`run_toolcheck.sh`, `cuda_controls.cu`, outputs `o_*`).

| Tool | Catches | Positive | Negative | Verdict |
|---|---|---|---|---|
| ASan | heap/stack out-of-bounds | fired | silent | PASS |
| MSan | uninitialized reads | fired | silent | PASS |
| UBSan + integer | signed overflow, size-math wrap | fired | silent | PASS |
| TSan | CPU data races | fired | silent | PASS |
| libFuzzer + ASan | input-driven seam bugs | fired (~2.1k execs) | n/a | PASS |
| compute-sanitizer memcheck | GPU out-of-bounds | fired | silent | PASS |
| compute-sanitizer initcheck | GPU uninitialized reads | fired | silent | PASS |
| compute-sanitizer racecheck | shared-memory hazards | fired | silent | PASS |
| compute-sanitizer synccheck | barrier misuse | fired (`__syncwarp` mask) | silent | PASS with blind spot |
| valgrind memcheck/helgrind | memory / races | — | — | NOT INSTALLED |

**Measured blind spots**
- synccheck on RTX 5060 (sm_120) did **not** flag a divergent `__syncthreads`; it did flag an invalid
  `__syncwarp` mask. Per-thread barriers since Volta make the first case undefined but undetected.
- ASan does not see in-buffer uninitialized reads (a small C network library's bug needed MSan) or use-after-free inside pool allocators.
- The first tool inventory said valgrind was present; it was not. Only the planted bug exposed that.

To install valgrind: in Ubuntu, `sudo apt install valgrind libc6-dbg`, then re-run `run_toolcheck.sh`.

## 4. Target ranking (likelihood x criticality, Estimated)

Likelihood = chance of an unreported, in-scope bug for reasonable effort. Evidence used: OSS-Fuzz coverage
(checked), hand-written size math, crowding (others' recent fix PRs, checked). Criticality = input trust,
primitive, reach, and whether the project's policy counts it.

| Seam / target class | L | Basis | C | Basis | LxC |
|---|---|---|---|---|---|
| Small C network libs/daemons without disclaiming policy | 3 | unfuzzed, hand-written parsers; 1 real T4 found, 2 clean | 3 | LAN-reachable data, mostly reads | 9 |
| Size arithmetic on large legitimate tensors (int32 index / nbytes wrap) | 3 | recurring class; UBSan + memcheck give decidable signals | 3 | trusted usage, silent corruption ranks high (O-11); regular bug not security | 9 |
| Media-decode wrappers (torchvision, TorchCodec, DALI) | 2 | unfuzzed glue, but **crowded**: active fix PRs by others in Aug-Oct 2026 | 4 | untrusted web data on default paths | 8 |
| Thread / stream races (intra-op pools, CUDA streams) | 2 | real but hard to trigger and to attribute | 3 | corrupts trusted workloads | 6 |
| ML model-file parsers (LightGBM, XGBoost, PyTorch) | 4 | technically easy | 1 | disclaimed by policy or already filed; maintainers overloaded | 4 |
| Continuously fuzzed data libs (numpy, arrow, pillow, opencv, codecs) | 1 | OSS-Fuzz harvests the shallow bugs | 4 | untrusted data | 4 |
| Rust parsers (safetensors, tokenizers) | 1 | memory-safe language | 3 | untrusted data | 3 |

**Reading the table:** the two top rows tie. The C-network row has a proven yield on this PC; the size-math row
reuses the bitsandbytes #2105 win and survives every policy exclusion because it fires on legitimate inputs.
The decode-wrapper row is the most critical but is being worked by others right now, so it ranks below.

## 5. What not to do (learned the hard way)

- Don't trust an inventory without a planted bug.
- Don't read code deeply before dedup on a popular target.
- Don't file a class the project's policy disclaims as security, and don't add to a flood maintainers have
  publicly asked relief from.
- Don't call a clean run a negative for a bug class the tool cannot see.

- Don't count carriage returns with `grep -c $'\r'` in Git Bash: it returned 0 on a CRLF control and the line count on
  LF files (measured 2026-11-01). Count raw bytes with Python (`sys.stdin.buffer.read().count(b'\r')`), checked on a control.
- When testing a fix by loading `main`'s Python file over an older installed package with compiled ops, a failure can
  come from the version mismatch (main calls an op the old build lacks), not the fix. Re-apply the same patch to the
  INSTALLED source and re-run before calling it a regression (torchvision box_iou_rotated, 2026-11-01).
