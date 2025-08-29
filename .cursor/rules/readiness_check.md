---
description: "PRE-START Acceptance Gate for solo freelancer workflow"
globs: ["**/*"]
alwaysApply: true
---

# PRE-START Acceptance Gate
<rule>
name: prestart_gate
description: |
  Hindi papayagang mag-PLAN kung kulang ang pre-start artifacts.
  Target outputs na dapat meron bago tumuloy:
  - memory-bank/business/client_score.json
  - memory-bank/business/capacity_report.md
  - memory-bank/business/pricing.ratecard.yaml
  - memory-bank/business/estimate_brief.md
  - memory-bank/plan/proposal.md
triggers:
  - command: "/preflight"
actions:
  - type: attach_rules
    rules:
      - "kits/prestart/client_screener.mdc"
      - "kits/prestart/capacity_planner.mdc"
      - "kits/prestart/pricing_policy.mdc"
      - "kits/prestart/estimate_sizer.mdc"
      - "kits/prestart/proposal_builder.mdc"
  - type: suggest
    message: |
      ▶ PRE-START initiated. Tumatakbo ang screener, capacity, pricing, estimate, at proposal.
      Kapag kumpleto na ang artifacts, tatak ang gate as PASS.
  - type: set_state
    key: "phase"
    value: "PRE_START"
</rule>

# Block planning kung kulang
<rule>
name: block_planning_if_incomplete
description: "Hard block kapag may nawawalang required files"
filters:
  - type: equals
    key: "phase"
    value: "PRE_START"
actions:
  - type: reject
    when: missing_all([
      "memory-bank/business/client_score.json",
      "memory-bank/business/capacity_report.md",
      "memory-bank/business/pricing.ratecard.yaml",
      "memory-bank/business/estimate_brief.md",
      "memory-bank/plan/proposal.md"
    ])
    message: |
      ⛔ PRE-START incomplete. Run `/preflight` at ayusin ang kulang.
  - type: set_state
    when: exists_all([
      "memory-bank/business/client_score.json",
      "memory-bank/business/capacity_report.md",
      "memory-bank/business/pricing.ratecard.yaml",
      "memory-bank/business/estimate_brief.md",
      "memory-bank/plan/proposal.md"
    ])
    key: "phase"
    value: "PLAN"
  - type: suggest
    when: equals("PLAN", state("phase"))
    message: "✅ PRE-START PASS. You may run `/plan`."
</rule>
