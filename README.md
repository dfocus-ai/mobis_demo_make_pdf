### 소스 코드
- make_pdf.py : 실행 시 buttons-dbs 데이터에 대한 gpt의 간단한 분석 요약 및 도식화 pdf 반환
- makd_mermaid_img.py : make_pdf.py 실행 후 mermaid 관계도를 png 이미지로 반환

### 실행 방법
- buttons-json : 버튼 id, 버튼 name, backend 데이터를 dict로 입력하여 button-backend 데이터를 생성
- pdf-name : pdf 파일 이름
```
python make_pdf.py --buttons-dbs '[{"id":1,"name":"주문 조회","backend":"orders"},{"id":2,"name":"주문 생성","backend":"orders"},{"id":3,"name":"회원 조회","backend":"users"},{"id":4,"name":"상품 목록","backend":"products"},{"id":5,"name":"상품 등록","backend":"products"}]' --pdf-name report.pdf
```

### 필요 사항
- 설치 필요 : npm i -g @mermaid-js/mermaid-cli
- mermaid 실행 시 필요
