#!/bin/bash
# Setup branch protection rules via GitHub API
# Usage: ./setup_branch_protection.sh <github_token> <owner> <repo>

set -e

GITHUB_TOKEN=${1:-$GITHUB_TOKEN}
OWNER=${2:-"HaymayndzUltra"}
REPO=${3:-"AdvancedRules"}

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ Error: GitHub token required"
    echo "Usage: $0 <github_token> [owner] [repo]"
    echo "Or set GITHUB_TOKEN environment variable"
    exit 1
fi

echo "🔧 Setting up branch protection for $OWNER/$REPO"

# Function to apply branch protection
apply_protection() {
    local BRANCH=$1
    local PAYLOAD=$2
    
    echo "  → Protecting branch: $BRANCH"
    
    curl -X PUT \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        "https://api.github.com/repos/$OWNER/$REPO/branches/$BRANCH/protection" \
        -d "$PAYLOAD" \
        -s -o /dev/null -w "%{http_code}"
}

# Main branch protection
MAIN_PROTECTION='{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "CI Pipeline / Lint Code",
      "CI Pipeline / Run Tests (3.11)",
      "CI Pipeline / Validate Schemas and Registry",
      "Governance & Quality Gates / Registry Validation",
      "Governance & Quality Gates / Gate Evaluator Smoke Test",
      "Governance & Quality Gates / Scoring Pipeline Validation",
      "Governance & Quality Gates / Artifact Audit & Provenance",
      "Governance & Quality Gates / Instrumentation & Redaction",
      "Governance & Quality Gates / End-to-End Orchestration Test"
    ]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true,
  "required_linear_history": false,
  "allow_fork_syncing": false
}'

# Develop branch protection
DEVELOP_PROTECTION='{
  "required_status_checks": {
    "strict": false,
    "contexts": [
      "CI Pipeline / Lint Code",
      "CI Pipeline / Run Tests (3.11)",
      "CI Pipeline / Validate Schemas and Registry"
    ]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": false,
    "require_code_owner_reviews": false
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": false,
  "required_linear_history": false,
  "allow_fork_syncing": false
}'

# Apply protections
echo "📋 Applying branch protection rules..."

# Check if main branch exists
if git ls-remote --heads origin main | grep -q main; then
    STATUS=$(apply_protection "main" "$MAIN_PROTECTION")
    if [ "$STATUS" = "200" ] || [ "$STATUS" = "201" ]; then
        echo "  ✅ Main branch protected"
    else
        echo "  ⚠️  Main branch protection failed (HTTP $STATUS)"
    fi
else
    echo "  ⏭️  Main branch doesn't exist, skipping"
fi

# Check if develop branch exists
if git ls-remote --heads origin develop | grep -q develop; then
    STATUS=$(apply_protection "develop" "$DEVELOP_PROTECTION")
    if [ "$STATUS" = "200" ] || [ "$STATUS" = "201" ]; then
        echo "  ✅ Develop branch protected"
    else
        echo "  ⚠️  Develop branch protection failed (HTTP $STATUS)"
    fi
else
    echo "  ⏭️  Develop branch doesn't exist, skipping"
fi

echo ""
echo "✨ Branch protection setup complete!"
echo ""
echo "📝 Note: Cursor branches (cursor/**) should have relaxed rules"
echo "   These can be configured manually in GitHub settings for pattern matching"
echo ""
echo "🔗 View settings at: https://github.com/$OWNER/$REPO/settings/branches"