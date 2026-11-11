"""파일을 고친 뒤 프로젝트의 린터를 돌리는 PostToolUse Hook.

플러그인은 규칙을 모른다. 규칙은 프로젝트가 `scripts/arch_lint.py` 로 갖고,
이 Hook은 그 파일이 있을 때만 실행해 결과를 그대로 넘긴다.
  - uv.lock 이 있으면 `uv run python scripts/arch_lint.py`
  - 없으면 지금 쓰는 python 으로 실행
린터가 exit 2 로 끝나면 stderr 의 수정 지침이 에이전트에게 전달된다.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

LINTER = Path("scripts") / "arch_lint.py"


def main() -> int:
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or ".")
    linter = root / LINTER
    if not linter.exists():
        return 0
    if (root / "uv.lock").exists():
        cmd = ["uv", "run", "--project", str(root), "python", str(linter)]
    else:
        cmd = [sys.executable, str(linter)]
    result = subprocess.run(cmd, cwd=root, capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        sys.stderr.write(result.stderr or result.stdout)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
