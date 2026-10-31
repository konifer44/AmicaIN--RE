> **Prepared by Jan Konieczny.**

# AGENTS.md - AmicaIN / SmartIN / SMART2

This project is for the **AmicaIN**(`amica.com`) application and the**SmartIN / SMART2** platform oven. Do not confuse it with the Amica Home (Tuya) application. Start with this file and [README.md](README.md); select further documents for the task.

Agent instructions in this file take precedence over older instructions in the README and diagnostic documentation.

## Job for a non-technical person

- The user does not need to know the IP address, subnet, ports, session ID or how the router works. **Collect available data and solve problems yourself.** Don't start with a list of technical questions.
- When a user wants to connect to the oven, treat it as a task to be completed. Check the existing results, the computer's network status and possible ways to detect the device; continue diagnostics while useful independent work remains.
- Only ask a question when the necessary information cannot be reasonably determined on your own or physical action by the user is required. Briefly explain why it is necessary and provide one simple step-by-step instruction. Don't ask for your Wi-Fi password, login information, or session ID if there's another way.
- Write in simple language: say what you have found, what you are doing next and what the effect is. Only explain technical terms if they help the user take action. Don't present an assumption as confirmed fact.
- Use information already provided. If the user has confirmed that the oven works in AmicaIN, do not ask them to re-pair the device without an established reason.

## Connecting to the oven

1. Read [LAN-RUNTIME-INVESTIGATION.md](LAN-RUNTIME-INVESTIGATION.md), [OVEN-COMMUNICATION.md](OVEN-COMMUNICATION.md) and the existing results in `probes/`. Treat their description of the protocol as a hypothesis requiring confirmation on the device.
2. Check the active interface, computer address and actual network mask yourself. Use available local device data and existing tools to determine the likely candidate. The absence of a device name or an open port does not prove that the oven is not on the network; do not assign an address without reliable confirmation.
3. If necessary, use the discovery described in the project. Check the actual broadcast address: the current `tools/probe-smartin-lan.py` script assumes `/24`, which may not match your network. The known address of the device allows you to point to the target without this assumption. Select the limited diagnostics needed to find your oven.
4. If you need a session ID, first check the data available in your project and other possible ways to connect. Don't assume that the placeholder ID will ensure proper pairing. Don't write secrets in logs or reveal them in a response.
5. Base next steps on actual results. The mere operation of the application on the phone does not confirm that the computer has access to the oven via LAN. Successfully finding the device does not mean correct control.
6. Record useful results in `probes/{date}__lan-attempt/` and findings in the project documentation when the task involves such work. Explain the results and the specific restart point. When technical access or permissions prevent action, name the specific blockage and implement an available workaround.

Only your own equipment; no relay fuzzing and no foreign firmware from forums. Do not send commands to change settings, start heating or update firmware without explicit instructions from the user.

## Project map

|Place|Contents|
|---------|-----------|
|[README.md](README.md)|Project and file overview|
|[LAN-RUNTIME-INVESTIGATION.md](LAN-RUNTIME-INVESTIGATION.md)|Attempt to communicate in the local network|
|[OVEN-COMMUNICATION.md](OVEN-COMMUNICATION.md)|Communication and protocol arrangements|
|[SMARTIN-SMART2-DEEP-DIVE.md](SMARTIN-SMART2-DEEP-DIVE.md)|In-depth analysis of the platform|
|[AmicaIN-SmartIN-Research-Report.pdf](AmicaIN-SmartIN-Research-Report.pdf)|Report on the findings so far|
|[docs/08-decompilation-checklist.md](docs/08-decompilation-checklist.md)|APK analysis tips|
| `APK/downloaded/` |Downloaded application package|
| `apk-decompile-work/` |Working decompilation result|
| `apk-static/` |APK static analysis results|
| `assets-extract/` |Isolated application resources|
| `probes/` |Device diagnostic results|
| `tools/` |Support scripts including `probe-smartin-lan.py`|

Analyze APKs, resources and reports when it helps with a specific task. Check the availability of tools and existing artifacts before assuming something needs to be downloaded or recreated. Save results in the appropriate project directories, not in a separate document outside the project.
