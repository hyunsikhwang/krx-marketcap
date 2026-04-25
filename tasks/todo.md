# TODO

- [x] KRX/NXT `tradeType` 실응답 형태 확인
- [x] 서울시간 기준 장중/장외 판정 로직 추가
- [x] `load_stock_data`가 선택된 `tradeType`으로 조회되도록 수정
- [x] 화면에 현재 가격 기준 시장(KRX/NXT)과 적용 시간대 표시
- [x] 검증 결과 및 변경 영향 정리

## Review

- `get_current_trade_type_info()`를 추가해 서울시간 기준 09:00 이전 또는 15:00 이후에는 `NXT`, 그 외에는 `KRX`를 선택하도록 구현함
- `load_stock_data()`가 `trade_type` 인자를 받아 네이버 API 조회 시 `tradeType`을 동적으로 반영하도록 수정함
- 필터 영역 아래에 현재 가격 기준 시장과 적용 시간대, 현재 서울 시각을 함께 보여주는 배너를 추가함
- 검증: `curl -sS -A 'Mozilla/5.0' ...tradeType=KRX...` 및 `...tradeType=NXT...`로 두 응답이 모두 동일 스키마 계열임을 확인
- 검증: `python3 -m py_compile app.py` 통과
- 테스트: 미실행 (사유: 저장소에 표준 테스트 스크립트 없음, 로컬 환경에 앱 런타임 의존성 미설치)
