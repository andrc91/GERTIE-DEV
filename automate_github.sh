#!/bin/bash
# GitHub Automation Script
# Run after: gh auth login

set -e

cd ~/Desktop/camera_system_incremental

echo "Creating pull request for documentation updates..."
gh pr create \
  --repo andrc1/GERTIE \
  --base main \
  --head update-documentation \
  --title "docs: Update README and add issue templates" \
  --body "Updates documentation with USB deployment workflow and P0 issue templates"

echo ""
echo "Merging pull request..."
gh pr merge update-documentation --repo andrc1/GERTIE --squash --delete-branch

echo ""
echo "Creating P0 issues..."

# Issue 1: WYSIWYG
gh issue create \
  --repo andrc1/GERTIE \
  --title "[P0] WYSIWYG: Preview aspect ratio doesn't match capture" \
  --label "P0-blocker,WYSIWYG,bug" \
  --body-file .github/ISSUE_TEMPLATE/p0-wysiwyg.md

# Issue 2: Time Sync
gh issue create \
  --repo andrc1/GERTIE \
  --title "[P0] Time sync: Cameras have different clock times" \
  --label "P0-blocker,system,enhancement" \
  --body-file .github/ISSUE_TEMPLATE/p0-time-sync.md

# Issue 3: Telemetry
gh issue create \
  --repo andrc1/GERTIE \
  --title "[P0] Telemetry: Need complete capture logging system" \
  --label "P0-blocker,logging,enhancement" \
  --body-file .github/ISSUE_TEMPLATE/p0-telemetry.md

# Issue 4: Lag
gh issue create \
  --repo andrc1/GERTIE \
  --title "[P0] Performance: 5-10 second lag on operations" \
  --label "P0-blocker,performance,bug" \
  --body-file .github/ISSUE_TEMPLATE/p0-lag-reduction.md

# Issue 5: Reliability
gh issue create \
  --repo andrc1/GERTIE \
  --title "[P0] Reliability: Random camera capture failures" \
  --label "P0-blocker,reliability,bug" \
  --body-file .github/ISSUE_TEMPLATE/p0-capture-reliability.md

echo ""
echo "✅ All GitHub tasks complete!"
echo "View issues: https://github.com/andrc1/GERTIE/issues"
