# PRE-START Runbook (Exact Execution Order)

## A. Bago mag-submit ng proposal sa Upwork

### 1. `/pricing` → Pricing & Terms Setup
**Command**: `/pricing`  
**Outputs**: 
- `memory-bank/business/pricing.ratecard.yaml`
- `memory-bank/business/terms.md`

**Fill**: 
- Base rates, rush rates, weekend rates
- Upfront payment percentage
- Change request policy
- Invoicing terms

### 2. `/screen_client` → Client Assessment
**Command**: `/screen_client`  
**Outputs**: 
- `memory-bank/business/client_score.json`
- `memory-bank/business/red_flags.md`

**Fill**: 
- Fit score (0-100)
- Project risk (LOW/MEDIUM/HIGH)
- Complexity (S/M/L/XL)
- Must-ask questions (≥3)
- Decline reasons if applicable

### 3. `/capacity` → Team Availability Check
**Command**: `/capacity`  
**Outputs**: 
- `memory-bank/business/capacity_report.md`

**Check**: 
- Weekly availability hours
- Hard constraints
- Recommendation: ACCEPT|WAITLIST|DECLINE

### 4. `/estimate` → Project Estimation
**Command**: `/estimate`  
**Outputs**: 
- `memory-bank/business/estimate_brief.md`
- `memory-bank/business/estimate.matrix.yaml`

**Fill**: 
- T-shirt size (S/M/L/XL)
- Risk buffer (10-40%)
- Key uncertainties (≥3)
- Timeline projections

### 5. `/proposal` → Goal-Level Proposal
**Command**: `/proposal`  
**Outputs**: 
- `memory-bank/plan/proposal.md`

**Fill**: 
- Outcomes (measurable success criteria)
- In-Scope deliverables
- Out-of-Scope exclusions
- Timeline & milestones
- Pricing reference
- Next steps

### 6. `/upwork_cover` → Upwork-Specific Assets
**Command**: `/upwork_cover`  
**Outputs**: 
- `memory-bank/upwork/cover_letter.md`
- `memory-bank/upwork/milestones.yaml` (fixed-price)
- `memory-bank/upwork/hourly_scope.md` (hourly)

**Fill**: 
- Cover letter (200-300 words, goal-level)
- Milestones with amounts & dates (fixed)
- Weekly scope & cap hours (hourly)

### 7. (Optional) `/connects_policy` → Boost Decision
**Command**: `/connects_policy`  
**Outputs**: 
- `memory-bank/upwork/connects_decision.md`

**Fill**: 
- Fit score from client screener
- Competition level assessment
- Boost decision: no_boost|boost_low|boost_mid|boost_high

---

## B. Kapag may offer na sa Upwork

### 8. `/upwork_checks` → Offer Status Setup
**Command**: `/upwork_checks`  
**Outputs**: 
- `memory-bank/upwork/offer_status.json` (auto-created if missing)

**Fill from actual Upwork offer**:
```json
{
  "contract_type": "fixed|hourly",
  "escrow_funded": true,  // if fixed AND Milestone 1 funded
  "work_diary_ready": true,  // if hourly
  "weekly_cap_hours": 40,  // if hourly, set actual cap
  "notes": "Paste key details from Upwork offer here."
}
```

**Rules**:
- **Fixed Price**: `escrow_funded = true` (Milestone 1 must be funded)
- **Hourly**: `work_diary_ready = true` AND `weekly_cap_hours > 0`

### 9. `/preflight` → Final Gate Check
**Command**: `/preflight`  
**System Action**: 
- Validates all required artifacts
- Checks Upwork contract conditions
- Sets `phase = PLAN` if PASS
- Shows BLOCK message if incomplete

**Expected Result**:
- ✅ **PASS**: "✅ PRE-START PASS (Upwork conditions met). You may run /plan."
- ⛔ **BLOCK**: Fix missing artifacts/flags per error message

---

## Quick Reference

### Required Files for Gate Passage:
```
memory-bank/business/
├── client_score.json      # /screen_client
├── capacity_report.md     # /capacity  
├── pricing.ratecard.yaml  # /pricing
├── estimate_brief.md      # /estimate
└── red_flags.md          # /screen_client

memory-bank/plan/
└── proposal.md            # /proposal

memory-bank/upwork/
└── offer_status.json      # /upwork_checks
```

### Upwork Contract Types:
- **Fixed Price**: Requires `escrow_funded: true`
- **Hourly**: Requires `work_diary_ready: true` + `weekly_cap_hours > 0`

### Next Phase:
After `/preflight` PASS → `phase = PLAN` → Ready for `/plan` command

---

## Status Tracking

**Current Phase**: [ ] PRE-START [ ] PLAN [ ] EXECUTE [ ] CLOSE

**PRE-START Progress**: 
- [ ] Pricing & Terms
- [ ] Client Screening  
- [ ] Capacity Check
- [ ] Estimation
- [ ] Proposal
- [ ] Upwork Cover
- [ ] Connects Policy (optional)
- [ ] Offer Status
- [ ] Preflight Check

**Next Action**: [ ] Submit to Upwork [ ] Wait for offer [ ] Run /upwork_checks [ ] Run /preflight

---

*Last Updated: [Date]*
*Status: [In Progress / Ready for Upwork / Offer Received / Gate Passed]*
