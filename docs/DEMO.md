# Three-minute demo: fail, repair, verify, retain

Audience: engineers and technical hiring reviewers

Presenter: Cooper Reed, founder and lead engineer, Daily AI Agents

Target duration: 2:45–3:00

The scripted local renderer is `scripts/render-demo-video.py`; it loads displayed receipt values from the executable `scripts/demo-sequence.py --json` output. The exact generated-video narration is retained in [`DEMO-TRANSCRIPT.md`](DEMO-TRANSCRIPT.md). Voice, font, and codec output can vary across macOS, Pillow, and ffmpeg builds.

## Recording rules

- Record in a disposable directory containing only synthetic demonstration data.
- Keep the terminal font large and show the command, input, status, finding, and receipt path.
- Do not show credentials, private repositories, customer data, browser profiles, or unrelated desktop content.
- Say “local deterministic check,” not “the claim is true” or “the release is approved.”
- Record the final public package installation only after PyPI publication is independently verified. Until then, use a local editable install and label the footage `LOCAL RELEASE CANDIDATE`.

## Storyboard and narration

### 0:00–0:20 — The problem

**Screen:** Title card, then a tiny synthetic workspace with a report and a completion contract.

**Narration:**

> AI systems can say work is complete before the evidence is retained. I built the Daily AI Agent Toolkit to make that boundary explicit. It provides two local MCP servers and six portable Agent Skills. Here is one deterministic failure-and-repair loop.

### 0:20–0:55 — Artifact failure

**Screen:** Invoke `verify_artifact` against the synthetic report with one required term deliberately absent. Highlight `status: FAIL` and `required_term_missing`.

**Narration:**

> Evidence Gate checks a file beneath an operator-supplied root. This report exists, but it fails the declared rule because the required limitation is missing. The result is a bounded local receipt—not a semantic judgment.

### 0:55–1:20 — Repair and rerun

**Screen:** Add the missing limitation in an editor, save, and invoke the same tool with the same rule. Highlight `status: PASS`, byte count, and SHA-256.

**Narration:**

> I repair the artifact and rerun the identical check. It now passes and records the retained bytes. That proves this file met this rule at this time. It does not prove every statement in the report.

### 1:20–1:50 — Preserve uncertainty

**Screen:** Invoke `audit_claims` once with only a URL and once with a rooted local source. Highlight the URL case as `UNVERIFIED` and the local-source case as declared evidence present.

**Narration:**

> The server never fetches URLs, so URL-only evidence stays unverified. A local source can establish evidence availability, but not semantic entailment. The tool keeps those boundaries in its limitations instead of upgrading uncertainty.

### 1:50–2:20 — Make the blocker actionable

**Screen:** Run `evaluate_completion` with one requirement lacking evidence, then pass its findings to `format_blockers`. Highlight `NOT_RUN` or `BLOCKED`, the requirement ID, and the repair text.

**Narration:**

> Release Gate preserves non-passing states and converts them into explicit blocker records. Missing evidence does not become an optimistic pass, and the next required action remains visible.

### 2:20–2:45 — Retain a release receipt

**Screen:** Invoke `build_release_receipt` with the passing check and repaired artifact. Save and display the JSON receipt. Highlight status, relative artifact path, SHA-256, and limitation.

**Narration:**

> Finally, Release Gate hashes the artifact into a retained receipt. The receipt itself does not publish, deploy, or approve anything. It gives a reviewer a reproducible record for the next controlled decision.

### 2:45–3:00 — Close

**Screen:** Repository URL, package names, Apache-2.0, and a concise boundary card.

**Narration:**

> The toolkit is open source, local, and deterministic. It is designed to make evidence, blockers, and limitations easier to inspect before release.

## Capture checklist

- [ ] Synthetic inputs are committed or attached so viewers can reproduce the exact run.
- [ ] Every shown status matches the recorded receipt.
- [ ] The repaired artifact has a different SHA-256 from the failing artifact.
- [ ] Final receipt is retained as a release asset or repository example.
- [ ] Package and registry URLs shown on screen work without authentication.
- [ ] Captions, transcript, and 1080p export are readable.
- [ ] Runtime is no more than three minutes.
- [ ] No statement claims external, hosted, production, security, or semantic proof.

## Publication gate

Video recording may use the local release candidate. Publicly label package installation, registry discovery, CI, and repository availability only after those exact public surfaces pass their acceptance checks. Otherwise mark the affected shot `UNVERIFIED` or omit it.
