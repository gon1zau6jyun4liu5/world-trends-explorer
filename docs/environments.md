# 환경 운영

변경은 기능 브랜치 → dev → stg → prd 순서로 PR과 검사 후 머지합니다.
각 환경은 해당 브랜치의 독립 Git worktree에서 실행합니다. PR 머지만으로 로컬 서버가 자동 배포되지는 않습니다. 대상 worktree를 `git merge --ff-only origin/<환경>`로 갱신하고 포털 manager로 해당 앱만 재시작합니다.

| 환경 | 포털 앱 ID | 포트 | 데이터 |
| --- | --- | --- | --- |
| dev | world-trends-dev | 49481 | dev 전용 SQLite |
| stg | world-trends-stg | 49482 | stg 전용 SQLite |
| prd | world-trends | 49480 | 기존 운영 SQLite 유지 |

서버는 `backend/desk_server.py --port <포트> --data-dir <독립 데이터 경로>`로 실행합니다.
`LOCAL_APPS_PORTAL`에 기존 포털 경로를 지정하여 공통 기기 허용 목록과 로그인 세션을 재사용합니다. 원격 호스트는 포털 network.json에서 읽으며, 포털 링크도 현재 호스트를 사용합니다.

개발·검증 데이터는 최초에만 SQLite backup API로 운영 데이터의 일관된 스냅샷을 만들고 이후 분리합니다. 운영 데이터를 테스트 데이터로 덮어쓰지 않습니다. 데이터와 인증 파일은 Git에 넣지 않습니다.

승격마다 CI, 로컬 응답, 원격 로그인 및 API 인증, 공유 세션, Origin/CSRF 차단을 확인합니다. 화면 변경은 데스크톱·태블릿·모바일에서 검증합니다. 외부 제공자의 요청 한도는 세 환경이 같은 IP를 쓰므로 공유될 수 있습니다.

릴리즈 태그는 검증한 prd 커밋에 생성합니다. 롤백이 필요하면 직전 릴리즈의 별도 worktree로 운영 실행 경로를 바꾸고 기존 운영 데이터 경로는 유지합니다. 스키마 변경이 있는 릴리즈는 데이터 호환성을 먼저 확인합니다.
