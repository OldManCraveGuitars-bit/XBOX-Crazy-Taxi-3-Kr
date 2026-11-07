**V1.0 비공식 한글판 정식버젼 — 패처 수정판 1.0.1**

**Korea Localized by GiKakNo**

초기 EXE는 실행 경고 제보 후 회수했습니다. 이번 릴리스는 배포용 패처를 교체한 버전입니다. **게임 한글화 내용과 결과 ISO 해시는 V1.0과 동일합니다.**

- Python/PyInstaller·외부 xdelta EXE를 제거하고 일반 C#/.NET EXE로 제작
- 실행 파일을 임시 폴더에 추출하거나 다른 프로그램을 실행하지 않음
- 네트워크 접근·관리자 권한 요구 없음
- 원본·내장 데이터·결과 SHA-256 검증, 기존 파일 덮어쓰기 방지
- 최신 정의 `1.463.169.0`의 Microsoft Defender 사용자 지정 검사에서 위협 미탐지
- 15개 데이터 테스트와 폼 배치 검사, 실제 원본 적용을 포함한 8개 통합 검증 통과

**사용법:** `XBOX-Crazy-Taxi-3-Kr-v1.0.1-Patcher.exe` 실행 → Japan (En,Ja) 원본 ISO 선택 → 새 저장 경로 선택 → 패치·결과 검증 완료.

단일 EXE이며 Windows 10/11의 .NET Framework 4.x를 사용합니다. Python이나 별도 패치 도구가 필요 없습니다.

EXE SHA-256:
```text
bd7a9329574e9b131a5fa80f488c6a3a667ec0e8649f936e6e2994540edd1d22
```

원본 ISO: `63042c8c6abdf6e645214b47dffa8b9695b151a24c99ba2f18a513a4ef76cc26`  
한글 ISO: `71f18581106d3bc0f22ada87a06011a065fd941fafed82c660c382edd49f5fa8`

정확한 최초 탐지명은 확인되지 않아 원인이나 오탐 여부를 확정하지 않았습니다. 로컬 Defender 검사 결과가 모든 백신의 판단을 보증하지는 않습니다. 코드 서명은 되어 있지 않아 발행자·평판 경고가 표시될 수 있습니다. [검사 기록과 변경 내용](https://github.com/OldManCraveGuitars-bit/XBOX-Crazy-Taxi-3-Kr/blob/main/docs/SECURITY.md)을 공개합니다.

가사 자막은 기존과 같이 오디오 17개 중 12개, 총 260구간의 음성 인식 대조 번역본입니다. 전곡 직접 청취·모든 가사 완전 수록 검증은 완료하지 못했습니다. 게임 ISO·원작 XBE·음원은 배포하지 않습니다. [전체 사용법·범위·타이틀](https://github.com/OldManCraveGuitars-bit/XBOX-Crazy-Taxi-3-Kr#readme)을 참고하세요.
