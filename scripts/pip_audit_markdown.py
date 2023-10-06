"""
Run pip-audit and output a table in the format that renders nicely on github.
"""
import json
import subprocess
from typing import Any

from prettytable import MARKDOWN, PrettyTable


def get_results() -> dict[str, list[dict[str, Any]]]:
    process = subprocess.run(
        ["pip-audit", "-s", "osv", "-f", "json"],
        capture_output=True,
        universal_newlines=True,
    )
    return json.loads(process.stdout)


def format_results(results: dict[str, list[dict[str, Any]]]) -> PrettyTable:
    table = PrettyTable(["name", "version", "fix_version", "id", "desc"])
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
            table.add_row([
                pkg_dict["name"],
                pkg_dict["version"],
                fix_ver,
                vuln["id"],
                vuln["description"],
            ])
    return table


def main():
    table = format_results(get_results())
    if not table.rows:
        print("No vulnerabilities found")
        return 0
    else:
        print(table)
        return 1


if __name__ == "__main__":
    exit(main())
