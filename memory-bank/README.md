# Memory Bank Directory

The `memory-bank/` directory serves as the persistent knowledge repository for the AdvancedRules AI orchestration framework. It stores all artifacts, documents, and state information generated throughout the AI workflow pipeline.

## 📁 Directory Structure

```
memory-bank/
├── artifacts_index.json          # Provenance index (auto-updated)
├── business/                     # Business artifacts and client data
│   ├── capacity_report.md        # Capacity planning and resource assessment
│   ├── client_score.json         # Client evaluation and scoring data
│   ├── estimate_brief.md         # Project estimation documentation
│   └── pricing.ratecard.yaml     # Pricing structure and rate cards
├── plan/                         # Project planning and requirements
│   ├── acceptance_criteria.json  # Project acceptance criteria
│   ├── Action_Plan.md           # Detailed action plan and roadmap
│   ├── client_brief.md          # Client requirements and objectives
│   ├── Final_Implementation_Plan.md # Final implementation strategy
│   ├── framework_analysis_prompt.md # Framework analysis prompts
│   ├── product_backlog.yaml     # Product backlog and features
│   ├── product_vision.md        # Product vision and goals
│   ├── proposal.md              # Project proposal document
│   ├── simple_framework_analysis_prompt.md # Simplified analysis prompts
│   ├── Summary_Report.md        # Project summary and overview
│   ├── task_breakdown.yaml      # Detailed task breakdown
│   ├── technical_plan.md        # Technical implementation plan
│   ├── user_stories.md          # User stories and requirements
│   └── Validation_Report.md     # Validation and testing report
├── checklists/                   # Operational checklists and runbooks
│   ├── prestart-master-checklist.md # Master prestart checklist
│   └── prestart-runbook.md      # Detailed prestart procedures
└── upwork/                       # Upwork integration data
    └── offer_status.json        # Upwork offer status and tracking
```

## 🎯 Purpose & Functionality

### Business Intelligence (`business/`)
- **Client Scoring**: Evaluates client fit, requirements, and project viability
- **Capacity Planning**: Assesses resource availability and project capacity
- **Pricing Strategy**: Defines pricing models and rate structures
- **Estimation**: Provides project timeline and effort estimates

### Project Planning (`plan/`)
- **Requirements Analysis**: Captures and analyzes client requirements
- **Technical Architecture**: Defines technical implementation approach
- **Project Roadmap**: Creates detailed project timelines and milestones
- **Quality Assurance**: Establishes validation and testing criteria

### Operational Procedures (`checklists/`)
- **Prestart Checklists**: Ensures all prerequisites are met before project initiation
- **Runbooks**: Provides step-by-step procedures for various operations
- **Quality Gates**: Defines validation checkpoints throughout the process

### Integration Management (`upwork/`)
- **Offer Tracking**: Monitors Upwork offer status and client interactions
- **Contract Management**: Tracks contract details and milestones
- **Client Communication**: Maintains communication records and agreements

## 🔄 Artifact Lifecycle

### Creation & Indexing
- Artifacts are automatically indexed with SHA-256 hashes when created by AI roles
- The `artifacts_index.json` maintains provenance and version control
- All artifacts follow standardized JSON schema validation

### Validation & Quality Assurance
```bash
# Validate all artifacts against schemas
python3 ../tools/schema/validate_artifacts.py

# Check artifact integrity
python3 ../tools/artifacts/hash_index.py --verify
```

### Version Control & Provenance
- Every artifact maintains a complete audit trail
- SHA-256 hashes ensure content integrity
- Timestamps track creation and modification history
- Role attribution identifies which AI persona created each artifact

## 📊 Key Artifacts Overview

### Client & Business Intelligence
| Artifact | Purpose | Format |
|----------|---------|--------|
| `client_score.json` | Client evaluation metrics | JSON |
| `capacity_report.md` | Resource capacity analysis | Markdown |
| `pricing.ratecard.yaml` | Pricing structure | YAML |
| `estimate_brief.md` | Project estimation | Markdown |

### Project Planning & Execution
| Artifact | Purpose | Format |
|----------|---------|--------|
| `client_brief.md` | Requirements documentation | Markdown |
| `technical_plan.md` | Technical implementation | Markdown |
| `product_backlog.yaml` | Feature specifications | YAML |
| `acceptance_criteria.json` | Success criteria | JSON |
| `Action_Plan.md` | Execution roadmap | Markdown |

### Quality & Validation
| Artifact | Purpose | Format |
|----------|---------|--------|
| `Summary_Report.md` | Project overview | Markdown |
| `Validation_Report.md` | Quality assessment | Markdown |
| `user_stories.md` | User requirements | Markdown |

## 🔧 Maintenance & Operations

### Regular Maintenance Tasks
- **Artifact Cleanup**: Remove outdated or superseded artifacts
- **Index Updates**: Ensure artifacts_index.json is current
- **Schema Validation**: Regular validation against JSON schemas
- **Backup Procedures**: Maintain secure backups of critical artifacts

### Automated Processes
- **Provenance Tracking**: Automatic SHA-256 hashing and indexing
- **Schema Validation**: Continuous validation during artifact creation
- **Audit Logging**: Complete activity logging for compliance
- **Integrity Checks**: Regular content integrity verification

## 📋 Operational Guidelines

### Artifact Creation Standards
1. **Naming Conventions**: Use descriptive, consistent naming
2. **Format Standards**: Follow established JSON/YAML/Markdown formats
3. **Schema Compliance**: All artifacts must pass schema validation
4. **Documentation**: Include comprehensive inline documentation

### Quality Assurance Procedures
1. **Pre-Creation Review**: Validate requirements before artifact creation
2. **Content Validation**: Ensure accuracy and completeness
3. **Cross-Reference Checking**: Verify consistency across related artifacts
4. **Approval Workflows**: Implement review and approval processes

## 🚨 Troubleshooting

### Common Issues
- **Schema Validation Errors**: Check artifact format against schema definitions
- **Missing Dependencies**: Ensure all prerequisite artifacts exist
- **Integrity Failures**: Rebuild artifacts_index.json if corrupted
- **Permission Issues**: Verify file system permissions for AI role access

### Recovery Procedures
```bash
# Rebuild artifacts index
python3 ../tools/artifacts/hash_index.py --rebuild

# Full validation sweep
python3 ../tools/schema/validate_artifacts.py --comprehensive

# Integrity verification
python3 ../tools/artifacts/hash_index.py --verify-all
```

## 🔗 Integration Points

### Framework Components
- **Decision Scoring**: Uses business intelligence for candidate evaluation
- **Role Execution**: Consumes planning artifacts for task execution
- **Observability**: Generates metrics from artifact creation patterns
- **Audit System**: Maintains compliance records and audit trails

### External Systems
- **Upwork Platform**: Bidirectional synchronization with offer status
- **Client Management**: Integration with client relationship systems
- **Project Management**: Synchronization with PM tools and workflows

---

**Memory Bank** - The persistent knowledge foundation of AdvancedRules AI orchestration! 🧠💾
