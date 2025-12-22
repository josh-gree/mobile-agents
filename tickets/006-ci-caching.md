# Ticket 006: CI Caching for Faster Workflows

## Summary

Optimise CI workflow performance by caching Node.js dependencies and environment setup.

## Acceptance Criteria

- [x] Cache `node_modules` between workflow runs
- [x] Cache npm global packages if needed (not applicable - no global packages used)
- [x] Use `actions/setup-node` built-in caching (skipped - requires package-lock.json which we don't commit)
- [x] Workflow should skip `npm install` when cache hit
- [x] Document cache invalidation strategy

## Implementation

Implemented in PR #38. Uses `actions/cache@v4` with a custom cache key based on `package.json` hash.

## Cache Invalidation Strategy

The cache key is: `${{ runner.os }}-node-${{ hashFiles('package.json') }}`

**Cache is invalidated when:**
1. `package.json` changes (dependency added/removed/updated)
2. Runner OS changes (e.g. ubuntu-latest image update that changes OS identifier)

**Fallback behaviour:**
- `restore-keys: ${{ runner.os }}-node-` allows partial cache restoration if exact match not found
- This means after a dependency change, the old cache may be restored and then `npm install` updates it

**Manual invalidation:**
- Clear via GitHub UI: Settings → Actions → Caches
- Or use `gh cache delete` CLI command

## Technical Notes

```yaml
- name: Cache node_modules
  uses: actions/cache@v4
  id: cache-node-modules
  with:
    path: node_modules
    key: ${{ runner.os }}-node-${{ hashFiles('package.json') }}
    restore-keys: |
      ${{ runner.os }}-node-

- name: Install dependencies
  if: steps.cache-node-modules.outputs.cache-hit != 'true'
  run: npm install
```

Note: We use `actions/cache` directly rather than `actions/setup-node`'s built-in caching because:
- We don't commit `package-lock.json` (allows minor version updates)
- Built-in caching requires package-lock.json for cache key

## Dependencies

- 001-003-A (Agent SDK script)
