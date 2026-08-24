# Security policy

## Security posture

The v0.1 implementation is intentionally read-only and dependency-light.

- No credentials are required for the documented DREAM public API.
- No write operations to DREAM or any government system exist.
- The DREAM adapter permits only HTTPS requests to `public-api.dream.gov.ua`.
- Arbitrary upstream URLs are not accepted.
- Responses are size-limited before JSON parsing.
- Source text is data and is never executed as code or instructions.
- Canonical JSON hashing uses SHA-256 for evidence integrity identifiers; hashes are not claims of authorship or ownership.

## Secrets

Do not commit API tokens, private datasets, credentials, personal data obtained outside legitimate public sources, or privileged government records.

## Reporting a vulnerability

Please use GitHub's repository security-reporting mechanism if enabled, or contact the maintainer through the repository owner profile. Do not publish exploitable details before a fix is available.

## Scope boundary

A data inconsistency is not a security vulnerability by itself. Report security issues separately from integrity findings so that operational security and public-data analysis do not become conflated.
