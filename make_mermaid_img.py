import re
import subprocess
from pathlib import Path
from shutil import which
from PIL import Image as PILImage  # pillow

"""
설치 필요 : npm i -g @mermaid-js/mermaid-cli
"""

# ====== 특수문자 제거 ======
def _slugify(s: str) -> str:
    s = s.strip() # 양쪽 공백 제거
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^0-9a-zA-Zㄱ-힣_]", "", s) # 숫자, 영어 대/소, _가 아닌 모든 문자를 제거
    if not s: # 문자열이 없으면 node 반환
        s = "node"
    if s[0].isdigit(): # 문자열 첫번째가 숫자면 앞에 _ 추가
        s = "_" + s
    return s

def generate_mermaid_from_buttons(buttons, direction="LR", title="버튼-DB 관계도"):
    """
    buttons: [{"id": 1, "name": "주문 조회", "backend": "orders"}, ...]
    direction: "LR"(좌->우), "TB"(상->하) 등
    """
    # 고유 버튼/DB 목록 : 버튼, DB를 각각 다른 리스트에 분리 저장
    btn_names, db_names = [], []
    for b in buttons:
        if b["name"] not in btn_names:
            btn_names.append(b["name"])
        if b["backend"] not in db_names:
            db_names.append(b["backend"])

    # ID 매핑
    btn_ids = {name: _slugify(f"btn_{name}") for name in btn_names}
    db_ids  = {name: _slugify(f"db_{name}")  for name in db_names}

    lines = []
    lines.append(f"flowchart {direction}")
    lines.append(f"%% 제목: {title}")
    lines.append("")

    # Buttons
    lines.append("subgraph Buttons")
    for name in btn_names:
        nid = btn_ids[name]
        # 이름 옆에 (id) 표시를 원하면: label = f"{name} ({...})"
        lines.append(f'    {nid}["{name}"]')
    lines.append("end\n")

    # Databases
    lines.append("subgraph Databases")
    for name in db_names:
        nid = db_ids[name]
        lines.append(f'    {nid}[("{name}")]')  # 원통형
    lines.append("end\n")

    # node 간의 간선
    for b in buttons:
        lines.append(f"{btn_ids[b['name']]} --- {db_ids[b['backend']]}")

    # 스타일 설정
    lines.extend([
        "",
        "%% 스타일",
        "classDef button fill:#E6F3FF,stroke:#5B9BD5,stroke-width:1px,color:#0B3D91;",
        "classDef db fill:#FFF2CC,stroke:#C65911,stroke-width:1px,color:#7F6000;",
        "class " + ",".join(btn_ids.values()) + " button;",
        "class " + ",".join(db_ids.values())  + " db;",
    ])

    return "\n".join(lines)

# ================ mermaid 저장 ==================

def save_mermaid(mermaid_str: str, path: str):
    p = Path(path)
    p.write_text(mermaid_str, encoding="utf-8")
    return str(p.resolve())

# ================ mermaid html로 저장 ==================

def save_mermaid_as_html(mermaid_str: str, path: str, page_title="Mermaid Diagram"):
    html = f"""
    <!doctype html>
    <html lang="ko">
    <head>
      <meta charset="utf-8">
      <title>{page_title}</title>
      <style>
        body{{margin:24px;font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,Apple SD Gothic Neo,Malgun Gothic,sans-serif}}
      </style>
      <script type="module">
        import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs";
        mermaid.initialize({{"startOnLoad": true, "securityLevel": "loose"}});
      </script>
    </head>
    <body>
      <h2>{page_title}</h2>
      <div class="mermaid">
    {_indent(mermaid_str, 4)}
      </div>
    </body>
    </html>
          """
          
    p = Path(path)
    p.write_text(html, encoding="utf-8")
    
    return str(p.resolve())

# ================ 문자열 앞에 공백 생성 ==================

def _indent(s: str, n: int) -> str:
    pad = " " * n
    return "\n".join(pad + line for line in s.splitlines())

# ================ mermaid 도식화 이미지를 png로 변환 ==================

def render_with_mmdc(input_mmd: str, output_path: str = None, scale: float = 1.0):
    """
    @mermaid-js/mermaid-cli (mmdc) 로 렌더.
    """
    in_path = Path(input_mmd)
    
    if output_path is None:
        output_path = str(in_path.with_suffix(".png"))
    
    cmd = ["npx", "-y", "@mermaid-js/mermaid-cli", "-i", str(in_path), "-o", output_path, "-s", str(scale)]
    
    subprocess.run(cmd, check=True, shell=True)

    return str(Path(output_path).resolve())

# ================ mermaid 실행 ==================

def result_mermaid_png(datas, doc, direction="LR", title=str, file_num=str) :
    
    ## mermaid 전환용 str 생성
    mermaid_str = generate_mermaid_from_buttons(
        datas,
        direction=direction,
        title=title
    )
    # print("===== Mermaid =====\n", mermaid_str)
    # print("\n")

    ## .mmd로 저장
    mmd_file_name = "graphdb_relation_" + file_num + ".mmd"
    mmd_path = save_mermaid(mermaid_str, mmd_file_name)
    # print("==== saved .mmd ====\n", mmd_path)

    ## HTML 에 mermaid 이미지 저장
    html_file_name = "graphdb_relation_" + file_num + ".html"
    html_path = save_mermaid_as_html(mermaid_str, html_file_name, page_title="버튼-DB 관계도")
    # print("==== saved .html =====\n", html_path)

    ## mmdc 를 사용하여 html의 mermaid 이미지를 가져오고, png 파일로 변환
    png_name = "graphdb_relation_" + file_num + ".png"
    try:
        png_path = render_with_mmdc(mmd_path, png_name, scale=1.0)
        print("✅ mermade png 생성 완료 : \n", png_path)
    except RuntimeError as e:
        print("==== 이미지 렌더 에러 =====\n", e)

    ## pdf에서 사용할 PNG의 픽셀 크기 조정 (1.5배 축소)
    with PILImage.open(png_path) as im:
        px_w, px_h = im.size
        dpi_x, dpi_y = im.info.get("dpi", (72, 72))  # DPI 없으면 72로 가정

    img_w_pt = px_w * 72.0 / dpi_x
    img_h_pt = px_h * 72.0 / dpi_y

    scale = 1.0 / 1.5   ### 1.5배 축소 (≈ 0.6667)
    img_w_pt *= scale
    img_h_pt *= scale

    max_w = doc.width ### 페이지 폭(doc.width)보다 넓으면 비율 유지하며 축소
    if img_w_pt > max_w:
        s = max_w / img_w_pt
        img_w_pt *= s
        img_h_pt *= s

    return png_name, img_w_pt, img_h_pt 
    