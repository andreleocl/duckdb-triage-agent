# Codex model metadata

Both model jobs use `gpt-5-mini`. Codex CLI 0.164.0 does not bundle
metadata for this alias, so this repository supplies a local catalogue.
The alias can change its underlying snapshot; record the returned model identity
when evaluating runs.

This is a project-maintained adaptation, not an official GPT-5 mini catalogue.
It uses the GPT-5 family entry from OpenAI Codex rust-v0.114.0:
https://github.com/openai/codex/blob/rust-v0.114.0/codex-rs/core/models.json
The source is Apache-2.0 licensed; see LICENSE.

The slug, display name and description identify the mini alias; the upgrade
suggestion is removed. The family instructions and conservative client defaults
are retained: minimal/low/medium/high reasoning, a 272,000-token working context,
no parallel tool calls and no native patch tool. The context cap is below the
model's documented 400,000-token limit. API capabilities and model identifiers are listed
in the [official model documentation](https://developers.openai.com/api/docs/models/gpt-5-mini).
These settings configure the client; they do not guarantee model quality or
account access. The documentation marks this model deprecated, so verify access
before an authorized live run.

Activation uploads this catalogue from the trusted workflow revision. Both
model jobs download it under `/tmp/gh-aw`, which is mounted inside their
containers. Neither job needs evaluation cases to load this file.

The triage job uses Codex's `model_catalog_json` configuration. The external
detector in gh-aw v0.93.5 ignores additional `engine.config` and regenerates its
own config. Its supported engine environment override therefore selects a
separate CODEX_HOME containing `detection-config.toml`. That config retains the
compiler's OpenAI proxy URL, authentication and disabled WebSocket settings.
Recheck those settings when upgrading the compiler or firewall.

Loading this adapted metadata can change default instructions and capabilities
compared with fallback metadata. Explicit workflow tool restrictions and the
selected API model remain explicit. A new authorized practice run is required
before claiming that the hosted warning is gone; prior results are preserved.

## Offline verification

Validated with the official Windows Codex CLI 0.164.0 binary and isolated
configuration directories. A loopback-only HTTP server rejected every inference
request with an intentional error; no real credentials or provider calls were
used. Without the catalogue, the CLI emitted the fallback warning. With the
catalogue, both tested configurations resolved without that warning and still
requested `gpt-5-mini`. The intentional HTTP rejection returned exit 1;
it was not a successful model run. Hosted Linux/container delivery remains to
be checked in a separately authorized practice run.

`tests/test_model_catalog.py` checks catalogue identity, the native-editing
restriction, artifact delivery, the detector config path and proxy consistency.
