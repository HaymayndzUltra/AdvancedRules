# Prestart Kits

This directory contains specialized rule kits designed to streamline the pre-project engagement process. These kits ensure comprehensive preparation before project planning begins, following the AdvancedRules framework's pre-start acceptance gate requirements.

## Overview

The prestart phase is a critical gate that must be completed before any project planning can commence. These kits provide structured workflows to assess client fit, evaluate capacity, establish pricing, create estimates, and build proposals.

## Required Artifacts

Before proceeding to the planning phase, the following artifacts must be generated:

- `memory-bank/business/client_score.json` - Client fit assessment
- `memory-bank/business/capacity_report.md` - Team capacity evaluation  
- `memory-bank/business/pricing.ratecard.yaml` - Pricing structure
- `memory-bank/business/estimate_brief.md` - Project estimation
- `memory-bank/plan/proposal.md` - Client proposal document

## Available Kits

### 1. Client Screener (`client_screener.mdc`)
**Purpose**: Evaluate client fit and identify potential red flags  
**Command**: `/screen_client`  
**Outputs**: 
- Client fit score (0-100)
- Project risk assessment (LOW/MEDIUM/HIGH)
- Complexity classification (S/M/L/XL)
- Critical questions to ask
- Decline reasons if applicable

**Use Case**: First step in client engagement to determine if the project is a good fit.

### 2. Capacity Planner (`capacity_planner.mdc`)
**Purpose**: Assess team availability and avoid overcommitment  
**Command**: `/capacity`  
**Outputs**: 
- Weekly availability report
- Hard constraints identification
- Open slots calculation for next 4 weeks
- Accept/Waitlist/Decline recommendation

**Use Case**: Ensure realistic project commitments based on current workload.

### 3. Pricing Policy (`pricing_policy.mdc`)
**Purpose**: Establish rate structure and payment terms  
**Command**: `/pricing`  
**Outputs**: 
- Rate card with service tiers
- Payment terms and conditions
- Package pricing options
- Time & materials rates

**Use Case**: Standardize pricing approach and ensure profitability.

### 4. Estimate Sizer (`estimate_sizer.mdc`)
**Purpose**: Create goal-level, risk-adjusted project estimates  
**Command**: `/estimate`  
**Outputs**: 
- High-level effort estimation
- Risk factors and mitigation strategies
- Timeline projections
- Resource requirements

**Use Case**: Provide clients with realistic project scope and timeline expectations.

### 5. Proposal Builder (`proposal_builder.mdc`)
**Purpose**: Create comprehensive client proposals  
**Command**: `/proposal`  
**Outputs**: 
- Clear project outcomes and success metrics
- In-scope and out-of-scope items
- Timeline with milestones
- Pricing references
- Next steps and start conditions

**Use Case**: Present professional proposals that clearly define project boundaries.

### 6. Demo Playbook (`demo_playbook.mdc`)
**Purpose**: Standardize demo presentations (5-10 minutes)  
**Command**: `/demo`  
**Outputs**: 
- Structured demo flow
- Key talking points
- Success criteria
- Follow-up actions

**Use Case**: Consistent client demonstrations that focus on goal-level outcomes.

### 7. Risk Catalog (`risk_catalog.mdc`)
**Purpose**: Maintain reusable list of common risks and mitigations  
**Command**: `/risks`  
**Outputs**: 
- Risk identification checklist
- Mitigation strategies
- Contingency planning
- Risk register template

**Use Case**: Proactive risk management and consistent risk assessment.

### 8. Scope Guard (`scope_guard.mdc`)
**Purpose**: Establish baseline scope and change request workflow  
**Command**: `/scope`  
**Outputs**: 
- Scope baseline definition
- Change request process
- Approval workflows
- Impact assessment templates

**Use Case**: Prevent scope creep and manage project changes effectively.

### 9. Repo Bootstrapper (`repo_bootstrapper.mdc`)
**Purpose**: Create minimal, demo-ready project scaffolds  
**Command**: `/bootstrap`  
**Outputs**: 
- Project repository structure
- Basic configuration files
- Demo-ready templates
- Development environment setup

**Use Case**: Quick project initialization with consistent structure.

## Workflow

### Preflight Check
Run `/preflight` to initiate all prestart kits simultaneously. This command will:
1. Execute all prestart kits in sequence
2. Generate required artifacts
3. Validate completeness
4. Mark the pre-start gate as PASS when complete

### Sequential Execution
Alternatively, run kits individually in this recommended order:
1. `/screen_client` - Assess client fit
2. `/capacity` - Evaluate team capacity
3. `/pricing` - Establish pricing structure
4. `/estimate` - Create project estimates
5. `/proposal` - Build client proposal

### Validation
The system automatically validates that all required artifacts are present before allowing progression to the planning phase.

## File Structure

```
memory-bank/
├── business/
│   ├── client_score.json      # Client fit assessment
│   ├── capacity_report.md     # Team capacity
│   ├── pricing.ratecard.yaml  # Pricing structure
│   ├── estimate_brief.md      # Project estimation
│   └── red_flags.md          # Client red flags
└── plan/
    └── proposal.md            # Client proposal
```

## Best Practices

1. **Complete All Kits**: Don't skip any prestart kits - they're designed to work together
2. **Validate Outputs**: Review generated artifacts for accuracy and completeness
3. **Update Regularly**: Keep artifacts current as project details evolve
4. **Follow Sequence**: Execute kits in the recommended order for best results
5. **Document Decisions**: Use the generated artifacts as living documents

## Integration

These kits integrate with the broader AdvancedRules framework:
- **Phase Management**: Automatically manages project phase transitions
- **Validation Gates**: Enforces completion requirements before planning
- **Memory Bank**: Stores all artifacts in organized, searchable format
- **Workflow Automation**: Streamlines the entire pre-project process

---

*Maintained by AdvancedRules Framework - Prestart Phase Management*
