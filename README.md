# AmicaIN: Reverse Engineering

An **independent research project** exploring how the AmicaIN app communicates with an oven in the SmartIN / SMART2 ecosystem.

The goal is to collect knowledge and provide a **starting point for further independent research** into the device's communication and possible integrations. The material was prepared for educational and documentation purposes.

This is not a finished integration or a complete product. Some findings come from static analysis of the app and still need to be verified against a physical device. This project is independent and is not officially affiliated with the manufacturer.

## Why this project?

This project is based on my experience with reverse engineering from before AI tools became part of the process, combined with what I've learned using AI agents today. I put it together to share that knowledge and give someone else a place to start their own research.

It also draws on knowledge gathered around [REA: Reverse Engineer Anything](https://github.com/morluto/rea). The repository is intended to support further investigation, including work with an AI agent.

## Getting started

1. Read the [research report](AmicaIN-SmartIN-ustalenia.md) for the scope and background.
2. Explore the [oven communication notes](KOMUNIKACJA-PIEKARNIK.md) for initial findings about the protocol and communication paths.
3. Before working with a physical device, read the [local network investigation notes](PROBE-LAN-RUNTIME.md).
4. If you're handing the project to an AI agent, start with [AGENTS.md](AGENTS.md).

## What's in this repository?

| File or directory | Contents |
|---|---|
| [AGENTS.md](AGENTS.md) | Entry point and working instructions for an AI agent |
| [AmicaIN-SmartIN-ustalenia.md](AmicaIN-SmartIN-ustalenia.md) | Full research report and background |
| [AmicaIN-SmartIN-ustalenia.pdf](AmicaIN-SmartIN-ustalenia.pdf) | PDF version of the report |
| [KOMUNIKACJA-PIEKARNIK.md](KOMUNIKACJA-PIEKARNIK.md) | Initial findings about device communication |
| [SMARTIN-SMART2-gleboko.md](SMARTIN-SMART2-gleboko.md) | Analysis of the SmartIN / SMART2 ecosystem |
| [PROBE-LAN-RUNTIME.md](PROBE-LAN-RUNTIME.md) | Starting point for investigating local network communication |
| `tools/` | Scripts for analysis and communication experiments |
| `apk-static/` and `assets-extract/` | Materials obtained during app analysis |

## Working with an AI agent

Open the project root as your workspace and point the agent to [AGENTS.md](AGENTS.md). It contains the context, constraints, and guidance for continuing the work.

App analysis results are organized under `apk-static/`, while results from communication experiments belong in `probes/`.

## Third-party materials

Product names and other third-party materials belong to their respective owners. They are referenced in this project for the purpose of documenting and studying the system. Check the applicable licenses and terms before reusing or redistributing any materials.

## Status

This repository is a **starting point for further research**. Before building an integration based on these findings, verify the assumptions, app version, and behavior of your own device.
