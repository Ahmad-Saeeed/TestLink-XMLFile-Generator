"""
build_xml.py
Generates a TestLink test-suite import XML for the Message Broker13 Cloud project.

Fixed structure (2 test cases per CR, no template .doc needed):

  Test case 1 – Success
    Title       : Run {api} API to get success object
    Summary     : Run {api} API to get success object in the response
    Precondition: To have valid parameters : {param1, param2, ...}
    Step action : Run {api} API with valid input parameters
    Expected    : To get success object in the response

  Test case 2 – Fault
    Title       : Run {api} API to get fault object
    Summary     : Run {api} API to get fault object in the response
    Precondition: (empty)
    Step action : Run {api} API with invalid input parameters
    Expected    : To get fault object in the response

execution_type = 1 (Manual), importance = 2 (Medium)
externalid is intentionally omitted — TestLink assigns it on import.
"""

from typing import List


def build_xml(
    api_name: str,
    params: List[str],
    cr_number: str,
    suite_name: str,
    out_path: str,
) -> None:
    """Write the TestLink import XML to *out_path*."""
    params_str = ", ".join(params) if params else ""
    xml = _render(api_name, params_str, suite_name)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(xml)


# ---------------------------------------------------------------------------
# rendering
# ---------------------------------------------------------------------------

def _esc(s: str) -> str:
    """Escape special XML attribute characters."""
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
    )


def _render(api: str, params_str: str, suite_name: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="{_esc(suite_name)}">
  <details><![CDATA[Test Suite for {api} API under Message Broker13 Cloud]]></details>
  <testcase name="Run {api} API to get success object">
    <version><![CDATA[1]]></version>
    <summary><![CDATA[Run {api} API to get success object in the response]]></summary>
    <preconditions><![CDATA[To have valid parameters : {params_str}]]></preconditions>
    <execution_type><![CDATA[1]]></execution_type>
    <importance><![CDATA[2]]></importance>
    <node_order><![CDATA[1]]></node_order>
    <steps>
      <step>
        <step_number><![CDATA[1]]></step_number>
        <actions><![CDATA[Run {api} API with valid input parameters]]></actions>
        <expectedresults><![CDATA[To get success object in the response]]></expectedresults>
        <execution_type><![CDATA[1]]></execution_type>
      </step>
    </steps>
  </testcase>
  <testcase name="Run {api} API to get fault object">
    <version><![CDATA[1]]></version>
    <summary><![CDATA[Run {api} API to get fault object in the response]]></summary>
    <preconditions><![CDATA[]]></preconditions>
    <execution_type><![CDATA[1]]></execution_type>
    <importance><![CDATA[2]]></importance>
    <node_order><![CDATA[2]]></node_order>
    <steps>
      <step>
        <step_number><![CDATA[1]]></step_number>
        <actions><![CDATA[Run {api} API with invalid input parameters]]></actions>
        <expectedresults><![CDATA[To get fault object in the response]]></expectedresults>
        <execution_type><![CDATA[1]]></execution_type>
      </step>
    </steps>
  </testcase>
</testsuite>
"""
