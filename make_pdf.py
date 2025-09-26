import os
import argparse, json
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI

# pdf 생성 라이브러리
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import networkx as nx

# mermaid 방법으로 관계를 도식화하고 img 파일로 반환하는 모듈
from make_mermaid_img import *

# input parsing
def parse_args():
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--buttons-json", type=str)
    p.add_argument("--pdf-name", type=str, required=True)
    return p.parse_args()

def load_buttons(args):

    data = json.loads(args.buttons_json)
    if not isinstance(data, list):
        raise ValueError("buttons는 리스트여야 합니다.")
 
    return data

# ============ 2) OpenAI API로 분석 요청 ============
def get_analysis_text(buttons):
    prompt = f"""
    프론트엔드에는 5개의 버튼이 있고, 각 버튼은 특정 DB와 연결됩니다.
    버튼-DB 매핑은 다음과 같습니다:

    {buttons}

    이를 기반으로:
    1) 전체 구조를 처음 보는 사람도 알기 쉽게 요약하세요. 
    2) 버튼과 DB 연결 관계를 예시와 같이 설명하세요. (예시: 1. "주문 조회" 버튼은 "orders" 백엔드와 연결됩니다.)

    분석을 한국어로 작성하세요.
    """
    os.environ["OPENAI_API_KEY"] = os.getenv("gpt_api_key")

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    analysis_text = response.choices[0].message.content
    analysis_text = analysis_text.replace("\n", "<br/>")  # 줄바꿈을 <br/>로 변환

    return analysis_text

# ============ 3) PDF 생성 ============
def build_pdf(pdf_name, buttons, analysis_text) : 
    ## pdf 폰트 설정
    pdfmetrics.registerFont(TTFont('MalgunGothic', 'C:/Windows/Fonts/malgun.ttf'))
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="KorTitle", fontName='MalgunGothic', fontSize=18)) ## 한글폰트 스타일 설정
    styles.add(ParagraphStyle(name="KorNormal", fontName='MalgunGothic', fontSize=12))
    styles.add(ParagraphStyle(name="KorHeading2", fontName='MalgunGothic', fontSize=12))

    ## pdf 객체 생성
    pdf_name = pdf_name
    doc = SimpleDocTemplate(pdf_name)

    story = []

    ## 제목 삽입
    story.append(Paragraph("< 프론트엔드-백엔드 연결 분석 리포트 >", styles["KorTitle"]))
    story.append(Spacer(1, 24))

    ## 분석 텍스트 삽입
    story.append(Paragraph(analysis_text, styles["KorNormal"]))
    story.append(Spacer(1, 12))

    ## mermaid 이미지 생성 + 삽입
    ## make_mermaid_img.py의 실행 함수 : png 파일 생성 후, 1.5 배 축소한 w, h 값 반환
    png_name, img_w_pt, img_h_pt = result_mermaid_png(buttons, doc, direction="LR", title="버튼-DB 관계도", file_num="1")
    story.append(Paragraph("GraphDB 스타일 관계도", styles["KorHeading2"]))
    story.append(Spacer(1, 12))
    story.append(Image(png_name, width=img_w_pt, height=img_h_pt))
    story.append(Spacer(1, 12))

    ## 버튼-DB 테이블 삽입
    table_data = [
        [
            Paragraph("버튼 이름", styles["KorNormal"]),
            Paragraph("연결된 DB", styles["KorNormal"]) 
        ]
    ]
    for b in buttons:
        table_data.append(
            [
                Paragraph(b["name"], styles["KorNormal"]),
                Paragraph(b["backend"], styles["KorNormal"])
            ]
        )

    table = Table(table_data, hAlign="LEFT", colWidths=[100, 100])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightblue),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
    ]))   

    story.append(Paragraph("버튼-DB 매핑 표", styles["KorHeading2"]))
    story.append(Spacer(1, 24))
    story.append(table)
    story.append(Spacer(1, 24))

    # PDF 빌드
    doc.build(story)


def main() : 
    
    args = parse_args()
    buttons = load_buttons(args)
    analysis_text = get_analysis_text(buttons)
    build_pdf(args.pdf_name, buttons, analysis_text)
    print("✅ PDF 리포트 생성 완료: \n", args.pdf_name)

if __name__ == "__main__" :
    main()    
    