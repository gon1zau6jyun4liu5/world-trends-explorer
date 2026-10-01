# Code Review Rules

## Data sources and recovery
- Keep Google search trends and GDELT publisher-country news clearly distinguished. A provider failure must not be presented as a successful empty feed or erase the last successful data.
- Check retry deadlines and provider-wide throttling across countries. Polling during cooldown must not postpone recovery, and bootstrap must not trigger upstream requests.

## Access and persistence
- All remote assets and API routes must pass the existing portal authentication. Mutations also require matching Origin and CSRF; keep local credentials and SQLite data out of Git.
- Preserve saved topics, display preferences and cached news across reloads; do not claim cached data is current. Do not merge a PR unless the user explicitly requests it.
