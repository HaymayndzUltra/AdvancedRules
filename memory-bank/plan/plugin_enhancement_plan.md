# AdvancedRules Plugin Enhancement Plan

## Objective
Enhance the plugin system to dynamically generate content based on project type while maintaining system safety and architecture integrity.

## Current State Analysis

### Problems
1. **Static Templates**: Plugins use hardcoded templates regardless of project type
2. **Limited Keywords**: Only recognizes booking/portfolio keywords
3. **Minimal Brief Usage**: Only extracts title from client brief
4. **No Project Diversity**: Cannot handle AI, voice, mobile, or other project types

### System Constraints
- Must maintain idempotency (same input = same output)
- Must preserve safety-first approach
- Must work with existing state management
- Must maintain backward compatibility

## Enhancement Design

### Phase 1: Project Type Detection (Week 1)

#### 1.1 Create Project Detector Module
```python
# tools/runner/plugins/utils/project_detector.py
- Implement keyword-based detection
- Support extensible project types
- Return confidence scores
- Fallback to generic type
```

#### 1.2 Define Project Type Registry
```yaml
# config/project_types.yaml
project_types:
  voice_assistant:
    keywords: [voice, AI, speech, telephony, call]
    confidence_threshold: 0.7
    template_dir: voice_assistant
  
  web_application:
    keywords: [web, frontend, backend, API]
    confidence_threshold: 0.6
    template_dir: web_app
```

### Phase 2: Template System (Week 2)

#### 2.1 Create Template Structure
```
tools/runner/templates/
├── voice_assistant/
│   ├── product_backlog.yaml.j2
│   ├── acceptance_criteria.json.j2
│   ├── user_stories.md.j2
│   └── product_vision.md.j2
├── web_app/
├── mobile_app/
└── generic/
```

#### 2.2 Implement Template Engine
```python
# tools/runner/plugins/utils/template_engine.py
- Use Jinja2 for dynamic content
- Support conditional sections
- Variable substitution from parsed brief
- Maintain formatting standards
```

### Phase 3: Brief Parser Enhancement (Week 3)

#### 3.1 Structured Brief Parser
```python
# tools/runner/plugins/utils/brief_parser.py
class BriefParser:
    def parse(self, content: str) -> BriefData:
        return BriefData(
            title=self._extract_title(content),
            summary=self._extract_summary(content),
            goals=self._extract_goals(content),
            requirements=self._extract_requirements(content),
            timeline=self._extract_timeline(content),
            budget=self._extract_budget(content),
            project_type=self._detect_type(content)
        )
```

#### 3.2 Data Extraction Methods
- Use regex patterns for sections
- NLP for unstructured content
- Fallback defaults for missing data

### Phase 4: Plugin Updates (Week 4)

#### 4.1 Update product_owner.py
```python
def run() -> None:
    # Parse brief
    brief_data = BriefParser().parse(brief_content)
    
    # Detect project type
    project_type = ProjectDetector().detect(brief_data)
    
    # Load appropriate templates
    templates = TemplateEngine().load(project_type)
    
    # Generate artifacts
    backlog = templates.render('product_backlog', brief_data)
    write_text(MB / "plan/product_backlog.yaml", backlog)
```

#### 4.2 Update planning.py
- Similar pattern for task breakdown
- Use project-specific task templates
- Maintain existing structure

### Phase 5: Testing & Validation (Week 5)

#### 5.1 Test Cases
- Voice Assistant project
- Web Application project
- Mobile App project
- Generic/Unknown project
- Backward compatibility tests

#### 5.2 Validation Criteria
- Correct project type detection
- Appropriate template selection
- Dynamic content generation
- Idempotency maintained
- No regression in existing projects

## Implementation Steps

### Step 1: Create Enhancement Branch
```bash
git checkout -b feature/dynamic-plugin-content
```

### Step 2: Implement Project Detector
1. Create `project_detector.py`
2. Add keyword mappings
3. Implement confidence scoring
4. Add unit tests

### Step 3: Build Template System
1. Create template directories
2. Convert existing content to templates
3. Add project-specific templates
4. Test template rendering

### Step 4: Enhance Brief Parser
1. Create `brief_parser.py`
2. Implement section extractors
3. Add data validation
4. Create parser tests

### Step 5: Update Plugins
1. Modify `product_owner.py`
2. Modify `planning.py`
3. Update other affected plugins
4. Maintain backward compatibility

### Step 6: Integration Testing
1. Test with various project types
2. Verify idempotency
3. Check state management
4. Validate output quality

## Success Metrics
- Support for 5+ project types
- 90% accuracy in project detection
- Dynamic content generation
- Zero regression in existing functionality
- Maintained safety and idempotency

## Risk Mitigation
- Incremental implementation
- Feature flags for new functionality
- Comprehensive testing
- Rollback plan ready
- Documentation updates

## Timeline
- Week 1: Project detection
- Week 2: Template system
- Week 3: Brief parser
- Week 4: Plugin updates
- Week 5: Testing & deployment

## Next Actions
1. Review and approve plan
2. Create feature branch
3. Start with project detector implementation
4. Set up template structure