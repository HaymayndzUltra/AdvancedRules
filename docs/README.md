# Documentation Directory

This directory contains all project documentation, technical guides, and architectural documents for the AdvancedRules AI Framework.

## 📚 Documentation Contents

### Core Documentation
- `FRAMEWORK_SUMMARY.md` - Complete framework architecture and capabilities overview
- `FOLDER_STRUCTURE.md` - Detailed project structure and directory organization
- `VALIDATION_SUITE_STRUCTURE.md` - Validation and testing framework documentation
- `UPWORK_IMPLEMENTATION_GUIDE.md` - Guide for Upwork freelancer integration

### Technical Reports
- `QUEUE_SYSTEM_TEST_REPORT.md` - Queue system implementation and test results
- `RAG_MERGE_CHECKLIST.md` - RAG (Retrieval-Augmented Generation) integration checklist
- `TEST_SUMMARY.md` - Comprehensive test suite summary
- `report1.md` & `report2.md` - Additional technical analysis reports
- `next_prompt_for_cursor.md` - Cursor AI integration prompts

### ADRs (Architecture Decision Records)
- Located in `ADRs/` subdirectory
- Documenting key architectural decisions and their rationale

## 🏗️ Framework Architecture

### Core Components

#### Orchestrators
- **Execution Orchestrator**: Central coordination hub for AI persona management
- **Framework Memory Bridge**: Persistent memory and knowledge sharing
- **Rules Master Toggle**: Central control system for framework activation

#### AI Personas
- **Product Owner AI**: Strategic product management and vision alignment
- **Planning AI**: Project planning and roadmap development
- **Principal Engineer AI**: Technical architecture and engineering decisions
- **Codegen AI**: Automated code generation and implementation
- **Security AI**: Security analysis and vulnerability assessment
- **QA AI**: Quality assurance and testing strategy
- **Auditor AI**: Compliance validation and quality auditing

#### Domain Knowledge
- **Frontend**: React, Vue, Svelte, Next.js, Tailwind
- **Backend**: Python, FastAPI, Node.js, Java, Go
- **Mobile**: React Native, Flutter, Android
- **Testing**: Jest, Playwright, PHPUnit
- **Specialized**: AI/ML, Blockchain, DevOps
- **Utilities**: TypeScript, Database, Git, Clean Code

## 🚀 Getting Started (Operational Quickstart)

### Prerequisites
- Git
- Node.js 18+ (for frontend development)
- Python 3.8+ (for backend development)
- Docker (for containerized development)

### Run the solo-freelancer pipeline
```bash
# Prestart / Upwork readiness
python3 tools/prestart/prestart_composite.py

# One-command happy path
python3 tools/quickstart.py

# Or manual steps
mkdir -p memory-bank/plan
printf "Client brief" > memory-bank/plan/client_brief.md
python3 tools/run_role.py product_owner_ai
python3 tools/run_role.py planning_ai
python3 tools/run_role.py auditor_ai
python3 tools/run_role.py principal_engineer_ai --mode PEER_REVIEW
python3 tools/run_role.py principal_engineer_ai --mode SYNTHESIS
```

### Configuration
1. Copy `.env.example` to `.env`
2. Configure your AI service credentials
3. Set up your preferred development environment
4. Configure the Rules Master Toggle

## 🔧 Usage

### Basic Workflow
1. **Activate Framework**: Use Rules Master Toggle to activate required personas
2. **Define Requirements**: Product Owner AI creates user stories and requirements
3. **Plan Development**: Planning AI creates project roadmap and timeline
4. **Generate Code**: Codegen AI implements features based on specifications
5. **Quality Assurance**: QA AI and Security AI validate code quality
6. **Audit & Deploy**: Auditor AI ensures compliance before deployment

### Decision Scoring v3 + Trigger
```bash
# Score
python3 tools/decision_scoring/advanced_score.py

# Trigger (dry-run)
python3 tools/orchestrator/trigger_next.py --dry-run --candidates tools/decision_scoring/examples/trigger_candidates.json
```

## 📁 Project Structure (key paths)

```
AdvancedRules/
├── .cursor/rules/           # AI framework rules and personas
│   ├── orchestrator/        # Core control systems
│   ├── roles/              # AI persona definitions
│   └── domains/            # Domain-specific knowledge
├── memory-bank/            # AI-generated artifacts and memory
├── tools/                  # Runner, scoring, orchestrator, provenance, etc.
├── docs/                   # Documentation and ADRs
└── tests/                  # E2E + smoke tests
```

## 🎭 AI Personas

### Product Owner AI
- Translates business objectives into technical requirements
- Creates user stories with acceptance criteria
- Manages product backlog priorities
- Defines success metrics and KPIs

### Principal Engineer AI
- Establishes technical architecture and standards
- Makes critical engineering decisions
- Ensures code quality and best practices
- Manages technical debt and performance

### Codegen AI
- Generates production-ready code
- Implements design patterns and principles
- Ensures code quality and testing
- Creates comprehensive documentation

### Security AI
- Identifies security vulnerabilities
- Implements security best practices
- Ensures compliance with security standards
- Provides security testing and validation

## 🔒 Security & Compliance

- **Security First**: All code undergoes security review
- **Compliance Ready**: Built-in support for industry standards
- **Audit Trail**: Complete tracking of all decisions and changes
- **Quality Gates**: Automated validation at every stage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests and documentation
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the [docs/](docs/) directory
- **Issues**: Report bugs and feature requests via GitHub Issues
- **Discussions**: Join community discussions on GitHub Discussions

## 🗺️ Roadmap

- [ ] Enhanced AI persona coordination
- [ ] Advanced memory management
- [ ] Integration with external AI services
- [ ] Real-time collaboration features
- [ ] Advanced analytics and insights

---

**AdvancedRules** - Where AI meets software development excellence.
