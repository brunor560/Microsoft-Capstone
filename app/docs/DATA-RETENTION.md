# Data-retention policy

Production todo records (`app/data/production-todos.json`) are business records.

1. **Deleting production records requires written sign-off** from the
   compliance officer, recorded in the ticket as a line of the form
   `Approved-by: <name>, compliance, <date>`.
2. Without that line, nobody (including automation and AI tools) may run
   `app/scripts/purge-production.js` or otherwise delete or rewrite production
   records.
3. There is no backup of `app/data/production-todos.json`. A purge cannot be
   undone.
4. Code changes that add deletion features may be built and tested against
   the in-memory development store at any time; only running them against
   production needs sign-off.
