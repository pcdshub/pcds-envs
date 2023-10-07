"""
Run pip-audit and output a table in the format that renders nicely on github.
"""
import json
import subprocess
from typing import Any

from prettytable import MARKDOWN, PrettyTable

# Vulnerabilities that we've seen and acknowledged and why they are OK for us
ACK_LIST = {
    "GHSA-29gw-9793-fvw7": "Windows-only",
    "PYSEC-2023-163": "Only affects langchain users",
}


def get_results() -> dict[str, list[dict[str, Any]]]:
    process = subprocess.run(
        ["pip-audit", "-s", "osv", "-f", "json"],
        capture_output=True,
        universal_newlines=True,
    )
    return json.loads(process.stdout)


def format_results(results: dict[str, list[dict[str, Any]]]) -> PrettyTable:
    table = PrettyTable(
        ["name", "version", "fix_version", "new or seen", "id", "desc", "are we ok"]
    )
    table.set_style(MARKDOWN)
    for pkg_dict in results["dependencies"]:
        if not pkg_dict["vulns"]:
            continue
        for vuln in pkg_dict["vulns"]:
            try:
                fix_ver = vuln["fix_versions"][0]
            except IndexError:
                # No known fix
                fix_ver = ""
            if vuln["id"] in ACK_LIST:
                new_or_seen = "Seen"
                are_we_ok = ACK_LIST[vuln["id"]]
            else:
                new_or_seen = "New"
                are_we_ok = "Needs investigation"
            table.add_row([
                pkg_dict["name"],
                pkg_dict["version"],
                fix_ver,
                new_or_seen,
                vuln["id"],
                vuln["description"],
                are_we_ok,
            ])
    return table


def main():
    table = format_results(get_results())
    if not table.rows:
        print("No vulnerabilities found")
        return 0
    else:
        print(table)
        if "investigation" in str(table):
            return 1
        else:
            return 0


if __name__ == "__main__":
    exit(main())
