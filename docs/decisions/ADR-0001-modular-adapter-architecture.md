# ADR-0001: Modular Adapter Architecture

## Status

Accepted

## Context

Embodied AI simulators have conflicting dependency stacks, GPU requirements,
asset stores, GUI/headless modes, and operating system assumptions. Installing
all of them into one environment would make the base project fragile and hard to
test.

## Decision

SimTools represents each simulator with:

1. a YAML manifest
2. a lightweight adapter
3. one or more installation profiles
4. smoke and viewer command plans
5. documentation and tests

The core registry and CLI operate on manifests and adapter contracts. Simulator
dependencies are lazy-loaded only in explicit execution paths.

## Consequences

- The base package stays lightweight.
- Tests run without real simulators.
- New tools can be added with limited core changes.
- Real integrations require careful opt-in execution paths.
