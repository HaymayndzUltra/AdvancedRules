# Framework Memory Bridge
# Persistent memory management for AdvancedRules AI framework

## Purpose
Provides seamless access to persistent memory storage, enabling AI personas to maintain context across sessions and share knowledge.

## Core Features
- **Context Persistence**: Store and retrieve conversation context, decisions, and artifacts
- **Knowledge Sharing**: Enable personas to access and contribute to shared knowledge base
- **Memory Compression**: Efficient storage and retrieval of large context objects
- **Version Control**: Track changes to memory objects with full audit trail
- **Cross-Persona Communication**: Facilitate information exchange between different AI roles

## Memory Types
```yaml
memory_categories:
  context:
    - conversation_history
    - user_preferences
    - session_state
  
  knowledge:
    - domain_expertise
    - best_practices
    - learned_patterns
  
  artifacts:
    - generated_code
    - design_documents
    - test_results
  
  metadata:
    - creation_timestamps
    - access_patterns
    - relevance_scores
```

## API Interface
```typescript
interface MemoryBridge {
  store(key: string, value: any, metadata?: MemoryMetadata): Promise<void>;
  retrieve(key: string): Promise<any>;
  search(query: string, filters?: SearchFilters): Promise<SearchResult[]>;
  update(key: string, value: any): Promise<void>;
  delete(key: string): Promise<void>;
  archive(key: string): Promise<void>;
}
```

## Integration
- Connects to memory-bank directory structure
- Provides RESTful API for external access
- Supports multiple storage backends (file, database, cloud)
- Implements caching for performance optimization
description:
globs:
alwaysApply: true
---
