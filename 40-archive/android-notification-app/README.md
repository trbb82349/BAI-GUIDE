# 안드로이드 알림 테스트 앱

버튼을 누르면 폰 알림창에 알림이 뜨는 가장 단순한 안드로이드 앱. 실제로 설치 가능한 `.apk` 파일을 만들어보는 첫 연습용 프로젝트.

## 결과물

- `output/notify-app-debug.apk` — 폰에 설치 가능한 파일 (약 780KB, 서명 안 된 debug 빌드)

## 설치 방법 (폰에서)

1. `output/notify-app-debug.apk` 파일을 폰으로 옮긴다 (카카오톡 나에게 보내기, USB 연결, 구글 드라이브 등 아무 방법이나 가능)
2. 폰에서 그 apk 파일을 눌러서 연다
3. "출처를 알 수 없는 앱" 설치 허용 여부를 물어보면 허용 (설정 > 보안 에서도 미리 켤 수 있음)
4. 설치 후 앱을 열고 "알림 보내기" 버튼을 누르면 알림이 뜬다 (안드로이드 13 이상은 처음 열 때 알림 권한을 한 번 허용해야 함)

## 다시 빌드하는 방법 (컴퓨터에서)

```
cd src
./gradlew.bat assembleDebug
```

빌드 결과는 `src/app/build/outputs/apk/debug/app-debug.apk` 에 생긴다.

## 이번에 컴퓨터에 새로 설치된 것

- Java (Microsoft OpenJDK 17) — `C:\Program Files\Microsoft\jdk-17.0.20.8-hotspot`
- Android SDK 명령줄 도구 — `C:\Android\Sdk` (platform-tools, build-tools 34.0.0, platform android-34)
- Gradle 8.7 — `C:\Android\gradle-8.7` (프로젝트 안에는 `gradlew.bat`로 wrapper가 들어있어서 이후엔 이 폴더가 없어도 프로젝트 자체적으로 빌드 가능)

Android Studio는 설치하지 않음 — 명령줄 도구만으로 빌드했기 때문에 코드는 VSCode 등 일반 에디터에서 봐도 됨.

## 다음에 확장하고 싶다면

원래 하고 싶었던 건 "웹사이트/데이터 변화를 감지해서 카카오톡으로 알림 보내기"였음. 이번 앱은 그중 "폰에 알림 띄우기" 부분만 안드로이드 로컬 알림으로 검증한 것이고, 아래 두 가지는 아직 안 붙어 있음.

- 웹사이트 변화 감지 (주기적으로 확인하는 로직)
- 카카오톡으로 실제 메시지 보내기 (네이티브 앱에서 카카오 SDK 붙이려면 카카오 디벨로퍼스 계정 + 네이티브 앱 키 등록이 별도로 필요함)

이어서 하려면 `notes/`에 어떤 사이트를, 얼마나 자주 확인할지부터 정리하고 시작하는 게 좋음.

## 구조

```
android-notification-app/
├── README.md
├── src/          ← Gradle 프로젝트 전체 (app/, gradlew.bat 등)
├── input/        ← (아직 없음)
├── output/       ← 빌드된 apk 파일
└── notes/        ← (아직 없음)
```
