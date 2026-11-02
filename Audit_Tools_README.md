# ML audit tool stack: where it lives and how to use it

Installed 2026-10-30 in WSL Ubuntu (now on G:), in `~/mlsec-tools/`. All from official sources (PyPI, Ubuntu archive, GitHub
release with checksum verified). Start every session with:

    source ~/mlsec-tools/activate.sh

| Tool | Version | Status | Use it for |
|---|---|---|---|
| Fickling | 0.1.12 | ✅ verified | **Gate for pickle files.** `fickling --check-safety f.pkl` prints nothing: **exit 1 = unsafe, 0 = safe**. Python: `fickling.is_likely_safe(path)` |
| ModelScan | 0.8.8 | ✅ verified | Second opinion across formats: `modelscan -p <file or dir>` |
| pickletools | built in | ✅ | See the raw opcodes: `python -m pickletools f.pkl` (look for GLOBAL/STACK_GLOBAL + REDUCE) |
| safetensors | 0.8.0 | ✅ verified | Parse the header without loading tensors: first 8 bytes = header length, then JSON with dtype/shape/offsets; check offsets against the file size |
| gguf / `gguf-dump` | 0.19.0 | ✅ | Dump GGUF metadata and tensor offsets before any loader touches the file |
| mitmproxy / mitmdump | 12.3.1 | ✅ installed | Intercept or mock Hugging Face Hub traffic to test client and cache behaviour (your own machine only) |
| ASan / UBSan | gcc / clang | ✅ verified | Build C/C++ extensions with `-fsanitize=address,undefined -g` (caught a planted heap overflow) |
| compute-sanitizer | 2026.3 (CUDA 13.4) | ✅ on **Windows** | `"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\bin\compute-sanitizer.bat" --tool memcheck python script.py`. Set `PYTORCH_NO_CUDA_MEMORY_CACHING=1` so the caching allocator doesn't hide out-of-bounds accesses |
| nmap | 7.98 | ✅ verified | Port audit of cluster nodes. Without root, add **`-Pn`** (skip ping) and use `-sT` |
| ss / capsh | system | ✅ | Listening sockets (`ss -tlnp`) / container capabilities (`capsh --print`) |
| amicontained | 0.4.9 (2019) | ⚠️ partial | Container runtime, namespaces, capabilities. **The blocked-syscall probe hangs under WSL2**; stop it (Ctrl-C) after the capabilities output. Unmaintained since 2019 |
| valgrind | 3.26.0 | ❌ needs one command | Needs the system debug symbols. Run once in Ubuntu with your password: `sudo apt install valgrind libc6-dbg`. ASan covers most of the same memory bugs meanwhile |

## Measured scanner behaviour (read before trusting a "clean" result)
Three test pickles, built and never loaded:

| File | ModelScan | Fickling |
|---|---|---|
| Calls `os.system` on load | flagged (critical) | flagged |
| Calls `print` on load (harmless function, same mechanism) | **missed** | flagged |
| Plain weights, no code | clean | clean |

ModelScan matches a list of known-bad functions, so anything not on the list passes. Fickling distrusts any import it
doesn't recognise. **Gate with Fickling, use ModelScan as a second opinion, and never treat "No issues found" as proof
that a file is safe.** The only real guarantee is not loading pickle at all (safetensors, or `weights_only=True`).
