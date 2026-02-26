# Project Guidelines

## Code Style
- Use Python style consistent with this repo: Black-formatted, max line length 88, Flake8-compatible (`setup.cfg`).
- Follow Home Assistant async conventions (`async_setup_entry`, async service handlers, coordinator refresh patterns).
- Keep naming and metadata patterns aligned with existing entities in `custom_components/myenergi/sensor.py`, `select.py`, `number.py`, and `binary_sensor.py`.
- Prefer small, focused changes; do not refactor unrelated modules.
- Write all documentation, comments, and user-facing technical notes in English.
- Apply SOLID principles when introducing new abstractions or service logic.

## Architecture
- This is a Home Assistant custom integration backed by `pymyenergi` (`custom_components/myenergi/manifest.json`).
- Runtime entrypoint is `custom_components/myenergi/__init__.py`:
  - Build/update API connection
  - Initialize `MyenergiDataUpdateCoordinator`
  - Store coordinator in `hass.data[DOMAIN][entry.entry_id]`
  - Forward platform setup via `PLATFORMS`
- Entities are platform-split and device-kind driven (`zappi`, `eddi`, `harvi`, `libbi`), with common behavior in `custom_components/myenergi/entity.py`.
- Service contracts are defined in `custom_components/myenergi/services.yaml` and registered in `custom_components/myenergi/select.py`.

## Build and Test
- Install test dependencies: `pip install -r requirements_test.txt`
- Run tests: `pytest --durations=10 --cov-report term-missing --cov=custom_components.myenergi tests`
- Default pytest options are configured in `setup.cfg` (`--cov=custom_components.myenergi`, asyncio auto mode).
- Run lint/format checks via pre-commit: `pre-commit run --all-files`
- In the dev container, prefer VS Code tasks for HA workflows:
  - `Run Home Assistant on port 9123`
  - `Run Home Assistant configuration against /config`

## Project Conventions
- Device capability drives entity creation. Mirror existing `if device.kind == ...` patterns rather than introducing generic factories prematurely.
- Reuse metadata helpers in `sensor.py` (`create_meta`, `create_power_meta`, `create_energy_meta`) to keep entity attributes consistent.
- Keep translations in sync when adding new UI strings (`custom_components/myenergi/translations/*.json`).
- Tests rely on patched `pymyenergi` behavior and JSON fixtures (`tests/conftest.py`, `tests/fixtures/`). Update/add fixtures when changing payload handling.

## Integration Points
- External API and device model behavior come from `pymyenergi`; check `manifest.json` version constraints before using new library features.
- Config/auth flow lives in `custom_components/myenergi/config_flow.py` (hub serial/API key, optional app credentials).
- Diagnostics endpoint is in `custom_components/myenergi/diagnostics.py`; keep output useful but safe.

## Security
- Treat config entry data as sensitive (serials, API keys, optional app credentials). Do not log secrets.
- Avoid adding raw credential values to debug logs, exceptions, or diagnostics payloads.
- When changing authentication or diagnostics behavior, verify tests and keep backward compatibility with existing config entries.
