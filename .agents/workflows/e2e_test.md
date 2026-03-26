---
description: Run End-to-End (E2E) Test on Sandbox Environment
---

이 워크플로우(스킬)는 `MediafileAutoFormatter Sandbox` 환경을 초기화하고 E2E 테스트를 실행합니다.

// turbo-all

1. `Before` 디렉토리에 원본 테스트 파일들을 복사하여 초기화합니다. `run_command` 툴을 사용하여 다음 PowerShell 명령어를 실행하세요:
`Copy-Item 'C:\Users\Administrator\Desktop\MediafileAutoFormatter Sandbox\Original\*' 'C:\Users\Administrator\Desktop\MediafileAutoFormatter Sandbox\Before\' -Recurse -Force`

2. 이전 테스트의 결과물이 남아있는 `After` 디렉토리를 비웁니다. `run_command` 툴을 사용하여 다음 명령어를 실행하세요:
`Remove-Item 'C:\Users\Administrator\Desktop\MediafileAutoFormatter Sandbox\After\*' -Recurse -Force -ErrorAction SilentlyContinue`

3. `main.py` 포매터 스크립트를 실행합니다. `run_command` 툴을 사용하여 다음 명령어를 비동기로 실행하세요 (설정에 맞게):
`uv run main.py "C:\Users\Administrator\Desktop\MediafileAutoFormatter Sandbox\Before" --target_path="C:\Users\Administrator\Desktop\MediafileAutoFormatter Sandbox\After" --multiple=True`

4. `command_status` 툴로 스크립트가 성공적으로 완료되었는지 확인한 후, `list_dir` 툴을 이용해 `After` 폴더 안에 변환/번역 결과물이 잘 저장되었는지 검증하세요.
