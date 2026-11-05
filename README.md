# TestLink CR XML Generator

Standalone Windows desktop app that generates a **TestLink test-suite import XML**
for a new Change Request on the **Message Broker13 Cloud** project.

No template `.doc` needed — the two fixed test-case patterns (Success / Fault)
are built in. Just supply the ISD `.docx` and a CR number.

---

## Usage

1. Click **Browse…** and select the ISD .docx for the new CR  
   (filename must follow the `*_<ApiName>_ISD*.docx` naming convention).
2. The app auto-detects the **API name** and **input parameters**.  
   Edit the API name field if the auto-detection picked the wrong segment.
3. Type the **CR number** (digits only, e.g. `6885`).
4. The **output filename** is auto-filled as  
   `Message Broker13 Cloud - CR <number> - <ApiName>` — edit if needed.
5. Click **Generate XML** and choose where to save the .xml file.
6. Import the saved .xml into TestLink via  
   **Test Project → Import Test Cases** (or **Import Test Suite**).

---

## Generated XML structure

```xml
<testsuite name="Message Broker13 Cloud - CR {cr} - {api}">
  <testcase name="Run {api} API to get success object">
      Precondition : To have valid parameters : {param1, param2, ...}
      Step action  : Run {api} API with valid input parameters
      Expected     : To get success object in the response
  </testcase>
  <testcase name="Run {api} API to get fault object">
      Precondition : (empty)
      Step action  : Run {api} API with invalid input parameters
      Expected     : To get fault object in the response
  </testcase>
</testsuite>
```

`execution_type = 1` (Manual), `importance = 2` (Medium).  
`externalid` is **not** included — TestLink assigns it on import.

---

## Building from source (GitHub Actions)

Push the repository to GitHub. The workflow at  
`.github/workflows/build.yml` runs automatically on every push to `main`  
and uploads the whole `TestLinkCRXMLGen` folder (onedir layout) as a build artifact.

To download: **Actions → latest run → Artifacts → TestLinkCRXMLGen-Windows**.

### Why onedir instead of a single .exe?

- Far fewer VirusTotal / Windows Defender false positives  
  (one-file EXEs extract themselves at runtime – a classic AV heuristic).
- Proper Windows VERSIONINFO metadata is embedded.
- If anything still fails at startup, a log file  
  `TestLinkCRXMLGen_error.log` is written next to the executable.

### Local build (optional)

```bat
pip install python-docx lxml pyinstaller
pyinstaller --clean TestLinkCRXMLGen.spec
:: output: dist\TestLinkCRXMLGen\TestLinkCRXMLGen.exe
```

---

## Project layout

```
TestLinkCRXMLGen/
├── app.py                 # GUI entry point (tkinter) + error logging
├── extract_isd.py         # Reads API name + parameters from ISD .docx
├── build_xml.py           # Renders the TestLink import XML
├── requirements.txt
├── TestLinkCRXMLGen.spec  # PyInstaller spec (onedir, VERSIONINFO, upx=False)
└── .github/workflows/
    └── build.yml          # GitHub Actions build
```

## Troubleshooting

| Symptom | What to do |
|---------|------------|
| EXE does not start / nothing happens | Look for `TestLinkCRXMLGen_error.log` next to the EXE. It contains the full Python traceback. |
| VirusTotal still flags a few engines | Expected for any unsigned binary. The onedir + VERSIONINFO build is already much cleaner. You can also add an Authenticode signature if you have a code-signing certificate. |
| “Cannot detect API name” | Filename must contain `_<ApiName>_ISD` (case-insensitive). |
| No parameters found | Check that the ISD has either an “Input Parameters” table or `MessageBody/<name>` XPath-style text. |
