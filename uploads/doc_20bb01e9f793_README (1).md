# Documentation Branching and Release Process

## Branching Strategy

### Main Branch
The *main* branch contains the latest working state of the documentation.

- Working and development branches may be merged into *main* **without review**.
- Contributors are expected to merge regularly.
- Long-lived branches are avoided to reduce merge conflicts.

### Feature Branches (`feature/<featurename>`)
Used for new documentation topics or improvements.

Workflow:
1. Create a feature branch from *main*.
2. Implement changes.
3. Merge back into *main* without review.

### Bugfix Branches (`bugfix/<bugname>`)
Used to fix issues for a specific release.

Workflow:
1. Branch from the appropriate release branch.
2. Implement the fix.
3. Merge into the release branch.
4. Cherry-pick into *main* if needed.

### Release Branches (`release-x.y` or versioned branches)
Release branches represent a frozen documentation state used for publication.

- Created from *main* at documentation freeze.
- Only reviewed changes are accepted.
- Branches stay open for patch releases.
- Fluid Topics publishes only from release branches.

## Release Train Process

1. Create a release branch (example: `release-1.2`).
2. Create a release candidate tag (example: `1.2.0-rc.0`).
3. Apply reviewed changes only.
4. Tag final release (example: `1.2.0`).
5. Patch flow:
   - Create bugfix branch.
   - Apply fix and review.
   - Merge into release branch.
   - Cherry-pick into *main*.
   - Tag patch (example: `1.2.1`).

## Working Agreements

### Merges to Main
- Working and dev branches may merge into *main* without review.
- Merge regularly to avoid drift.

### Changes to Release Branches
- All changes must be reviewed by the documentation team.

### Publishing
- All deployments to Fluid Topics are made from release branches.
- Release branches stay open for future updates.

## Summary

| Area | Policy |
|------|--------|
| Daily work | Merge working/dev branches into *main* without review |
| Release branches | Documentation team review required |
| Publishing | Only from release branches |
| Patch releases | Fix in release branch and cherry-pick into *main* |

