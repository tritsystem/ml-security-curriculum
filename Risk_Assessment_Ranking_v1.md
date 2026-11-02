Threat model: a team downloading Hugging Face models and training on a shared GPU cluster

How I ranked the risks

For each risk I asked how likely it is (who can get at it, how hard it is to pull off) and how bad it would be (what an attacker gets, how far it spreads). I scored both roughly from one to five and multiplied them. Anything hard to detect moved up, and ways in rank above things that only make an existing break-in worse. Honestly, the pickle problem is the one that worries me. Everything else is a distant second.

1. Untrusted binary input: Critical (about 22 out of 25)

Anyone can upload a model, and anyone on the team can pull one down. Older model files use Python's pickle format, which runs whatever code is inside the moment you load it. No skill needed. The attacker then has that training job's access: other teams' data on shared storage, cloud keys, Hub tokens that can push models. The safe formats don't fully close this either. They don't run code, but the loader still trusts the sizes and shapes in the file. I found exactly this in bitsandbytes: a checkpoint with the wrong shape made a GPU kernel read past the end of its memory. Biggest single fix: no pickle files, or force safe loading.

2. Cluster software that assumes the network is safe: High (about 20)

Distributed training tools were built for speed on private networks. Traffic between machines often has no login or encryption, and on one popular scheduler the login exists but ships switched off. This is how a single bad training job spreads to the whole cluster. If any control panel is reachable from the internet, it becomes a way in by itself and goes to Critical.

3. Unchecked native code: High, part of risk 1

The fast low-level code in ML frameworks and GPU kernels skips safety checks. On its own it usually ends in a crash or a leak, but delivered through a malicious model file it's a real way in, so I group it with risk 1.

4. Training data and model corruption: Medium to High (about 12)

For a team that trains, this matters more than it would for a serving setup, because the trained model is the product. Poisoned base weights or datasets can plant a backdoor that passes normal testing and only misbehaves on certain triggers, and every model trained on top inherits it. Pinning the exact model version stops it changing under you, but it doesn't catch a model that was bad from the start.

5. Weak GPU isolation: Medium (about 5)

Leaking another team's data through a shared GPU needs the attacker on the same hardware and a loose sharing setup. The well-known GPU memory leak research didn't affect NVIDIA, and training jobs usually get whole GPUs, so this sits low for this setup.

6. Silent integrity failures: Medium for security, High for reliability

Mostly accidents, not attacks, but in training they're expensive and quiet. I reproduced a PyTorch bug where compiled code returned variances 50 to 100 percent wrong with no error at all, tracked down the change that triggered it, and tested a fix. A run like that just produces a worse model. The fix: pin versions, check key results against a higher-precision reference, and watch training curves for anything odd.

Any specific vulnerability found under one of these gets its own CVSS 4.0 score.
