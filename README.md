# AdvancedRules AI Framework

A sophisticated AI orchestration framework that coordinates multiple specialized AI personas to deliver high-quality software development outcomes.

## �� Overview

AdvancedRules is an intelligent framework that orchestrates specialized AI personas to handle different aspects of software development, from product planning to code generation and quality assurance.

## 🏗️ Architecture Components

### 1. Core Orchestrators (`.cursor/rules/orchestrator/`)
- **Execution Orchestrator**: Central coordination hub for AI persona management
- **Framework Memory Bridge**: Persistent memory and knowledge sharing system
- **Rules Master Toggle**: Central control system for framework activation

### 2. AI Personas (`.cursor/rules/roles/`)
- **Product Owner AI**: Strategic product management and requirements
- **Planning AI**: Project planning and roadmap development
- **Principal Engineer AI**: Technical architecture and engineering decisions
- **Codegen AI**: Automated code generation and implementation
- **Security AI**: Security analysis and vulnerability assessment
- **QA AI**: Quality assurance and testing strategy
- **Auditor AI**: Compliance validation and quality auditing
- **Documentation AI**: Documentation creation and maintenance

### 3. Domain Knowledge (`.cursor/rules/domains/`)
- **Frontend**: React, Vue, Svelte, Next.js, Tailwind, HTMX, SolidJS, Qwik
- **Backend**: Python, FastAPI, Node.js, Java, Go, C#, Rust, Laravel, WordPress, Convex
- **Mobile**: React Native, Flutter, Android, NativeScript
- **Testing**: Jest, Playwright, PHPUnit
- **Specialized**: AI/ML, Blockchain, DevOps
- **Utilities**: TypeScript, Database, Git, Clean Code, Medusa, BeefreeSDK

### 4. Memory Management (`memory-bank/`)
- **Plan**: Client briefs, product backlogs, technical plans
- **Reports**: Security findings, test plans, audit reports
- **Logs**: Handoff logs, gate results, execution tracking

### 6. Operational Stack (New)
- **Runner + Plugins**: `tools/run_role.py`, `tools/runner/plugins/*` (per-role execution, event logging)
- **Decision Scoring v3**: `tools/decision_scoring/advanced_score.py` (calibration, exploration, shadow) + metrics
- **Trigger**: `tools/orchestrator/trigger_next.py` (scorer → registry)
- **State Engine**: `tools/orchestrator/state.py` (idempotent transitions; `workflow_state.json`)
- **Provenance**: `tools/artifacts/hash_index.py` → `memory-bank/artifacts_index.json`
- **Attach Log**: `tools/rule_attach/detect.py` → `logs/rule_attach_log.json`
- **Observability**: `tools/observability/aggregate.py` → `logs/observability/summary.{json,md}`

### 5. Documentation (`docs/`)
- **README**: Comprehensive framework documentation
- **ADRs**: Architecture Decision Records system
- **Contributing**: Development guidelines and standards

## 📁 File Structure

AdvancedRules/
├── .cursor/rules/ # AI framework rules and personas
│ ├── orchestrator/ # Core control systems
│ ├── roles/ # AI persona definitions
│ ├── domains/ # Domain-specific knowledge
│ ├── kits/ # Pre-start and Upwork automation
│ └── utilities/ # Framework utilities and tools
├── memory-bank/ # AI-generated artifacts and memory
├── src/ # Application source code
├── docs/ # Documentation and ADRs
└── package.json # Node.js project configuration


## ⚡ Operational Quickstart (Solo Freelancer Pipeline)

### 1) Prestart / Readiness
```bash
python3 tools/prestart/prestart_composite.py
```
Ensures `memory-bank/upwork/offer_status.json` exists and prints preflight status.

### 2) Minimal happy path
```bash
python3 tools/quickstart.py
```
Runs: readiness → product owner → planning → audit → PE peer review → PE synthesis.

### 3) Manual steps (if preferred)
```bash
# Prepare client brief
mkdir -p memory-bank/plan
printf "Client brief" > memory-bank/plan/client_brief.md

# Roles
python3 tools/run_role.py product_owner_ai
python3 tools/run_role.py planning_ai
python3 tools/run_role.py auditor_ai
python3 tools/run_role.py principal_engineer_ai --mode PEER_REVIEW
python3 tools/run_role.py principal_engineer_ai --mode SYNTHESIS
```

### 4) Decision Scoring v3 and Trigger
```bash
# Score candidates (prints decision, trace, optional shadow)
python3 tools/decision_scoring/advanced_score.py

# Trigger next step from scorer result (dry-run prints mapped command)
python3 tools/orchestrator/trigger_next.py --dry-run --candidates tools/decision_scoring/examples/trigger_candidates.json
```

### 5) Govern, Validate, Observe
```bash
# Governance policy checks
python3 tools/rules/validate.py

# Artifact schema checks
python3 tools/schema/validate_artifacts.py

# Observability summary
python3 tools/observability/aggregate.py && sed -n '1,120p' logs/observability/summary.md
```

### 6) Provenance and Rule Attach
```bash
# Provenance index (auto-written on artifact emits)
cat memory-bank/artifacts_index.json

# Deterministic attach log
python3 tools/rule_attach/detect.py --dry-run
python3 tools/rule_attach/detect.py && head -n 1 logs/rule_attach_log.json
```

## 🎯 What’s Included vs Deferred
- Included: governance validator, role rules (guards), registry (tightened), runner plugins, readiness, decision scoring v3, trigger, state engine, provenance, attach log, observability, schemas, quickstart, tests.
- Deferred (by choice): CI tests on PRs (only validator runs in CI until you port to your main repo).

## 🔧 Rules File Format

### YAML Frontmatter Structure

Every `.mdc` rules file follows this standardized format:

```yaml
---
title: "Technology Name — v1"
description: "Brief description of what the rules cover"
globs: ["**/*.ext", "src/**/*.ext", "components/**/*.ext"]
alwaysApply: false
priority: high
---
```

### Field Explanations

#### 1. `title`
- **Purpose**: Human-readable name for the rules file
- **Format**: String with version number
- **Example**: `"React Best Practices — v1"`
- **Usage**: Shows in UI, documentation, and rule selection

#### 2. `description`
- **Purpose**: Brief explanation of what the rules cover
- **Format**: Short descriptive string
- **Example**: `"React best practices and patterns for modern web applications"`
- **Usage**: Helps users understand rule scope

#### 3. `globs`
- **Purpose**: File patterns where these rules should apply
- **Format**: Array of glob patterns
- **Example**: `["**/*.tsx", "**/*.jsx", "components/**/*"]`
- **Usage**: Tells the system which files to apply rules to

**Common Glob Patterns:**
- `**/*.tsx` = All `.tsx` files anywhere
- `src/**/*.js` = All `.js` files in `src/` directory
- `components/**/*.{ts,tsx}` = All `.ts` and `.tsx` files in `components/`
- `**/*.{py,js,ts}` = All Python, JavaScript, and TypeScript files

#### 4. `alwaysApply`
- **Purpose**: Whether rules should always be active
- **Format**: Boolean (`true` or `false`)
- **Usage**: 
  - `true` = Rules always active (like base rules)
  - `false` = Rules only active when specifically selected

#### 5. `priority`
- **Purpose**: Importance level of the rules
- **Format**: String (`low`, `medium`, `high`)
- **Usage**: Determines rule precedence and activation order

### Example Rules Files

#### Frontend Rules
```yaml
---
title: "React Best Practices — v1"
description: "React best practices and patterns for modern web applications"
globs: ["**/*.tsx", "**/*.jsx", "components/**/*"]
alwaysApply: false
priority: high
---
```

#### Backend Rules
```yaml
---
title: "C# .NET Development — v1"
description: "C# and .NET development with best practices and patterns"
globs: ["**/*.cs", "**/*.csproj", "**/*.sln"]
alwaysApply: false
priority: high
---
```

#### Utility Rules
```yaml
---
title: "TypeScript Best Practices — v1"
description: "TypeScript coding standards and best practices for modern web development"
globs: ["**/*.ts", "**/*.tsx", "**/*.d.ts"]
alwaysApply: false
priority: medium
---
```

## 🚀 Framework Capabilities

### Development Workflow
1. **Requirement Analysis**: Product Owner AI creates user stories
2. **Technical Planning**: Planning AI develops project roadmap
3. **Architecture Design**: Principal Engineer AI establishes technical standards
4. **Code Generation**: Codegen AI implements features
5. **Quality Assurance**: QA AI and Security AI validate code
6. **Compliance Audit**: Auditor AI ensures standards compliance
7. **Documentation**: Documentation AI maintains comprehensive docs

### Quality Standards
- **Security First**: All code undergoes security review
- **Clean Code**: Follows established coding standards and patterns
- **Testing Coverage**: Comprehensive testing strategies
- **Performance Optimization**: Built-in performance considerations
- **Accessibility**: WCAG compliance standards

## 📊 Technology Coverage

### �� **Backend Domain (11 technologies)**
- **Languages**: C++, Go, Java, Python, Rust
- **Frameworks**: FastAPI, Laravel, Node.js/Express, WordPress, C#/.NET, Convex

### 🎨 **Frontend Domain (9 technologies)**
- **Frameworks**: React, Vue, Svelte, SolidJS, Qwik, Next.js
- **CSS**: Tailwind CSS
- **Enhancement**: HTMX
- **Standards**: Universal Coding Standards

### �� **Mobile Domain (4 technologies)**
- **Native**: Android
- **Cross-Platform**: Flutter, React Native, NativeScript

### 🔬 **Specialized Domain (3 technologies)**
- **AI/ML**: Machine learning, data science
- **Blockchain**: Smart contracts, DApps, Web3
- **DevOps**: Infrastructure, CI/CD, cloud deployment

### �� **Testing Domain (3 technologies)**
- **Unit Testing**: Jest (JS/TS), PHPUnit (PHP)
- **E2E Testing**: Playwright

### 🛠️ **Utilities Domain (8 technologies)**
- **Code Quality**: Clean code, quality standards, formatting
- **Development Tools**: Git, TypeScript, database design
- **Platform SDKs**: BeeFree (email), Medusa (e-commerce)
- **Effectiveness**: Rules effectiveness measurement system

## 🔒 Security & Compliance

### Built-in Security
- **Vulnerability Scanning**: Automated security checks
- **Compliance Validation**: Industry standard compliance
- **Access Control**: Role-based permissions
- **Audit Logging**: Complete activity tracking

### Standards Support
- **OWASP Top 10**: Web application security
- **ISO 27001**: Information security management
- **SOC 2**: Security, availability, confidentiality
- **GDPR/CCPA**: Data privacy compliance

## �� Performance & Scalability

### Optimization Features
- **Memory Management**: Efficient knowledge storage and retrieval
- **Parallel Processing**: Multi-persona concurrent execution
- **Caching Strategies**: Performance optimization
- **Resource Allocation**: Dynamic resource management

### Monitoring & Observability
- **Performance Metrics**: Real-time performance tracking
- **Quality Metrics**: Continuous quality monitoring
- **Execution Logs**: Complete workflow tracking
- **Alert Systems**: Proactive issue detection

## 🎭 AI Persona Integration

### Coordination Patterns
- **Sequential Execution**: Personas execute in strict order
- **Parallel Execution**: Compatible personas run simultaneously
- **Adaptive Execution**: Dynamic adjustment based on complexity

### Communication Protocols
- **Memory Bridge**: Shared knowledge and context
- **Quality Gates**: Validation checkpoints
- **Handoff Protocols**: Smooth transitions between personas
- **Audit Trails**: Complete decision tracking

## 🚀 Getting Started

### Prerequisites
- Git
- Node.js 18+ (for frontend development)
- Python 3.8+ (for backend development)
- Docker (for containerized development)

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd AdvancedRules

# Install dependencies
npm install
pip install -r requirements.txt

# Initialize the framework
npm run init
```

### Configuration
1. Copy `.env.example` to `.env`
2. Configure your AI service credentials
3. Set up your preferred development environment
4. Configure the Rules Master Toggle

## 🔧 Usage

### Basic Workflow
1. **Activate Framework**: Use Rules Master Toggle to activate personas
2. **Define Requirements**: Product Owner AI creates user stories
3. **Plan Development**: Planning AI creates project roadmap
4. **Generate Code**: Codegen AI implements features
5. **Validate Quality**: QA AI and Security AI validate code
6. **Deploy**: Auditor AI ensures compliance before deployment

### Quality Gates
- **PRE-START Gate**: Validates project readiness
- **Development Gate**: Ensures code quality during development
- **Security Gate**: Validates security compliance
- **Deployment Gate**: Final validation before deployment

## �� Documentation

### Framework Documentation
- **README**: This comprehensive overview
- **ADRs**: Architecture Decision Records
- **Contributing**: Development guidelines
- **API Reference**: Framework API documentation

### Rule Documentation
- **Technology Rules**: Domain-specific best practices
- **Coding Standards**: Universal development standards
- **Quality Guidelines**: Quality assurance procedures
- **Security Standards**: Security and compliance requirements

## 🤝 Contributing

### Adding New Rules
1. Create new `.mdc` file in appropriate domain directory
2. Follow YAML frontmatter format
3. Include comprehensive rule content
4. Update this README with new technology
5. Test rule effectiveness

### Rule Format Requirements
- **YAML Frontmatter**: Must include all required fields
- **Content Structure**: Use consistent markdown formatting
- **Examples**: Include practical code examples
- **Best Practices**: Cover comprehensive guidelines

## 📊 Monitoring & Effectiveness

### Rules Effectiveness Measurement
- **Code Quality Metrics**: Standards compliance, completeness
- **Process Metrics**: Planning, implementation, testing quality
- **Adoption Metrics**: Rule usage, framework integration
- **Continuous Improvement**: Regular assessment and optimization

### Quality Assurance
- **Automated Testing**: Code analysis, quality checks
- **Manual Validation**: Peer review, quality audits
- **Performance Monitoring**: Metrics tracking, trend analysis
- **Feedback Loops**: Developer input, improvement cycles

## 🎯 Use Cases

### Software Development
- **Full-Stack Applications**: Complete application development
- **API Development**: Backend service creation
- **Mobile Applications**: Cross-platform mobile development
- **Legacy Modernization**: System upgrade and migration

### Quality Assurance
- **Code Review**: Automated quality validation
- **Security Auditing**: Vulnerability assessment
- **Performance Testing**: Optimization and benchmarking
- **Compliance Validation**: Standards and regulatory compliance

### Project Management
- **Requirement Analysis**: User story creation and validation
- **Project Planning**: Roadmap development and tracking
- **Risk Assessment**: Identification and mitigation strategies
- **Resource Allocation**: Team and technology optimization

## 🔮 Future Roadmap

### Planned Enhancements
- **AI Model Integration**: Advanced AI model support
- **Cloud Integration**: Multi-cloud deployment support
- **Enterprise Features**: Advanced security and compliance
- **Community Edition**: Open-source community version

### Technology Expansion
- **Emerging Technologies**: AI/ML, blockchain, quantum computing
- **Industry Standards**: Healthcare, finance, automotive
- **Regional Compliance**: GDPR, CCPA, regional regulations
- **Performance Optimization**: Advanced caching and optimization

## 📞 Support & Community

### Getting Help
- **Documentation**: Comprehensive framework documentation
- **Examples**: Practical implementation examples
- **Community**: Developer community and forums
- **Support**: Enterprise support and consulting

### Contributing
- **Code Contributions**: Framework improvements and extensions
- **Rule Contributions**: New technology rules and standards
- **Documentation**: Documentation improvements and examples
- **Testing**: Framework testing and validation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## �� Acknowledgments

- **AdvancedRules Team**: Core framework development
- **Open Source Community**: Contributing technologies and standards
- **Industry Partners**: Best practices and compliance standards
- **Developer Community**: Feedback and improvement suggestions

---

**AdvancedRules Framework** - Empowering AI-driven software development excellence! 🚀

*For more information, visit our [documentation](docs/) or [contribute](CONTRIBUTING.md) to the project.*