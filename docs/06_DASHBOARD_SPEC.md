# Dashboard Spec

The dashboard MVP uses Streamlit because it is lightweight and fast for local
inspection.

## Sections

1. Overview: tool counts, categories, installation difficulty, visualization
   support, GPU requirements, and large asset flags.
2. Tool Matrix: the same comparison matrix used by the CLI.
3. Tool Detail: manifest summary, sample commands, install profiles, viewer
   modes, and smoke command.
4. Doctor Preview: local system info and adapter status.
5. Artifacts Placeholder: future screenshots, videos, logs, and smoke reports.
6. Profiles: local, linux_gpu, macos_light, and windows_light profile metadata.

## Rules

- The dashboard reads from the same registry/config as the CLI.
- It must not import real simulators.
- It must not launch viewers directly in tests.
- If Streamlit is missing, `simtools ui` prints an install hint.
