#!/usr/bin/env python3
from cli.main import app
import os
os.environ["TERM"] = "xterm-256color"

if __name__ == "__main__":
    app()