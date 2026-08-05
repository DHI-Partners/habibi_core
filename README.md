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
