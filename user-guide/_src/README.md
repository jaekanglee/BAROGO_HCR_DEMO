# HCR 사용 가이드 원본

`user-guide/index.html`은 이 폴더의 파일로 만든 결과물입니다. 가이드를 고칠 때는 `index.html`을 직접 고치지 말고 여기 원본을 고친 뒤 빌드합니다.

## 빌드

```sh
cd user-guide/_src
python3 build_guide.py   # → user-guide/index.html 생성 (Python 3 표준 라이브러리만 사용)
```

빌드 결과를 커밋해 `main`에 푸시하면 GitHub Pages로 배포됩니다.

## 파일

| 파일 | 내용 |
|------|------|
| `build_guide.py` | 장별 본문·스크린샷 배치·목차를 조립해 `index.html` 생성 |
| `glossary.py` | 용어 장 데이터(분류별 용어, 두 앱이 다르게 부르는 말) |
| `versions.py` | 기준 버전(앱·서버)과 변경 이력 |
| `diagrams.py` | 기능 지도 등 인라인 SVG 다이어그램 5종, 가이드 한눈에 보기(본문 장·소제목에서 자동 생성) |
| `search_aliases.py` | 장·소제목별 검색 동의어. 키는 제목과 정확히 같아야 함(다르면 빌드 실패) |
| `guide.css`, `guide.js` | 페이지 스타일, 검색·사진 확대 |

스크린샷은 `user-guide/img/*.jpg`(이름·잔액 등 가린 이미지)를 씁니다. 원본 캡처는 개인정보가 있어 레포에 넣지 않습니다.

## 고칠 때마다

1. 내용을 고친다(근거는 운영 코드 기준: HCR·라이더 앱, zoo 서버).
2. `versions.py`의 `HISTORY` 맨 위에 한 줄 추가. 장 추가·구조 변경은 minor(1.x), 문구·근거 정정은 patch(1.x.y).
3. 앱·서버 기준 버전이 바뀌었으면 `BASIS`도 갱신.
4. 빌드 → 커밋 → 푸시.
