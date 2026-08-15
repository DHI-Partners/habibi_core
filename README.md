### Habibi Core

Customization layer on top of ERPNext. Everything we change about stock ERPNext behaviour
belongs here — custom fields, document events, overridden classes, reports, print formats —
so that the `erpnext` fork stays as close to upstream as possible.

Where a change goes:

| | |
| --- | --- |
| **habibi_core** (this app) | anything reachable from `hooks.py`: `doc_events`, `override_doctype_class`, `override_whitelisted_methods`, custom fields as fixtures, new DocTypes, reports, client scripts |
| **[habibi-erp](https://github.com/DHI-Partners/habibi-erp)** (fork of erpnext) | only what hooks cannot reach: SQL inside stock reports, `.js` of core forms, schema changes to stock DocTypes |
| **[saas_bridge](https://github.com/DHI-Partners/saas_bridge)** | the control plane: provisioning client sites, plans and role profiles, the telephony webhook |

The fork is the expensive option — every upstream release has to be merged by hand — so
reach for it only after checking that no hook covers the case.

### Installation

The app is baked into the `habibi:16` image: it is listed in `habibi/apps.json` of
[habibi_docker](https://github.com/DHI-Partners/habibi_docker) and pulled from GitHub at
build time, so nothing is installed on the server by hand. On a site:

```bash
bench --site <site> install-app habibi_core
```

For local development see `habibi/dev-setup.md` in habibi_docker:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch version-16
bench --site <site> install-app habibi_core
```

### User limit

A site can be held to a number of users. The limit is not stored in the site's database —
it comes from its `site_config.json`, written there by
[saas_bridge](https://github.com/DHI-Partners/saas_bridge):

```json
{"saas_bridge_max_users": 10}
```

That split is the point of the design. This app enforces a number and does not care where
it came from — a decision, a plan, a billing service later on. A tenant's own System
Manager can edit anything inside their database, permissions included, but has no way to
reach `site_config.json`, and a limit the limited party can raise is not a limit. Raising
someone's limit is then a config write rather than a deployment to every site.

`habibi_core/limits.py` hooks `User.validate` (see `doc_events`). A seat is an **enabled
System User**: `Guest` never counts, `Administrator` does — it is a working login whose
password is handed out when the site is created. Portal users are free, since frappe
derives `user_type` from roles in `User.validate` and only desk access makes a System User.

The hook runs on `validate` rather than `before_insert`, and also fires when `enabled` or
`user_type` changes. That closes the two ways around a limit that take two steps: create a
disabled user and enable them later, or create a free portal user and then grant them a
desk role. It stands aside during install, migrate, patch and import, so a site is never
left half-built because of a limit.

With a limit set, `bootinfo.habibi_limits` carries `max_users` and `used_users` for the
interface to show. Without one the key is absent and nothing is enforced.

One deployment note. Frappe caches each site's resolved hooks in redis, so a site that
cached them before this app carried `limits.py` keeps creating users past its limit until
something clears that cache — `bench --site <site> migrate` (which the deploy job already
runs) or `bench --site <site> clear-cache`. `saas_bridge.api.set_site_limits` clears it for
the site it writes to, so setting a limit through the panel is enough on its own.

Tests: `habibi_core/tests/test_limits.py`, run on a throwaway site as usual —
`bench --site <test-site> run-tests --module habibi_core.tests.test_limits`.

### Branch

`version-16` — the branch tracks the framework version, not the app's own version. When the
bench moves to v17 a `version-17` branch is cut and `apps.json` switches to it.

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/habibi_core
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### License

mit
