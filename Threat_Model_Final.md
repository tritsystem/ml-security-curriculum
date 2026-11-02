Threat Model: A Team Downloading Hugging Face Models and Training on a Shared GPU Cluster

How I ranked the risks. For each threat I scored likelihood (who can get at it, how hard it is to pull off) and impact (what an attacker gets, how far it spreads), each from 1 to 5, and multiplied them (max 25). Ties go to whatever is a way in, or hardest to detect. Assignment numbers are in brackets. Honestly, the pickle problem is the one that worries me. Everything else is a distant second.

1. Untrusted binary input [#6]. 5 × 5 = 25, Critical
Anyone can upload a model and anyone on the team can pull one down. Older model files use Python's pickle format, which runs whatever code is inside the moment you load it. The attacker then has that job's access: other teams' data on shared storage, cloud keys, and Hub tokens that can push models.
Defend: Safetensors only; anything else gets loaded with weights_only or converted in a sandbox with no network and no credentials. Pull models through an internal mirror with pinned versions, and give jobs short-lived, read-only tokens.
Detect: Scan every file before loading, with Fickling as the gate. Alert if a loading job starts programs, opens outside connections, or writes where it shouldn't.

2. Cluster software that assumes the network is safe [#4]. 4 × 5 = 20, Critical
Distributed training tools were built for speed on private networks. Traffic between machines often has no login or encryption, and on Ray the login exists but ships switched off. This is how one bad job spreads to the whole cluster, and how stolen credentials get used. An internet-facing control panel makes this a way in by itself.
Defend: Turn on built-in authentication; reach dashboards only through an SSH tunnel. Give each team its own network segment.
Detect: Alert on unexpected job submissions and logins, and on any traffic between teams' jobs or to the control plane.

3. Unchecked native code [#3]. 3 × 4 = 12, Medium (part of the #1 attack path)
The fast low-level code in ML frameworks and GPU kernels skips safety checks, and "safe" formats still have their sizes and shapes trusted by the loader. I found exactly this in bitsandbytes: a checkpoint with the wrong shape made a GPU kernel read past the end of its memory.
Defend: Patch frameworks, the GPU driver and the container toolkit on a schedule. Load outside models in a sandbox: not root, no host access.
Detect: Treat crashes during model loading as security events, and note which file was loading. Watch containers for attempts to reach the host.

4. Training data and model corruption [#1]. 3 × 4 = 12, Medium
For a team that trains, the model is the product. Poisoned base weights or datasets can plant a backdoor that passes normal testing, and every model trained on top inherits it. Pinning a version stops it changing, but it doesn't catch a model that was bad from the start.
Defend: Pin exact model and dataset versions from trusted sources, and record what every model was trained on. Before promotion, test against held-out data and trigger probes.
Detect: Compare each new model with the base and previous versions; investigate sudden changes on narrow inputs. Alert if an approved file's hash changes.

5. Weak GPU isolation [#2]. 2 × 3 = 6, Low
This needs the attacker on the same hardware with a loose sharing setup. The well-known GPU memory leak research didn't affect NVIDIA, and training jobs usually get whole GPUs.
Defend: Whole GPUs per job, or MIG on data-centre cards; no time-slicing or shared contexts across teams.
Detect: Audit GPU sharing and flag any GPU running more than one team's work.

6. Silent integrity failures [#5]. 2 × 2 = 4, Low for security, High for reliability
Mostly accidents, not attacks, but in training they're expensive and quiet. I reproduced a PyTorch bug where compiled code returned variances 50 to 100 percent wrong with no error, tracked down what triggered it, and tested a fix.
Defend: Pin framework versions, and check key calculations against a higher-precision reference before upgrading.
Detect: Alert on NaNs, loss spikes and odd gradients; run quick evaluations at each checkpoint; track GPU memory errors.

Audit toolkit. Model files: Fickling (gate; it caught a test file ModelScan missed), ModelScan, pickletools, safetensors header checks, gguf-dump. Native code: compute-sanitizer, ASan/UBSan, valgrind. Cluster: nmap and ss for open ports; capsh and amicontained for container privileges; mitmproxy to test Hub client and cache behaviour. Any specific vulnerability found gets its own CVSS 4.0 score.
