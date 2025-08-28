# Memory Bank README

## Overview
This Memory Bank serves as the central knowledge repository for project management, client assessments, capacity planning, and operational workflows within the AdvancedRules framework. It contains structured data and documentation that supports decision-making throughout the project lifecycle.

## Directory Structure

### `/business/` - Business Intelligence & Planning
Contains core business documents that inform project decisions and resource allocation.

#### 📋 Capacity Report (`capacity_report.md`)
- **Weekly Availability**: 40 hours/week (Mon-Fri, flexible weekends)
- **Focus Blocks**: 9 AM - 12 PM, 2 PM - 6 PM
- **Hard Constraints**: No Wednesdays, max 2 active projects, 4-hour minimum blocks
- **Current Commitments**: Project A (8 hours/week ongoing)
- **Recommendation**: ACCEPT new projects (25 hours/week maximum)

#### 🎯 Client Assessment (`client_score.json`)
- **Fit Score**: 75/100 (Medium risk, Medium complexity)
- **Must-Ask Questions**:
  - Timeline requirements
  - Main point of contact
  - Success criteria
  - Budget range
- **Status**: No decline reasons noted, client appears reasonable

#### 📊 Project Estimation (`estimate_brief.md`)
- **Project Type**: Medium complexity (M)
- **Effort Estimate**: 150-200 hours (including 25% risk buffer)
- **Timeline**: 6 weeks total
  - Weeks 1-2: Discovery & Architecture (40 hours)
  - Weeks 3-4: Core Development (80 hours)
  - Week 5: Testing & QA (30 hours)
  - Week 6: Deployment & Documentation (20 hours)
- **Key Uncertainties**: Requirements clarity, integration complexity, testing requirements, deployment environment

#### 💰 Pricing Structure (`pricing.ratecard.yaml`)
- **Base Rates**:
  - Hourly: $75
  - Daily: $600
  - Weekly: $3,000
- **Rush Rates**: $95/hour (+25%)
- **Weekend Rates**: $85/hour (+13%)
- **Package Pricing**:
  - Discovery & Planning: $1,500 (1-2 weeks)
  - Development & Testing: T&M or Fixed (project dependent)
  - Post-Launch Support: $500 (1 month)
- **Terms**: 50% upfront, Net 15 days, 2% late fee after 30 days

### `/checklists/` - Operational Checklists
Standardized checklists and runbooks for consistent project execution.

#### 📋 PRE-START Master Checklist (`prestart-master-checklist.md`)
Comprehensive checklist covering:
- **Repo Preparation**: Framework files, PRE-START kit files, globs configuration
- **Template & Data Folders**: Template directory, memory bank structure
- **Required Artifacts**: 5 mandatory files for gate passage
- **Command Flow**: 10-step execution order with acceptance criteria
- **Negative Tests**: Must-block scenarios for validation
- **Version Control**: Git workflow and hygiene practices

#### 🚀 PRE-START Runbook (`prestart-runbook.md`)
Detailed execution guide with exact command order:
1. `/pricing` → Ratecard & terms setup
2. `/screen_client` → Client assessment
3. `/capacity` → Team availability check
4. `/estimate` → Project estimation
5. `/proposal` → Goal-level proposal
6. `/upwork_cover` → Upwork-specific assets
7. `/upwork_checks` → Offer status setup
8. `/preflight` → Final gate check

### `/plan/` - Project Planning Documents
Strategic planning documents for project initiation and execution.

#### 📋 Client Brief Template (`client_brief.md`)
Structured template for documenting:
- Business objectives and success metrics
- Technical requirements (functional & non-functional)
- Constraints and assumptions
- Risk assessment matrix
- Next steps and action items

#### 📄 Project Proposal (`proposal.md`)
*Currently empty - to be populated during proposal phase*

### `/upwork/` - Upwork Integration
Upwork-specific documentation and status tracking.

#### 📊 Offer Status (`offer_status.json`)
*Currently empty - to be populated when Upwork offer is received*

### `/logs/` & `/reports/` - Tracking & Analytics
*Currently empty directories for future use*

## Key Workflows

### PRE-START Phase Workflow
1. **Pricing Setup** → Establish rates and terms
2. **Client Screening** → Assess fit and risk
3. **Capacity Planning** → Check resource availability
4. **Project Estimation** → Create timeline and budget estimates
5. **Proposal Development** → Craft goal-level proposal
6. **Upwork Preparation** → Create cover letter and milestones
7. **Offer Management** → Track contract status and funding
8. **Gate Check** → Validate all prerequisites before planning

### Required Artifacts for Gate Passage
```
✅ memory-bank/business/client_score.json
✅ memory-bank/business/capacity_report.md
✅ memory-bank/business/pricing.ratecard.yaml
✅ memory-bank/business/estimate_brief.md
✅ memory-bank/plan/proposal.md
```

### Upwork Contract Requirements
- **Fixed Price**: Requires escrow funding (Milestone 1 funded)
- **Hourly**: Requires Work Diary enabled + weekly cap hours set

## Current Status

### ✅ Completed Assessments
- Client fit score: 75/100 (Medium risk)
- Capacity assessment: Ready for new projects
- Project estimation: 150-200 hours (6 weeks)
- Pricing structure: Established with flexible packages

### ⏳ Pending Items
- Project proposal document
- Upwork offer status
- Specific client requirements gathering

### 🎯 Recommendations
- Start new projects with 25 hours/week maximum
- Maintain 15 hours/week buffer for existing commitments
- Consider Week 2 start for proper project handoff
- Focus on requirements clarification in discovery phase

## Usage Guidelines

1. **Update regularly** - Keep capacity reports and client assessments current
2. **Follow checklists** - Use PRE-START checklist for consistent execution
3. **Validate gate conditions** - Ensure all required artifacts exist before advancing phases
4. **Document decisions** - Record rationale for capacity decisions and risk assessments

## Contact & Support
For questions about Memory Bank structure or workflows, refer to the AdvancedRules framework documentation or contact the development team.

---
*Last Updated: $(date)*
*Framework Version: AdvancedRules v1.0*
