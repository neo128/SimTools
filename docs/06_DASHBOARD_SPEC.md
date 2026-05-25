# Dashboard Spec

The dashboard MVP uses Streamlit because it is lightweight and fast for local
inspection.

## Sections

1. Overview: tool counts, categories, installation difficulty, visualization
   support, GPU requirements, and large asset flags.
2. Tool Matrix: the same comparison matrix used by the CLI.
3. Real Readiness: local runnable and visualization verification gate.
4. Experiment Library: experiment configs from `configs/experiments/`.
5. Run History: run records from `.simtools/runs/`.
6. Run Detail: selected `report.json` content, run path, report path, artifact
   directory, and artifact references.
7. Tool Detail: manifest summary, sample commands, install profiles, viewer
   modes, and smoke command.
8. Doctor Preview: local system info and adapter status.
9. Artifacts: repository-local screenshots, videos, logs, and smoke reports
   when present.
10. Profiles: local, linux_gpu, macos_light, and windows_light profile metadata.

## Rules

- The dashboard reads from the same registry/config as the CLI.
- The dashboard reads run history through the same run-store helpers as the CLI.
- Experiment Library uses the same experiment-loading helper as the CLI.
- It must not import real simulators.
- It must not launch viewers directly in tests.
- If Streamlit is missing, `simtools ui` prints an install hint.
