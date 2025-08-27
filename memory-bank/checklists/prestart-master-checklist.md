# PRE-START Master Checklist (Solo Freelancer Autonomy Pack)

## A. Repo Prep (Structure at Wiring)

### ✅ Core Framework Files
- [ ] `.cursor/rules/orchestrator.mdc` exists
- [ ] `.cursor/rules/globals.mdc` exists
- [ ] `.cursor/rules/readiness_check.mdc` exists

### ✅ PRE-START Kit Files
- [ ] `.cursor/rules/kits/prestart/client_screener.mdc`
- [ ] `.cursor/rules/kits/prestart/capacity_planner.mdc`
- [ ] `.cursor/rules/kits/prestart/pricing_policy.mdc`
- [ ] `.cursor/rules/kits/prestart/estimate_sizer.mdc`
- [ ] `.cursor/rules/kits/prestart/proposal_builder.mdc`
- [ ] `.cursor/rules/kits/prestart/demo_playbook.mdc`
- [ ] `.cursor/rules/kits/prestart/repo_bootstrapper.mdc`
- [ ] `.cursor/rules/kits/prestart/risk_catalog.mdc`
- [ ] `.cursor/rules/kits/prestart/scope_guard.mdc`

### ✅ Globs Configuration
- [ ] Globs are narrow (not repo-wide): `"memory-bank/**"`, `"templates/**"`, (optional `"demos/**"`)
- [ ] `readiness_check.mdc` updated with `exists_all([...])` for all PRE-START outputs

## B. Templates & Data Folders

### ✅ Template Directory
- [ ] `templates/` exists with:
  - [ ] Proposal templates
  - [ ] Contract templates
  - [ ] Ratecard templates
  - [ ] Estimate matrix templates

### ✅ Memory Bank Structure
- [ ] `memory-bank/business/` exists
- [ ] `memory-bank/plan/` exists
- [ ] `memory-bank/scope/` exists
- [ ] `memory-bank/demo/` exists
- [ ] `memory-bank/bootstrap/` exists

## C. Required Artifacts List (PRE-START Gate Pass Condition)

### 🔴 Required (Must Exist)
- [ ] `memory-bank/business/client_score.json`
- [ ] `memory-bank/business/capacity_report.md`
- [ ] `memory-bank/business/pricing.ratecard.yaml`
- [ ] `memory-bank/business/estimate_brief.md`
- [ ] `memory-bank/plan/proposal.md`

### 🟡 Optional but Recommended
- [ ] `memory-bank/scope/baseline.yaml`
- [ ] `memory-bank/demo/demo_playbook.md`
- [ ] `memory-bank/bootstrap/manifest.yaml`
- [ ] `memory-bank/risk_catalog.md`

**Note**: Add all items to `exists_all([...])` in `readiness_check.mdc` to hard-block PLAN phase when incomplete.

## D. Command Flow (Run Order + Acceptance Criteria)

### 1. `/pricing` → Ratecard & Terms
**Files**: `pricing.ratecard.yaml`, `terms.md`
**Criteria**:
- [ ] Rates edited (base, rush, weekend)
- [ ] Terms include: upfront %, CR policy, invoicing terms

### 2. `/screen_client` → Fit Score & Red Flags
**Files**: `client_score.json`, `red_flags.md`
**Criteria**:
- [ ] `fit_score` set (0-100)
- [ ] `must_ask` ≥ 3 items
- [ ] If `project_risk = HIGH` → re-screen or decline path ready

### 3. `/capacity` → Overcommit Guard
**File**: `capacity_report.md`
**Criteria**:
- [ ] Weekly availability present
- [ ] Recommendation set (ACCEPT|WAITLIST|DECLINE)

### 4. `/estimate` → T-shirt + Risk Buffer
**Files**: `estimate_brief.md`, `estimate.matrix.yaml`
**Criteria**:
- [ ] Size set (S/M/L/XL)
- [ ] Risk buffer (10-40%)
- [ ] Key uncertainties listed (≥3)

### 5. `/proposal` → Goal-level Proposal (No Solutioning)
**File**: `proposal.md`
**Criteria**:
- [ ] Sections present: Outcomes, In-Scope, Out-of-Scope, Milestones, Pricing, Next Steps
- [ ] Out-of-Scope is explicit (scope-creep defense)

### 6. `/scope_baseline` → Baseline & Event Log
**Files**: `scope/baseline.yaml`, `scope/scope_event_log.md`
**Criteria**:
- [ ] Baseline matches proposal's In-Scope/Out-of-Scope
- [ ] 1 entry in event log: "baseline created"

### 7. `/demo` → 5-10 Min Demo Script
**Files**: `demo_playbook.md`, `demo_checklist.md`, `demo_metrics.md`
**Criteria**:
- [ ] Flow has 5 steps (Context → Inputs → Run → Result → Next Steps)
- [ ] Checklist includes environment & rollback
- [ ] Metrics placeholders present (time-to-result, success rate)

### 8. `/bootstrap` → Repo Scaffold Manifest
**Files**: `bootstrap/manifest.yaml`, `bootstrap/tree.md`, `bootstrap/README.md`
**Criteria**:
- [ ] `demo_type` set (rag|rest_api|web_ui)
- [ ] `scripts/run_demo.sh` path planned in `tree.md`

### 9. `/risks` → Catalog & Tags
**Files**: `risk_catalog.md`, `risk_tags.yaml`
**Criteria**:
- [ ] Covered domains: planning, technical, data, security, delivery
- [ ] At least 1 mitigation per risk

### 10. `/preflight` → Gate to PLAN
**Criteria**:
- [ ] `readiness_check.mdc` passes (no missing files)
- [ ] System sets `phase = PLAN`
- [ ] Prompt appears: "✅ PRE-START PASS. You may run `/plan`."

## E. Negative Tests (Must-Block Scenarios)

### 🚫 Blocked Scenarios
- [ ] Try `/plan` before completing PRE-START → BLOCKED message appears
- [ ] Delete 1 required artifact (e.g., `pricing.ratecard.yaml`) → `/preflight` should fail
- [ ] Missing fields in `client_score.json` → screener should re-prompt via suggest

## F. Globs Sanity Check (No Bleed)

### ✅ PRE-START Kit Files
- [ ] Globs = `["memory-bank/**","templates/**","demos/**"]`

### ✅ Framework Rules
- [ ] Narrow scope (e.g., React = `**/*.tsx`, `**/*.jsx`; Python = `**/*.py`, `pyproject.toml`)

### ✅ Role Rules
- [ ] Phase/command-triggered
- [ ] `alwaysApply: false`

## G. Version Control Hygiene

### 🔄 Git Workflow
- [ ] Create branch `prestart-kit`
- [ ] Commit in small chunks:
  - [ ] Modules
  - [ ] Gate
  - [ ] Templates
- [ ] Tag `prestart-v0.1` after passing `/preflight`
- [ ] Pull request notes include: artifacts list + test evidence

## H. Documentation Touchups

### 📚 Documentation Updates
- [ ] `.cursor/rules/README.md` → add PRE-START overview + run order
- [ ] `routing.examples.md` → add how orchestrator attaches PRE-START rules
- [ ] `proposal.md` template notes: "no solutioning; outcomes only"

## I. Ready Signal (Handoff to PLANNING)

### ✅ Completion Verification
- [ ] `/preflight` PASS recorded (screenshot or log)
- [ ] `phase = PLAN` verified
- [ ] Next command to use: `/plan` (planning role set)

---

## Quick Status Check

**Current Phase**: [ ] PRE-START [ ] PLAN [ ] EXECUTE [ ] CLOSE

**PRE-START Completion**: [ ] 0% [ ] 25% [ ] 50% [ ] 75% [ ] 100%

**Next Action**: [ ] Run `/preflight` [ ] Fix missing artifacts [ ] Proceed to `/plan`

---

*Last Updated: [Date]*
*Status: [In Progress / Complete / Blocked]*
