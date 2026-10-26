# Maintainer verification

These offline regression tests are for template maintainers. They are not a
student assessment, feedback feature, or course completion mechanism. There is
no GitHub Actions workflow and no integration with site progress.

From the standalone project root after installing requirements:

```sh
python -m unittest discover -s maintainer_tests -v
```

Tests simulate provider calls, use temporary databases, and import solution
snapshots. They cover basic distribution imports, no-key starter chat, storage,
user separation, tool calls/signature preservation, loop limits, webhook
verification, asynchronous acknowledgement, deduplication and cached retry.
No live model or Meta access is verified. Before publication, also complete the
fresh-account checklist in docs/free_tier_limits.md.
