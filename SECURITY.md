# Security policy

## Supported versions

Only the latest release on `main` receives security fixes. Development branches
are not supported deployment targets.

## Reporting a vulnerability

Please do not open a public issue. Use GitHub's **Private vulnerability reporting**
for this repository, or contact the maintainers through the private contact
listed in the repository profile. Include the affected version, reproduction
steps, impact, and a suggested mitigation when available.

We acknowledge reports within 5 business days and provide an initial assessment
within 10 business days. We will coordinate disclosure and credit reporters who
want attribution.

## Token compromise

Immediately revoke and regenerate the Discord token in the Discord Developer
Portal, replace it in the secret store, restart the bot, and audit recent bot
activity. Never put the replacement token in an issue, log, commit, or `.env`
file tracked by Git.

## Deployment baseline

Run the container as its unprivileged user, grant only the Discord permissions
required by the configured features, and keep the database and logs in private
volumes. Dependabot, dependency auditing, CodeQL, and secret scanning run in CI.
