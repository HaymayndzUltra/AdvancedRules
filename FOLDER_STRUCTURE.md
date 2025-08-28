# AdvancedRules Project Structure

```
AdvancedRules/
├── README.md                          # Project overview and documentation
├── .cursor/                           # Cursor IDE configuration
│   └── rules/                         # AdvancedRules framework rules
│       ├── advanced/                  # Advanced rule configurations
│       │   └── typescript-base.mdc   # TypeScript base rules
│       ├── domains/                   # Domain-specific rules
│       │   ├── backend/               # Backend development rules (12 technologies)
│       │   │   ├── convex.mdc        # Convex backend-as-a-service
│       │   │   ├── csharp-dotnet.mdc # C# .NET development
│       │   │   ├── cpp.mdc           # C++ development
│       │   │   ├── fastapi.mdc       # FastAPI Python framework
│       │   │   ├── go.mdc            # Go language
│       │   │   ├── java.mdc          # Java development
│       │   │   ├── laravel.mdc       # Laravel PHP framework
│       │   │   ├── node-express.mdc  # Node.js + Express
│       │   │   ├── python.mdc        # Python development
│       │   │   ├── rust.mdc          # Rust language
│       │   │   └── wordpress.mdc     # WordPress development
│       │   ├── frontend/              # Frontend development rules (9 technologies)
│       │   │   ├── coding-standards.mdc # Universal coding standards
│       │   │   ├── htmx.mdc          # HTMX (HTML extensions)
│       │   │   ├── nextjs.mdc        # Next.js React framework
│       │   │   ├── qwik.mdc          # Qwik framework
│       │   │   ├── react.mdc         # React library
│       │   │   ├── solidjs.mdc       # SolidJS framework
│       │   │   ├── svelte.mdc        # Svelte framework
│       │   │   ├── tailwind.mdc      # Tailwind CSS framework
│       │   │   └── vue.mdc           # Vue.js framework
│       │   ├── mobile/                # Mobile development rules (4 technologies)
│       │   │   ├── android.mdc       # Android native development
│       │   │   ├── flutter.mdc       # Flutter cross-platform
│       │   │   ├── nativescript.mdc  # NativeScript framework
│       │   │   └── react-native.mdc  # React Native cross-platform
│       │   ├── specialized/           # Specialized technology rules (3 technologies)
│       │   │   ├── ai-ml.mdc         # AI & Machine Learning
│       │   │   ├── blockchain.mdc    # Blockchain development
│       │   │   └── devops.mdc        # DevOps & infrastructure
│       │   ├── testing/               # Testing framework rules (3 technologies)
│       │   │   ├── jest.mdc          # Jest JavaScript testing
│       │   │   ├── phpunit.mdc       # PHPUnit PHP testing
│       │   │   └── playwright.mdc    # Playwright E2E testing
│       │   └── utilities/             # Development utilities rules (9 technologies)
│       │       ├── beefreeSDK.mdc    # BeeFree SDK integration
│       │       ├── clean-code.mdc    # Clean code principles
│       │       ├── codequality.mdc   # Code quality standards
│       │       ├── database.mdc      # Database design & management
│       │       ├── gitflow.mdc       # Git workflow strategies
│       │       ├── medusa.mdc        # Medusa e-commerce platform
│       │       ├── rules-effectiveness.mdc # Rules effectiveness measurement
│       │       ├── typescript.mdc    # TypeScript language
│       │       └── unified-code-formatting.mdc # Code formatting standards
│       ├── indexes/                   # Rule indexing and search
│       │   ├── frameworks.index.yaml  # Framework index
│       │   └── roles.index.yaml       # Roles index
│       ├── kits/                      # Pre-packaged rule kits
│       │   ├── prestart/              # PRE-START phase kits (9 kits)
│       │   │   ├── capacity_planner.mdc
│       │   │   ├── client_screener.mdc
│       │   │   ├── demo_playbook.mdc
│       │   │   ├── estimate_sizer.mdc
│       │   │   ├── pricing_policy.mdc
│       │   │   ├── proposal_builder.mdc
│       │   │   ├── repo_bootstrapper.mdc
│       │   │   ├── risk_catalog.mdc
│       │   │   └── scope_guard.mdc
│       │   └── upwork/                # Upwork-specific kits (3 kits)
│       │       ├── connects_policy.mdc
│       │       ├── contract_guard.mdc
│       │       └── upwork_adapter.mdc
│       ├── orchestrator/              # Rule orchestration logic
│       │   ├── execution_orchestrator.md
│       │   ├── framework_memory_bridge.md
│       │   └── rules_master_toggle.md
│       ├── roles/                     # Role-based rule sets
│       │   ├── auditor_ai.md
│       │   ├── codegen_ai.md
│       │   ├── documentation_ai.md
│       │   ├── planning_ai.md
│       │   ├── principal_engineer_ai.md
│       │   ├── product_owner_ai.md
│       │   ├── qa_ai.md
│       │   └── security_ai.md
│       ├── templates/                 # Rule templates
│       │   ├── change_request.md
│       │   ├── estimate.matrix.yaml
│       │   ├── pricing.ratecard.yaml
│       │   ├── contracts/             # Contract templates
│       │   │   ├── msa_template.md
│       │   │   └── sow_template.md
│       │   └── proposal/              # Proposal templates
│       │       └── proposal.md
│       ├── orchestrator.mdc           # Main orchestrator rule
│       ├── globals.md                 # Global rule definitions
│       └── readiness_check.mdc        # PRE-START acceptance gate
│
├── docs/                              # Documentation
│   ├── README.md                      # Documentation overview
│   └── ADRs/                         # Architecture Decision Records
│       └── README.md                  # ADR documentation
│
├── memory-bank/                       # Project memory and artifacts
│   ├── business/                      # Business-related artifacts
│   │   ├── capacity_report.md         # Team capacity report
│   │   ├── client_score.json          # Client fit assessment
│   │   ├── estimate_brief.md          # Project estimation
│   │   ├── pricing.ratecard.yaml      # Pricing structure
│   │   └── red_flags.md               # Client red flags
│   ├── checklists/                    # Project checklists
│   │   ├── prestart-master-checklist.md # PRE-START checklist
│   │   └── prestart-runbook.md        # PRE-START execution guide
│   ├── logs/                          # Project logs and history
│   ├── plan/                          # Planning artifacts
│   │   ├── client_brief.md            # Client brief document
│   │   └── proposal.md                # Client proposal
│   ├── reports/                       # Project reports
│   └── upwork/                        # Upwork-specific artifacts
│       └── offer_status.json          # Upwork offer status
│
├── scripts/                           # Utility scripts
│   └── validate_prestart.sh           # PRE-START validation script
│
├── src/                               # Source code (if applicable)
│   ├── backend/                       # Backend source code
│   ├── frontend/                      # Frontend source code
│   └── tests/                         # Test files
│
├── templates/                         # Project templates
│   └── upwork/                        # Upwork-specific templates
│
└── FRAMEWORK_SUMMARY.md               # Framework implementation summary
```

## Technology Coverage Summary

### 🎯 **Backend Domain (12 technologies)**
- **Languages**: C++, Go, Java, Python, Rust, C#
- **Frameworks**: FastAPI, Laravel, Node.js/Express, WordPress, Convex
- **Platforms**: .NET

### 🎨 **Frontend Domain (9 technologies)**
- **Frameworks**: React, Vue, Svelte, SolidJS, Qwik, Next.js
- **CSS**: Tailwind CSS
- **Enhancement**: HTMX
- **Standards**: Universal Coding Standards

### 📱 **Mobile Domain (4 technologies)**
- **Native**: Android
- **Cross-Platform**: Flutter, React Native, NativeScript

### 🔬 **Specialized Domain (3 technologies)**
- **AI/ML**: Machine learning, data science
- **Blockchain**: Smart contracts, DApps, Web3
- **DevOps**: Infrastructure, CI/CD, cloud deployment

### 🧪 **Testing Domain (3 technologies)**
- **Unit Testing**: Jest (JS/TS), PHPUnit (PHP)
- **E2E Testing**: Playwright

### 🛠️ **Utilities Domain (9 technologies)**
- **Code Quality**: Clean code, quality standards, formatting, rules effectiveness
- **Development Tools**: Git, TypeScript, database design
- **Platform SDKs**: BeeFree (email), Medusa (e-commerce)

## Key Directories

### 🎯 **`.cursor/rules/`** - AdvancedRules Framework
- **`domains/`** - 40 technology-specific rule sets
- **`kits/prestart/`** - PRE-START phase automation
- **`kits/upwork/`** - Upwork platform integration
- **`roles/`** - 8 AI persona definitions
- **`orchestrator/`** - Core coordination systems
- **`templates/`** - Contract and proposal templates
- **`indexes/`** - Rule indexing and search system
- **`advanced/`** - Advanced rule configurations
- **`readiness_check.mdc`** - PRE-START acceptance gate

### 🧠 **`memory-bank/`** - Project Artifacts
- **`business/`** - Core business documents
- **`checklists/`** - Project execution guides
- **`plan/`** - Planning and proposal documents
- **`upwork/`** - Upwork-specific files

### 📚 **`docs/`** - Documentation
- **`ADRs/`** - Architecture Decision Records

### 🛠️ **`scripts/`** - Automation Tools
- **`validate_prestart.sh`** - Quick PRE-START validation

## Current Status
✅ **PRE-START Phase Complete** - All required artifacts present  
✅ **Technology Coverage Complete** - 40 domain technologies loaded  
🚀 **Ready for `/preflight`** - Gate validation ready  
📋 **Next Phase** - Planning phase unlocked after validation

## Total Technology Coverage: 40 Technologies
- Backend: 12 ✅
- Frontend: 9 ✅
- Mobile: 4 ✅
- Specialized: 3 ✅
- Testing: 3 ✅
- Utilities: 9 ✅

The AdvancedRules framework is now a comprehensive, enterprise-grade development knowledge base covering the full spectrum of modern software development technologies and best practices! 🚀
