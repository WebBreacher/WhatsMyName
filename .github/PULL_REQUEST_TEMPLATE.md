## Type of change

- [ ] New site added to `wmn-data.json`
- [ ] Fix to an existing site entry (broken detection, updated URL, etc.)
- [ ] Other (docs, scripts, etc.)

## Checklist (for new or updated site entries)

- [ ] I tested `uri_check` against a real, existing account and confirmed `e_code`/`e_string` match
- [ ] I tested `uri_check` against a non-existent username and confirmed `m_code`/`m_string` match
- [ ] `e_string`/`m_string` are specific enough to avoid false positives/negatives (not too generic, not username-specific)
- [ ] The site is publicly accessible (no login/paywall) and the username appears directly in the profile URL
- [ ] My JSON is valid (the file will be auto-formatted/sorted and schema-validated by GitHub Actions)

## Description

<!-- What does this PR change, and why? -->
