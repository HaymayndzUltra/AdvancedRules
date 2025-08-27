# AdvancedRules Project Structure

```
AdvancedRules/
├── .cursor/                          # Cursor IDE configuration
│   └── rules/                        # AdvancedRules framework rules
│       ├── domains/                  # Domain-specific rules
│       │   ├── backend/              # Backend development rules (10 technologies)
│       │   │   ├── cpp.mdc          # C++ development
│       │   │   ├── fastapi.mdc      # FastAPI Python framework
│       │   │   ├── go.mdc           # Go language
│       │   │   ├── java.mdc         # Java development
│       │   │   ├── laravel.mdc      # Laravel PHP framework
│       │   │   ├── node-express.mdc # Node.js + Express
│       │   │   ├── python.mdc       # Python development
│       │   │   ├── rust.mdc         # Rust language
│       │   │   └── wordpress.mdc    # WordPress development
│       │   ├── frontend/             # Frontend development rules (8 technologies)
│       │   │   ├── htmx.mdc         # HTMX (HTML extensions)
│       │   │   ├── nextjs.mdc       # Next.js React framework
│       │   │   ├── qwik.mdc         # Qwik framework
│       │   │   ├── react.mdc        # React library
│       │   │   ├── solidjs.mdc      # SolidJS framework
│       │   │   ├── svelte.mdc       # Svelte framework
│       │   │   ├── tailwind.mdc     # Tailwind CSS framework
│       │   │   └── vue.mdc          # Vue.js framework
│       │   ├── mobile/               # Mobile development rules (4 technologies)
│       │   │   ├── android.mdc      # Android native development
│       │   │   ├── flutter.mdc      # Flutter cross-platform
│       │   │   ├── nativescript.mdc # NativeScript framework
│       │   │   └── react-native.mdc # React Native cross-platform
│       │   ├── specialized/          # Specialized technology rules (3 technologies)
│       │   │   ├── ai-ml.mdc        # AI & Machine Learning
│       │   │   ├── blockchain.mdc   # Blockchain development
│       │   │   └── devops.mdc       # DevOps & infrastructure
│       │   ├── testing/              # Testing framework rules (3 technologies)
│       │   │   ├── jest.mdc         # Jest JavaScript testing
│       │   │   ├── phpunit.mdc      # PHPUnit PHP testing
│       │   │   └── playwright.mdc   # Playwright E2E testing
│       │   └── utilities/            # Development utilities rules (8 technologies)
│       │       ├── beefreeSDK.mdc   # BeeFree SDK integration
│       │       ├── clean-code.mdc   # Clean code principles
│       │       ├── codequality.mdc  # Code quality standards
│       │       ├── database.mdc     # Database design & management
│       │       ├── gitflow.mdc      # Git workflow strategies
│       │       ├── medusa.mdc       # Medusa e-commerce platform
│       │       ├── typescript.mdc   # TypeScript language
│       │       └── unified-code-formatting.mdc # Code formatting standards
│       ├── indexes/                  # Rule indexing and search
│       ├── kits/                     # Pre-packaged rule kits
│       │   ├── prestart/             # PRE-START phase kits (9 kits)
│       │   │   ├── client_screener.mdc
│       │   │   ├── capacity_planner.mdc
│       │   │   ├── pricing_policy.mdc
│       │   │   ├── estimate_sizer.mdc
│       │   │   ├── proposal_builder.mdc
│       │   │   ├── demo_playbook.mdc
│       │   │   ├── repo_bootstrapper.mdc
│       │   │   ├── risk_catalog.mdc
│       │   │   └── scope_guard.mdc
│       │   └── upwork/               # Upwork-specific kits (3 kits)
│       │       ├── upwork_adapter.mdc
│       │       ├── contract_guard.mdc
│       │       └── connects_policy.mdc
│       ├── orchestrator/             # Rule orchestration logic
│       ├── roles/                    # Role-based rule sets
│       ├── templates/                # Rule templates
│       │   ├── contracts/            # Contract templates
│       │   └── proposal/             # Proposal templates
│       ├── orchestrator.mdc          # Main orchestrator rule
│       ├── globals.mdc               # Global rule definitions
│       └── readiness_check.mdc       # PRE-START acceptance gate
│
├── docs/                             # Documentation
│   └── ADRs/                        # Architecture Decision Records
│       └── README.md                 # ADR documentation
│
├── memory-bank/                      # Project memory and artifacts
│   ├── business/                     # Business-related artifacts
│   │   ├── client_score.json         # Client fit assessment
│   │   ├── capacity_report.md        # Team capacity report
│   │   ├── pricing.ratecard.yaml     # Pricing structure
│   │   ├── estimate_brief.md         # Project estimation
│   │   └── red_flags.md              # Client red flags
│   ├── checklists/                   # Project checklists
│   │   ├── prestart-master-checklist.md  # PRE-START checklist
│   │   └── prestart-runbook.md       # PRE-START execution guide
│   ├── logs/                         # Project logs and history
│   ├── plan/                         # Planning artifacts
│   │   └── proposal.md               # Client proposal
│   ├── reports/                      # Project reports
│   └── upwork/                       # Upwork-specific artifacts
│       ├── offer_status.json         # Upwork offer status
│       ├── cover_letter.md           # Upwork cover letter
│       ├── milestones.yaml           # Fixed-price milestones
│       └── hourly_scope.md           # Hourly scope definition
│
├── scripts/                          # Utility scripts
│   └── validate_prestart.sh          # PRE-START validation script
│
├── src/                              # Source code (if applicable)
│   ├── backend/                      # Backend source code
│   ├── frontend/                     # Frontend source code
│   └── tests/                        # Test files
│
└── templates/                        # Project templates
    └── upwork/                       # Upwork-specific templates
```

## Technology Coverage Summary

### 🎯 **Backend Domain (10 technologies)**
- **Languages**: C++, Go, Java, Python, Rust
- **Frameworks**: FastAPI, Laravel, Node.js/Express, WordPress

### 🎨 **Frontend Domain (8 technologies)**
- **Frameworks**: React, Vue, Svelte, SolidJS, Qwik, Next.js
- **CSS**: Tailwind CSS
- **Enhancement**: HTMX

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

### 🛠️ **Utilities Domain (8 technologies)**
- **Code Quality**: Clean code, quality standards, formatting
- **Development Tools**: Git, TypeScript, database design
- **Platform SDKs**: BeeFree (email), Medusa (e-commerce)

## Key Directories

### 🎯 **`.cursor/rules/`** - AdvancedRules Framework
- **`domains/`** - 36 technology-specific rule sets
- **`kits/prestart/`** - PRE-START phase automation
- **`kits/upwork/`** - Upwork platform integration
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
✅ **Technology Coverage Complete** - 36 domain technologies loaded  
🚀 **Ready for `/preflight`** - Gate validation ready  
📋 **Next Phase** - Planning phase unlocked after validation

## Total Technology Coverage: 36 Technologies
- Backend: 10 ✅
- Frontend: 8 ✅
- Mobile: 4 ✅
- Specialized: 3 ✅
- Testing: 3 ✅
- Utilities: 8 ✅

The AdvancedRules framework is now a comprehensive, enterprise-grade development knowledge base covering the full spectrum of modern software development technologies and best practices! 🚀
