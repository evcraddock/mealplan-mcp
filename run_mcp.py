#!/usr/bin/env python3
"""
Wrapper script for running the MCP server with all dependencies.
This ensures that when mcp dev is used, all required dependencies are available.
"""

import sys
import subprocess
import importlib.util


def main():
    # Try to install missing dependencies if we're in an isolated environment
    if importlib.util.find_spec("reportlab") is None:
        print("Installing missing dependencies...")
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "reportlab>=4.0.0",
                "markdown>=3.5.0",
            ]
        )

    # Now run the actual main.py
    spec = importlib.util.spec_from_file_location("main", "main.py")
    main_module = importlib.util.module_from_spec(spec)
    sys.modules["main"] = main_module
    spec.loader.exec_module(main_module)


if __name__ == "__main__":
    main()
