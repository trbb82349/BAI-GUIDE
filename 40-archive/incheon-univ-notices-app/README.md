# 인천대 알림 모음 — 안드로이드 앱

`10-projects/incheon-univ-notices/`에서 만들어 GitHub Pages로 배포해둔 사이트(`https://trbb82349.github.io/incheon-univ-notices/`)를 안드로이드 앱 안에서 그대로 열어주는 웹뷰(WebView) 래퍼 앱.

## 왜 웹뷰 방식인가

원본 사이트는 GitHub Actions가 매일 자동으로 최신 공지를 모아서 갱신한다. 앱이 그 페이지 주소를 그대로 불러오기 때문에, **앱을 다시 빌드하지 않아도** 사이트가 갱신될 때마다 앱에서도 최신 내용이 보인다. HTML을 앱 안에 통째로 넣는 방식은 그때그때 스냅샷이라 매번 다시 빌드해야 해서 이 목적에는 맞지 않음.

## 결과물

- `output/incheon-notices-app-debug.apk` — 폰에 설치 가능한 파일 (약 780KB, 서명 안 된 debug 빌드)

## 설치 방법 (폰에서)

이전에 만든 `android-notification-app`과 동일한 방식.

1. `output/incheon-notices-app-debug.apk`를 카카오톡 나에게 보내기 등으로 폰에 옮긴다
2. 폰에서 파일을 눌러서 연다
3. "출처를 알 수 없는 앱" 설치 허용
4. 설치 후 앱을 열면 자동으로 인천대 알림 모음 사이트가 뜬다
5. 인터넷(와이파이/데이터)이 연결돼 있어야 내용이 보인다 — 완전 오프라인 스냅샷이 아니라 매번 실시간으로 불러오는 방식

## 다시 빌드하는 방법

```
cd src
./gradlew.bat assembleDebug
```

주소를 바꾸고 싶으면 `src/app/src/main/res/values/strings.xml`의 `site_url` 값만 고치고 다시 빌드하면 된다.

## 구조

```
incheon-univ-notices-app/
├── README.md
├── src/          ← Gradle 프로젝트 전체 (WebView 하나만 있는 최소 구조)
├── input/        ← (아직 없음)
├── output/       ← 빌드된 apk 파일
└── notes/        ← (아직 없음)
```
