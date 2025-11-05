# GitHub PR Update Commands

## Option 1: Using GitHub Web Interface (Recommended)

1. Go to: https://github.com/Sivivatu/ayx-rag/pulls
2. Find the PR for branch `002-sitemap-download`
3. Click "Edit" on the PR description
4. Copy content from `PR_DESCRIPTION.md` and paste into PR description
5. Scroll to bottom and uncheck "Draft" if checked
6. Click "Ready for review" button
7. Save changes

## Option 2: Using GitHub CLI (if authenticated)

```bash
# First, authenticate with GitHub
gh auth login

# Find the PR number
gh pr list --head 002-sitemap-download

# Update PR to ready for review (replace NUMBER with actual PR number)
gh pr ready NUMBER

# Update PR description (replace NUMBER with actual PR number)
gh pr edit NUMBER --body-file PR_DESCRIPTION.md

# Or update interactively
gh pr edit NUMBER
```

## Option 3: Create New PR (if none exists)

```bash
# Authenticate first
gh auth login

# Create PR with description
gh pr create \
  --title "feat(sitemap-download): add production-ready sitemap downloader v0.2.0" \
  --body-file PR_DESCRIPTION.md \
  --base main \
  --head 002-sitemap-download

# Or create interactively
gh pr create --web
```

## Quick Summary for PR

**Title**: 
```
feat(sitemap-download): add production-ready sitemap downloader v0.2.0
```

**Labels to Add**:
- `feature`
- `documentation`
- `ready-for-review`

**Reviewers**: (Add appropriate reviewers)

**Milestone**: v0.2.0 (if exists)

## PR Metrics Summary (for comments)

```markdown
### 📊 Final Metrics
- **Test Coverage**: 88% (exceeds 80% requirement) ✅
- **Tests**: 67 passing (56 unit + 11 integration)
- **Commits**: 26 conventional commits
- **Documentation**: Complete (README, CHANGELOG, release notes)
- **Constitution**: All 9 principles satisfied ✅
- **Status**: Ready for merge 🚀
```
