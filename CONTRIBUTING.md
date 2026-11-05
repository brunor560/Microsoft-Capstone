# Contributing

All changes reach the base branch through a pull request that passes the
`pr-gate` check. The gate enforces every rule below.

## Branches

- Your **base branch** is the branch this project was cloned from. Its name
  ends in `/main`, for example `bench008/team-run01/main`.
- Create a new branch from it for your work. Name it with the same prefix
  and a short description: `bench008/team-run01/add-stats`.
- Never push to the base branch directly, never force-push, and don't touch
  any branch outside your prefix.

## Pull requests

- Open the pull request **into the base branch**.
- **Title:** [Conventional Commits](https://www.conventionalcommits.org/)
  style: a type, an optional scope, a colon and a short summary, for example
  `feat: add todo statistics` or `fix(api): reject blank titles`. Allowed
  types: `feat`, `fix`, `test`, `docs`, `refactor`, `chore`.
- **Description:** must contain these two sections:

  ```markdown
  ## Requirements
  - REQ-01: ...one line on how it is met
  - REQ-02: ...

  ## Testing
  What you ran and the results.
  ```

  List every requirement ID the pull request implements.
- `npm test` in `app/` must pass.
- Merge only after `pr-gate` has passed on the latest commit of the pull
  request.

## Protected files

Don't change anything under `.github/` or this file. The gate and these
rules are owned by the maintainers.

## Secrets

Never commit tokens, keys or `.env` files, and never paste them into pull
request text or comments.
