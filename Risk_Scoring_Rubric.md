Risk Scoring Rubric

Each threat gets four factor scores from 1 to 5. Two make up likelihood, two make up impact. Risk = Likelihood × Impact,
out of 25. The method follows the standard likelihood × impact approach (NIST SP 800-30, OWASP Risk Rating
Methodology), with factors defined for an ML training cluster.

Likelihood factors

Exposure: who can reach the weakness
5: Anyone on the internet (e.g. anyone can publish a model to the Hub)
4: Anyone with an account on the platform or any job on the cluster
3: An attacker who already has a foothold inside the cluster network
2: An attacker who must be co-located on the same hardware or node
1: Only an insider with administrator access

Ease: how hard it is to pull off
5: No skill needed; known technique, public tools, works by default
4: Known technique, needs light adaptation to this environment
3: Needs specific conditions or configuration to line up
2: Needs specialist skill or a non-default setup
1: Needs a new, unknown vulnerability (a "zero-day")

Impact factors

Attacker gain: what a successful attack gives the attacker
5: Running code on the system (code execution, host control)
4: Control over a valuable asset: stolen credentials, or attacker-controlled model behaviour (e.g. a backdoor)
3: A limited data leak, or disruption of service
2: A quietly worse model, or wasted compute, with no attacker control
1: Negligible

Blast radius: how far the damage spreads
5: Beyond the cluster: cloud accounts, published models, customers
4: The whole cluster or every team
3: One team, or one node and the jobs on it
2: One job or one training run
1: Nothing beyond the failed action

Combining the scores
- Likelihood = average of Exposure and Ease, rounded down.
- Impact = average of Attacker gain and Blast radius, rounded down.
- Risk score = Likelihood × Impact.
Rounding down stops one extreme factor from inflating a score by itself. Extreme single factors are handled by the
override rules below instead.

Categories
Critical: 20 to 25. Fix before the next training run uses outside models.
High: 15 to 19. Fix within the current planning cycle.
Medium: 9 to 14. Fix on the normal schedule; detection required meanwhile.
Low: 1 to 8. Accept and monitor, or fix when convenient.

Override and ordering rules
1. Floor rule: any threat with Attacker gain 5 and Exposure 4 or 5 is at least High, whatever its score.
2. Exposure change: if a control panel or service is reachable from the internet, its Exposure becomes 5. Rescore.
3. Tie-break: when scores are equal, a threat that gives an attacker a way in ranks above one that only spreads an
   existing compromise. If still tied, the harder-to-detect threat ranks higher.
4. Reliability flag: threats that are mostly accidental (Exposure and Ease both 2 or lower) get a separate
   reliability rating (Low / Medium / High), based on how often they happen and what they cost.
5. Individual vulnerabilities found under any threat are scored separately with CVSS 4.0. This rubric ranks threat
   categories, not single bugs.

Worked scores for the six threats

Untrusted binary input [#6]
Exposure 5, Ease 5 → Likelihood 5. Gain 5, Radius 5 → Impact 5. Score 25: Critical.
(Anyone can publish a model; pickle runs code on load; stolen tokens reach beyond the cluster.)

Cluster software that assumes the network is safe [#4]
Exposure 3, Ease 5 → Likelihood 4. Gain 5, Radius 5 → Impact 5. Score 20: Critical.
(Needs a foothold first, but logins ship switched off; control of the cluster leads to stolen credentials. If a
dashboard faces the internet, Exposure 5 → 25.)

Unchecked native code [#3]
Exposure 5, Ease 1 → Likelihood 3. Gain 4, Radius 4 → Impact 4. Score 12: Medium. Ranked above data corruption by
the tie-break (it is part of the way in).
(Malicious files are easy to deliver, but exploitation needs a real kernel or loader bug; out-of-bounds reads leak
memory, including tokens.)

Training data and model corruption [#1]
Exposure 5, Ease 2 → Likelihood 3. Gain 4, Radius 5 → Impact 4. Score 12: Medium.
(Anyone can publish data or weights; a backdoor that survives fine-tuning takes skill; a backdoored model reaches
customers.)

Weak GPU isolation [#2]
Exposure 2, Ease 2 → Likelihood 2. Gain 3, Radius 3 → Impact 3. Score 6: Low.
(Needs co-location and a loose GPU-sharing setup; leaks one co-tenant's data.)

Silent integrity failures [#5]
Exposure 2, Ease 2 → Likelihood 2. Gain 2, Radius 3 → Impact 2. Score 4: Low for security. Reliability flag:
High. (Rarely attacker-driven, but frequent and costly: a corrupted training run.)
