"""위험한 명령과 비밀 파일 읽기를 실행 전에 막는 PreToolUse Hook.

막는 것
  - rm -rf, PowerShell Remove-Item -Recurse -Force, rmdir /s
  - git push --force / -f
  - pip, pip3, python -m pip, python -m venv   (프로젝트에 uv.lock 이 있을 때만)
  - .env 파일 읽기 (Read 도구, cat/type/Get-Content)

Bash · PowerShell · Read 도구에 건다(matcher "Bash|PowerShell|Read").
Hook 입력(JSON, stdin)을 검사하고, 막을 때는 exit 2 와 함께 이유를 stderr 로 돌려준다.
"""
import json
import os
import re
import sys
from pathlib import Path

RULES = [
    (r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*f|\brm\s+-[a-zA-Z]*f[a-zA-Z]*r",
     "rm -rf 는 막혀 있습니다. 지울 파일을 사람에게 확인받으세요."),
    (r"(?i)\bRemove-Item\b(?=.*-Recurse)(?=.*-Force)|\brmdir\s+/s\b",
     "재귀 강제 삭제는 막혀 있습니다. 지울 파일을 사람에게 확인받으세요."),
    (r"\bgit\s+push\b.*(--force\b|\s-f\b)",
     "git push --force 는 막혀 있습니다. 일반 push 를 쓰세요."),
    (r"(?i)(^|[\s;&|])(cat|type|more|less|head|tail|Get-Content|gc)\s+([^;&|]*[\/\s\"'])?\.env([\s\"';&|]|$)",
     ".env 는 읽지 않습니다. 필요한 값은 사람에게 물어보세요."),
]

UV_RULES = [
    (r"(^|[\s;&|])(pip3?|python3?\s+-m\s+pip)\s",
     "이 프로젝트는 uv 를 씁니다. 패키지는 `uv add <패키지>`, 실행은 `uv run` 을 쓰세요."),
    (r"python3?\s+-m\s+venv\b",
     "가상환경은 직접 만들지 않습니다. `uv sync` 가 .venv 를 만듭니다."),
]


def project_dir(data: dict) -> Path:
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or ".")


def block(target: str, reason: str) -> int:
    print(f"[guard] 차단: {target}\n이유: {reason}", file=sys.stderr)
    return 2


def main() -> int:
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    tool_input = data.get("tool_input") or {}

    if data.get("tool_name") == "Read":
        path = tool_input.get("file_path", "")
        if Path(path).name == ".env":
            return block(path, ".env 는 읽지 않습니다. 필요한 값은 사람에게 물어보세요.")
        return 0

    command = tool_input.get("command", "")
    rules = list(RULES)
    if (project_dir(data) / "uv.lock").exists():
        rules += UV_RULES
    for pattern, reason in rules:
        if re.search(pattern, command):
            return block(command, reason)
    return 0


if __name__ == "__main__":
    sys.exit(main())
