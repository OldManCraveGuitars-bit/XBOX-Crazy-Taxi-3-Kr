![크레이지 택시 3 한글 타이틀](docs/images/title.png)

# 크레이지 택시 3: 하이 롤러

**V1.0 비공식 한글판 정식버젼 · Xbox 일본판 (En,Ja)**  
**Korea Localized by GiKakNo**

상단 이미지는 이번 패치에 적용한 한글 타이틀 리소스 미리보기입니다.

## 다운로드

**[V1.0 EXE 패처 받기](https://github.com/OldManCraveGuitars-bit/XBOX-Crazy-Taxi-3-Kr/releases/tag/v1.0.0)**

Windows 10/11 x64용 단일 EXE입니다. Python 설치나 인터넷 연결 없이 사용할 수 있습니다. 게임 ISO·실행 파일·음원은 배포하지 않으며, 아래 해시와 일치하는 원본 ISO를 직접 준비해야 합니다.

## 작업 내용

- 일본판의 메뉴, 설정, 저장·불러오기, 기록, 안내문, 목적지·기사 이름 등 한국어화
- 원작 분위기를 살린 한글 타이틀, 불꽃 글자, 미니게임·면허증 등 그래픽 작업
- 글자 외곽선·가독성 개선, 메뉴 정렬과 칸 넘침 수정
- 재생 중인 노래의 영어 제목 표시와 `♪`로 시작하는 한국어 가사 자막 추가
- `Korea Localized by GiKakNo` 크레딧 반영

**가사 수록 범위:** 게임 내 오디오 17개 중 12개에 총 260개 자막 구간을 수록했습니다. 음성 인식 결과를 대조해 번역한 검수본으로, 전곡 직접 청취 및 모든 가사 구간의 완전 수록을 검증한 상태는 아닙니다. 짧은 루프 4개와 `16_crash_US.adx`에는 신뢰할 만한 가사를 확정하지 못해 가사 자막을 넣지 않았습니다. [자막 범위와 검수 내용](docs/VERIFICATION.md)을 확인해 주세요.

## 사용법

1. 릴리스에서 `XBOX-Crazy-Taxi-3-Kr-v1.0-Patcher.exe`를 받습니다.
2. 실행 후 **Japan (En,Ja) 원본 ISO**와 **새 ISO 저장 경로**를 선택합니다.
3. **한글 패치 시작**을 누르고 결과 SHA-256 검증 완료를 기다립니다.

패처는 원본을 덮어쓰지 않습니다. 이미 있는 출력 파일도 덮어쓰지 않으므로 새 파일 이름을 지정해 주세요. 패치와 xdelta 엔진은 EXE 안에 포함되어 있습니다. 별도 `.xdelta` 파일은 다른 패치 도구를 사용하는 경우를 위해 함께 배포합니다.

원본 ISO는 **395,313,152 바이트**, 생성되는 한글 XISO는 **397,672,448 바이트**입니다. 출력 드라이브에는 최소 450 MB, Windows 임시 폴더에는 약 50 MB의 여유 공간을 확보해 주세요. 지역·파일명이 같더라도 덤프 구조나 내용이 다르면 해시 검증에서 거부됩니다. 이미 패치한 ISO에는 다시 적용할 수 없습니다.

실기에서 실행하려면 수정된 XBE 실행을 지원하는 환경이 필요합니다. 기기에 맞는 기존 방식으로 한글 ISO 또는 추출한 게임 파일을 사용하세요.

## SHA-256

해시는 파일이 정확히 같은지 확인하는 값입니다. **원본 ISO 해시**는 패치 적용 가능 여부를, **한글 ISO 해시**는 적용 결과를, **배포 파일 해시**는 다운로드한 파일의 일치 여부를 확인할 때 사용합니다. EXE는 적용 전후 해시를 자동 검사합니다.

| 대상 | SHA-256 |
| --- | --- |
| Japan (En,Ja) 원본 ISO | `63042c8c6abdf6e645214b47dffa8b9695b151a24c99ba2f18a513a4ef76cc26` |
| V1.0 한글 ISO | `71f18581106d3bc0f22ada87a06011a065fd941fafed82c660c382edd49f5fa8` |
| `CT3-Korean-v1.0.xdelta` | `a06ffcadaa1f935a8bf8b322432714a251487f02929ee439138e602dfb1192d0` |
| `XBOX-Crazy-Taxi-3-Kr-v1.0-Patcher.exe` | `931e2428ab23ecca2112008e0bf56714b8ff6d2a19248d68718a503e223af58c` |

Windows PowerShell에서 수동 확인하는 예시입니다.

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath '.\XBOX-Crazy-Taxi-3-Kr-v1.0-Patcher.exe'
```

릴리스의 `SHA256SUMS.txt`와 [패치 명세](patches/manifest.json)에도 해시를 기록했습니다. 패처 자체는 코드 서명되어 있지 않으며, 해시는 전자서명을 대신하지 않습니다.

## 검수 및 알려진 사항

- 패치 결과의 파일 401개를 검사했습니다. 10개가 수정되었고 391개는 원본과 동일합니다. 원본 ISO와 음악 데이터는 보존했습니다.
- 번역·텍스처 항목 938행을 재검토하고, x86 검증 53개 그룹과 UI 배치 1,446개 실행을 확인했습니다. 이는 자동·정적 검수 범위이며 모든 장면의 플레이 검증을 뜻하지 않습니다.
- Xbox 실행 파일의 섹션·참조·텍스처 구조를 정적 검토했습니다. 실기 구동 검증은 수행하지 않았으므로 실기 전체 동작을 보증하는 결과는 아닙니다.
- 일부 에뮬레이터의 메뉴 안쪽 세로선은 일본판 원본에서도 확인된 현상으로, 이번 패치에서 해당 프레임을 변경하지 않았습니다.
- 플레이 스크린샷은 추후 추가 예정입니다.

자세한 범위와 제한은 [검수 기록](docs/VERIFICATION.md)에 정리했습니다.

## 패처 소스

이 저장소에는 배포용 EXE 패처의 Python 소스, 차이 패치와 검증 명세를 포함합니다.

```powershell
python -m pip install -r requirements-build.txt
python -m unittest discover -s src -v
python build.py
```

Windows x64와 Python 3.13에서 빌드했습니다. 결과 EXE는 `dist` 폴더에 생성됩니다. 명령줄 적용도 지원합니다.

```powershell
.\XBOX-Crazy-Taxi-3-Kr-v1.0-Patcher.exe --source '원본.iso' --output '한글.iso' --report '결과.json'
```

게임 및 원작 그래픽·음악의 권리는 각 권리자에게 있습니다. 이 패치는 SEGA의 공식 한국어판이 아닙니다. 포함된 도구의 라이선스는 [licenses](licenses/THIRD-PARTY.md)를 참고하세요.
