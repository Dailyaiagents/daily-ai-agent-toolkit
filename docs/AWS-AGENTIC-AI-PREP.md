# AWS Agentic AI Demonstrated: legitimate preparation brief

Prepared for Cooper Reed

Updated: 2026-08-27

## What AWS publicly confirms

AWS describes its microcredentials as hands-on assessments in a provisioned AWS environment, based on simulated business scenarios rather than multiple-choice questions. AWS says **AWS Agentic AI Demonstrated** validates the ability to troubleshoot, repair, integrate, and enhance AI agents built using Amazon Bedrock. AWS also states that microcredentials are free and do not require a Skill Builder subscription. See the official [AWS announcement](https://aws.amazon.com/blogs/training-and-certification/microcredentials-from-aws-are-now-free-heres-why-that-matters/) and [AWS digital training page](https://aws.amazon.com/training/digital/).

The assessment's exact tasks, scoring rubric, duration, and environment configuration are not established by the public sources cited here and remain `UNVERIFIED`. Do not infer them from this brief.

## Integrity boundary

This document is preparation, not an answer key. Cooper must complete the assessment personally. During a live assessment:

- follow the rules and permitted-resource policy shown by AWS;
- do not share, request, record, or reconstruct assessment tasks or solutions;
- do not let an agent operate the assessment interface or decide changes on Cooper's behalf; and
- use assistance only for ordinary account or browser troubleshooting when the assessment rules permit it.

## High-value preparation map

### 1. Trace before changing

Practice reading the execution path from user input through orchestration, action-group selection, parameters, knowledge-base lookup, and final response. AWS documents that Bedrock agent traces expose orchestration steps, action-group inputs and outputs, knowledge-base activity, and failure reasons. In the API, trace is enabled with `enableTrace`; in the console, use **Show trace**. Sources: [test and troubleshoot agent behavior](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-test.html) and [trace events](https://docs.aws.amazon.com/bedrock/latest/userguide/trace-events.html).

Diagnostic order:

1. Reproduce one minimal failing request.
2. Confirm the intended agent version or working draft is under test.
3. Locate the first divergent trace step.
4. Classify it as configuration, permission, orchestration, tool input, tool output, knowledge retrieval, or response behavior.
5. Make one bounded change and rerun the same request.
6. Retain before/after observations.

### 2. Working draft, prepare, version, alias

Know the difference between an editable working draft, a prepared draft, an immutable version, and an alias used by an application. AWS documents that draft changes must be prepared before testing, that the API test alias is `TSTALIASID`, and that deployed applications invoke an alias pointing to a version. After editing, verify that the tested configuration is current before diagnosing model behavior. Source: [test and troubleshoot agent behavior](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-test.html).

### 3. Action-group integration

Review both execution modes:

- Lambda fulfillment, where Bedrock passes the predicted operation and parameters to a function; and
- return control, where the predicted action and parameters return to the calling application.

For Lambda fulfillment, validate the schema or function definition, Bedrock input event, handler routing, response shape, error path, and resource-based invocation permission. Sources: [add an action group](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-action-add.html) and [action-group Lambda input and response](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-lambda.html).

### 4. IAM and resource policies

Separate identity-based access from resource-based access. The agent service role can require model invocation, S3 schema, knowledge-base, guardrail, collaboration, or KMS permissions depending on configuration. A Lambda action group also needs a resource-based policy that permits the Bedrock service principal to invoke it. Prefer the least privileges needed for the configured resources and inspect trust relationships and condition keys. Source: [create a service role for Bedrock Agents](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-permissions.html).

### 5. Knowledge-base isolation

When retrieval is implicated, isolate it from action groups and orchestration. Check that the intended knowledge base is associated and enabled, that the agent role may query it, and that the trace shows the expected query and result. AWS permits enabling or disabling action groups and knowledge bases in the working draft for troubleshooting; changes must be prepared before retesting. Source: [test and troubleshoot agent behavior](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-test.html).

### 6. Performance without weakening correctness

Measure a stable request before optimizing. AWS documents a reduced-call path for the narrow case of one knowledge base, no enabled action groups, no request for more user information, and the default orchestration prompt. An overridden prompt uses the standard flow and may increase calls and latency. Do not apply this pattern to an agent whose required behavior violates those preconditions. Source: [optimize performance with a single knowledge base](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-optimize-performance.html).

## Failure-to-check map

| Symptom | First checks |
| --- | --- |
| Recent edit appears ignored | Confirm working draft, prepare status, version, alias, and `preparedAt`. |
| Agent selects the wrong action | Inspect trace, action/function descriptions, schema names, parameters, and ambiguity between actions. |
| Action is selected but fails | Inspect tool input, Lambda logs where available, handler routing, response format, and invocation policy. |
| Knowledge answer is absent or irrelevant | Confirm association and enabled state, query trace, role permissions, and retrieved results before changing prompts. |
| Invocation is denied | Identify the denied principal, action, and resource; distinguish caller policy, service-role policy, trust policy, Lambda resource policy, and KMS policy. |
| Latency is high | Establish a repeatable baseline, count orchestration/tool/retrieval steps, and use the documented reduced-call path only when all preconditions apply. |

## 45–60 minute readiness drill

1. **10 minutes:** Draw the path `caller → alias/version → orchestration → action or knowledge base → response` and label the IAM boundary at each hop.
2. **15 minutes:** Use a disposable practice agent or official tutorial to trigger one action, inspect the trace, and identify the exact selected parameters. Do not use company or customer data.
3. **15 minutes:** Introduce one reversible practice fault, such as an intentionally mismatched function response in a personal sandbox, then classify, repair, and rerun it.
4. **10 minutes:** Review draft/prepare/version/alias behavior and the difference between a service-role policy and a Lambda resource policy.
5. **10 minutes:** Rehearse the diagnostic order above without making speculative multi-variable changes.

Do not incur paid AWS usage solely for this drill. If a disposable personal sandbox would create charges, use documentation review and the assessment's provisioned environment instead.

## Browser and account checklist

- [ ] Open the official [AWS Agentic AI Demonstrated Skill Builder page](https://skillbuilder.aws/learn/32Y249P272/aws-agentic-ai-demonstrated/TTAJ5WKYTS).
- [ ] Sign in personally; do not share authentication or recovery codes.
- [ ] Confirm the displayed assessment rules, duration, allowed resources, and system requirements. Treat this page—not this brief—as authoritative.
- [ ] Close unrelated tabs and notifications; connect power and a stable network.
- [ ] Confirm adequate uninterrupted time based on the duration AWS displays.
- [ ] Do not click **Start** until ready to complete the personal assessment block.
- [ ] After completion, retain only the permitted credential or verification link, not assessment content.

## Current product note

The current Bedrock documentation labels Amazon Bedrock Agents as **Amazon Bedrock Agents Classic** and says it is no longer open to new customers, while existing customers may continue to use it. The public microcredential announcement still describes the assessment in terms of agents built with Amazon Bedrock. Therefore the exact service surface presented in the provisioned assessment remains `UNVERIFIED` until AWS displays it; follow the assessment environment and instructions rather than assuming a console layout. Source: [current Bedrock agent testing documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-test.html).
