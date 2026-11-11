# myharness

라운드 개발 하네스 플러그인.

| 구성 | 내용 |
|---|---|
| agents/verifier | spec 기준 검증, 보고만 |
| agents/cleaner | 죽은 코드 · 문서 불일치 정리 |
| hooks (PreToolUse) | `scripts/guard.py`: rm -rf · 강제 삭제 · force push · .env 읽기 차단, uv 프로젝트에서 pip 차단 |
| hooks (PostToolUse) | `scripts/project_lint.py`: 프로젝트에 `scripts/arch_lint.py`가 있으면 Edit/Write 뒤 실행 |
| skills/round | spec → plan → 구현 → 검증 → 정리 → 종료 점검 |

프로젝트마다 할 일: CLAUDE.md에 코드 규칙과 테스트 · 린트 명령을 적고, 필요하면 `scripts/arch_lint.py`를 둔다.
Hook은 PATH의 `python`으로 실행된다.

## 설치 (로컬)
```
/plugin marketplace add <이 폴더의 경로>
/plugin install myharness@myharness-marketplace
```
