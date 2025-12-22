# Ticket 006: CI Caching for Faster Workflows

## Summary

Optimise CI workflow performance by caching Node.js dependencies and environment setup.

## Acceptance Criteria

- [ ] Cache `node_modules` between workflow runs
- [ ] Cache npm global packages if needed
- [ ] Use `actions/setup-node` built-in caching
- [ ] Workflow should skip `npm install` when cache hit
- [ ] Document cache invalidation strategy

## Technical Notes

```yaml
- name: Setup Node.js
  uses: actions/setup-node@v4
  with:
    node-version-file: '.nvmrc'
    cache: 'npm'
```

The `cache: 'npm'` option will automatically cache based on `package-lock.json`. Since we're ignoring `package-lock.json`, we may need to use a custom cache key based on `package.json` hash instead:

```yaml
- name: Cache node_modules
  uses: actions/cache@v4
  with:
    path: node_modules
    key: ${{ runner.os }}-node-${{ hashFiles('package.json') }}
    restore-keys: |
      ${{ runner.os }}-node-
```

## Dependencies

- 001-003-A (Agent SDK script)
