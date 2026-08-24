# Preregistration — R1 §3.3 retry: raise `max_tokens` on the warrant judge

**Written before execution.** The decision rule in §3 is fixed as of this document's commit. No
arm has been run under this document.

Amends: `docs/superpowers/specs/2026-08-20-warrant-citation-scorer-prereg.md` (the "R1" spec).
This document is scoped **only** to re-clearing that spec's §3.3 degeneracy gate. §§4–9 of the R1
spec (cohort endpoints, decision rule, confirmation requirements, not-permitted list) are
unchanged and apply as written once §3.3 clears under this document.

---

## 0. Why a new preregistration, not a re-run

The R1 spec's own §8 forbids re-running with a changed warrant prompt/config and reporting it as
the same arm: *"If the first prompt fails the degeneracy probe (§3.3), the arm is abandoned — a
second prompt is a new preregistration."* Status entry 2026-08-23 recorded R1 **ABANDONED** on
that basis: 16/42 (38.1%) parseable replies against the 80% floor.

That entry also diagnosed the failure mechanically, not as a hypothesis rejection: reproduced on 2
full replies, both failures are `json.JSONDecodeError: Unterminated string` on the **last** object
of a 10-source reply, mid-`"reason"`-string. `WarrantJudge.max_tokens` defaults to **512**; 24 of
26 §3.3 failures had the full `top_k=10` context window, and failing reply lengths (1748–2629
chars) straddle several successful *shorter*-context replies — consistent with a fixed output
budget being too small for a 10-object JSON array with a free-text field per object, not with the
model failing to reason about warrant. Every inspected reply, truncated or not, was well-formed up
to the cutoff and on-rubric (relation/modality/scope/temporal/numeric).

**Claim under test here:** the §3.3 failure is fully explained by output-token starvation, and
raising `max_tokens` clears the floor without any other change.

---

## 1. Method — single variable

**Only `max_tokens` changes, from 512 to 1024.** Nothing else: same judge model
(`mlx-community/Qwen2.5-7B-Instruct-4bit`), same `_warrant_prompt` text (including the `"reason"`
field — shortening or dropping it is a **second** lever and stays out of this arm so a pass can be
attributed to token budget alone, not conflated with a smaller prompt), same frozen 50-row
`eval/probes/screen_v1.jsonl`, same production 1.5B answers.

**1024 is a sizing estimate, not a fit to the failures.** Failing replies topped out at 2629 chars
under a 512-token budget (~5.1 chars/token observed). A full 10-object reply needs roughly
10 × (bracket/key overhead ~40 chars + a warrant number + a reason of the length already observed,
~150–250 chars) ≈ 2,000–2,900 chars ≈ 400–570 tokens at the same rate — so 512 sits right at the
edge, which matches 38.1% passing versus 61.9% truncating. 1024 gives roughly 2× headroom over the
observed worst case, chosen before this arm runs, not selected after seeing which value clears 80%.

**Reused, not regenerated:** the 1.5B answer pass (`reports/warrant-degeneracy-answers.json`,
42 answered / 8 abstained) is unaffected by a judge-side change and is read as-is — regenerating it
would burn ~4 minutes of compute to reproduce byte-identical inputs.

**Implementation:** `scripts/analysis/warrant_degeneracy_probe.py --phase judge` gains a
`--max-tokens` flag (default kept at 512 so the script's default behavior is unchanged unless
asked); this arm invokes it with `--max-tokens 1024`. No change to `WarrantJudge`'s class default,
`_warrant_prompt`, or any production file (`generate.py`, `settings.py`, `config.toml`) — this is a
probe-only parameter, matching the R1 spec's own posture that nothing arms in production before
adoption (§9 there).

---

## 2. Endpoint

Identical to the original §3.3: **parseable-reply rate** on the 42 judged rows (answered, contexts
present), measured directly against raw-reply JSON-decodability (not `parse_warrant_scores`, which
collapses a decode failure to the same `[0.0]*n` as a legitimate all-zero judgment).

---

## 3. Decision rule — fixed in advance

- **Parseable rate ≥ 80%** (34 of 42) → **PROCEED** to R1 §4/§6 (the cohort run), per the original
  spec's unchanged terms.
- **< 80%** → **ABANDON**, recorded as this document's result. Per the same discipline this
  document itself invokes: a further parameter change (e.g. 1024 → 2048, or dropping `reason`)
  requires **another new preregistration**, not a retry under this one. Two failed configurations
  is also the point to stop and ask whether the 7B model can hold a 10-object structured-output
  task at all, rather than continuing to raise the budget.

No effect-size floor applies here — this is a mechanism-firing gate (§3.3 of the original spec),
not a metric arm; §6's effect-size floor belongs to the cohort run this gate unlocks.

---

## 4. Not permitted after seeing the result

- Reporting a parseable rate between arms of *this* document (e.g. trying 1024 then 768 and
  keeping whichever clears 80%) — one value, preregistered above, one result.
- Changing `_warrant_prompt` in the same run as the `max_tokens` change and attributing a pass to
  either alone.
- Treating a pass here as cohort or gate evidence — §4/§6/§7 of the R1 spec still gate adoption in
  full; this document only reopens the door to running them.
