#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.platypus.flowables import Flowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Rect, Line, String
from reportlab.graphics import renderPDF
import os

# ── フォント登録 ──────────────────────────────────────────────
FONT_PATH = "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"
FONT_PATH_P = "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf"
pdfmetrics.registerFont(TTFont("IPAGothic", FONT_PATH))
pdfmetrics.registerFont(TTFont("IPAPGothic", FONT_PATH_P))

# ── カラーパレット ─────────────────────────────────────────────
NAVY      = colors.HexColor("#0D1B2A")
NAVY_MID  = colors.HexColor("#162236")
NAVY_LIGHT= colors.HexColor("#1E3050")
GOLD      = colors.HexColor("#C9A84C")
GOLD_LIGHT= colors.HexColor("#E8C97A")
GOLD_PALE = colors.HexColor("#F5E6C0")
WHITE     = colors.white
OFF_WHITE = colors.HexColor("#F8F6F0")
GRAY_LIGHT= colors.HexColor("#E8E4DC")
GRAY_TEXT = colors.HexColor("#555555")
DARK_TEXT = colors.HexColor("#1A1A1A")

PAGE_W, PAGE_H = A4  # 595.27 x 841.89 pt

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# カスタム Flowable: フルワイドのネイビーヘッダーブロック
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class HeaderBlock(Flowable):
    def __init__(self, width, height=200):
        super().__init__()
        self.width  = width
        self.height = height

    def draw(self):
        c = self.canv
        w, h = self.width, self.height

        # 背景グラデーション風（濃紺→やや明るい紺）
        c.setFillColor(NAVY)
        c.rect(0, 0, w, h, fill=1, stroke=0)

        # ゴールドの細いラインアクセント（上下）
        c.setStrokeColor(GOLD)
        c.setLineWidth(1.2)
        c.line(0, h - 1, w, h - 1)
        c.line(0, 1, w, 1)

        # ── Personal Trainer 上村 徹（右上） ──
        c.setFont("IPAGothic", 8)
        c.setFillColor(GOLD_LIGHT)
        c.drawRightString(w - 12, h - 22, "Personal Trainer  上村 徹")

        # ── ゴールドの装飾ライン（タイトル上下） ──
        c.setStrokeColor(GOLD)
        c.setLineWidth(0.6)
        c.line(w * 0.1, h - 52, w * 0.9, h - 52)

        # ── メインタイトル ──
        c.setFont("IPAGothic", 28)
        c.setFillColor(WHITE)
        title = "完全専属プレミアムプラン"
        c.drawCentredString(w / 2, h - 88, title)

        # ── サブタイトル ──
        c.setFont("IPAGothic", 11)
        c.setFillColor(GOLD_LIGHT)
        c.drawCentredString(w / 2, h - 112, "田中麗様のためのフルサポートプログラム")

        # ── 装飾ライン ──
        c.line(w * 0.1, h - 122, w * 0.9, h - 122)

        # ── 価格テキスト（小） ──
        c.setFont("IPAGothic", 9)
        c.setFillColor(GRAY_LIGHT)
        c.drawCentredString(w / 2, h - 143, "月額 400,000円  ／  4ヶ月間総額 1,600,000円")

        # ── 大きな価格表示 ──
        c.setFont("IPAGothic", 40)
        c.setFillColor(GOLD)
        c.drawCentredString(w / 2, h - 182, "¥ 400,000")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# セクションヘッダー（左帯 + テキスト）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class SectionHeader(Flowable):
    def __init__(self, text, width):
        super().__init__()
        self.text  = text
        self.width = width
        self.height = 28

    def draw(self):
        c = self.canv
        w, h = self.width, self.height

        # 背景バー
        c.setFillColor(NAVY)
        c.roundRect(0, 2, w, h - 2, 3, fill=1, stroke=0)

        # 左ゴールドアクセント
        c.setFillColor(GOLD)
        c.roundRect(0, 2, 5, h - 2, 2, fill=1, stroke=0)

        # テキスト
        c.setFont("IPAGothic", 13)
        c.setFillColor(WHITE)
        c.drawString(16, 10, self.text)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# キャッチフレーズブロック
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class CatchBlock(Flowable):
    def __init__(self, text, width):
        super().__init__()
        self.text  = text
        self.width = width
        self.height = 44

    def draw(self):
        c = self.canv
        w, h = self.width, self.height

        # 背景
        c.setFillColor(GOLD_PALE)
        c.roundRect(0, 0, w, h, 4, fill=1, stroke=0)

        # ゴールドボーダー
        c.setStrokeColor(GOLD)
        c.setLineWidth(1.2)
        c.roundRect(0, 0, w, h, 4, fill=0, stroke=1)

        # 左右の装飾
        c.setFillColor(GOLD)
        c.rect(0, 0, 4, h, fill=1, stroke=0)
        c.rect(w - 4, 0, 4, h, fill=1, stroke=0)

        # テキスト
        c.setFont("IPAGothic", 13)
        c.setFillColor(NAVY)
        c.drawCentredString(w / 2, 14, self.text)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ロードマップカード
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class RoadmapCard(Flowable):
    def __init__(self, number, phase_label, period, body_lines, width, bg_color):
        super().__init__()
        self.number      = number
        self.phase_label = phase_label
        self.period      = period
        self.body_lines  = body_lines
        self.width       = width
        self.bg_color    = bg_color
        # 高さを動的計算
        self.height = 28 + len(body_lines) * 16 + 14

    def draw(self):
        c = self.canv
        w, h = self.width, self.height

        # 背景
        c.setFillColor(self.bg_color)
        c.roundRect(0, 0, w, h, 5, fill=1, stroke=0)

        # 左のゴールドアクセントバー
        c.setFillColor(GOLD)
        c.roundRect(0, 0, 6, h, 3, fill=1, stroke=0)

        # サークル番号エリア（左）
        cx, cy = 48, h / 2
        c.setFillColor(GOLD)
        c.circle(cx, cy, 20, fill=1, stroke=0)
        c.setFont("IPAGothic", 16)
        c.setFillColor(NAVY)
        c.drawCentredString(cx, cy - 6, self.number)

        # フェーズラベル
        c.setFont("IPAGothic", 8)
        c.setFillColor(GOLD_LIGHT)
        c.drawCentredString(cx, cy - 18, self.phase_label)

        # 期間テキスト
        c.setFont("IPAGothic", 10)
        c.setFillColor(WHITE)
        c.drawString(84, h - 18, self.period)

        # 本文
        c.setFont("IPAGothic", 9)
        c.setFillColor(GRAY_LIGHT)
        for i, line in enumerate(self.body_lines):
            c.drawString(84, h - 34 - i * 16, line)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# フッターブロック
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class FooterBlock(Flowable):
    def __init__(self, width):
        super().__init__()
        self.width  = width
        self.height = 36

    def draw(self):
        c = self.canv
        w, h = self.width, self.height
        c.setFillColor(NAVY)
        c.rect(0, 0, w, h, fill=1, stroke=0)
        c.setStrokeColor(GOLD)
        c.setLineWidth(0.8)
        c.line(0, h - 1, w, h - 1)
        c.setFont("IPAGothic", 8)
        c.setFillColor(GOLD_LIGHT)
        c.drawCentredString(w / 2, 13, "Personal Trainer 上村 徹  ｜  完全専属プレミアムプラン  ｜  Confidential")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PDF 生成メイン
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def build_pdf(output_path):
    L = 18 * mm
    R = 18 * mm
    T = 12 * mm
    B = 16 * mm

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=L, rightMargin=R,
        topMargin=T, bottomMargin=B,
        title="完全専属プレミアムプラン",
        author="Personal Trainer 上村 徹",
    )

    content_w = PAGE_W - L - R - 12  # subtract frame inner padding (6pt each side)
    story     = []

    # ── ヘッダーブロック ─────────────────────────────────────
    story.append(HeaderBlock(content_w, height=205))
    story.append(Spacer(1, 10))

    # ── キャッチフレーズ ──────────────────────────────────────
    story.append(CatchBlock('"田中様の時間に、私が完全に合わせます。"', content_w))
    story.append(Spacer(1, 14))

    # ── サービス内容 セクションヘッダー ──────────────────────
    story.append(SectionHeader("サービス内容", content_w))
    story.append(Spacer(1, 6))

    # サービステーブルデータ
    services = [
        ("早朝ウォーキング・ジョギング同行",
         "毎日対応可 ／ 田中様ご自宅周辺 ／ 朝3時〜\n日数は田中様が選択"),
        ("出張パーソナルトレーニング",
         "週2回 ／ 西宮ビットネス\nウェイトトレーニング & 有酸素運動"),
        ("田中様専用ストレッチ動画作成",
         "3本セット（朝・仕事の合間・寝る前）\niMessageで納品"),
        ("外食メニューサポート",
         "行きつけの店別・最適メニュー選び\nシート作成"),
        ("飲酒最適化サポート",
         "禁酒なし・無理なくビール350ml×2本への移行からスタート"),
        ("iPhoneヘルスケア",
         "1日の歩数目標 10,000歩\n1日の終わりに報告いただきます"),
        ("更年期ケア対応プログラム",
         "毎回のトレーニングに組み込み\n症状に合わせて調整"),
        ("犬の散歩活用プログラム",
         "1日4回の散歩を運動に組み込む\n歩き方・ルーティン提案"),
        ("体調日報（iMessage）",
         "毎朝2:30起床後すぐ・専用フォーマットで報告"),
        ("iMessageでサポート",
         "相談し放題"),
        ("月次レポート",
         "目標進捗・体調変化・翌月の改善提案"),
        ("従業員向けボクシング体験",
         "月1回・工場出張・4名以内・ストレス発散目的"),
    ]

    # スタイル定義
    svc_name_style = ParagraphStyle(
        "SvcName",
        fontName="IPAGothic",
        fontSize=9,
        textColor=NAVY,
        leading=14,
        spaceAfter=0,
    )
    svc_detail_style = ParagraphStyle(
        "SvcDetail",
        fontName="IPAGothic",
        fontSize=8.5,
        textColor=GRAY_TEXT,
        leading=13,
        spaceAfter=0,
    )

    table_data = []
    for i, (name, detail) in enumerate(services):
        name_para   = Paragraph(name, svc_name_style)
        detail_para = Paragraph(detail.replace("\n", "<br/>"), svc_detail_style)
        table_data.append([name_para, detail_para])

    col_widths = [130, content_w - 130]
    svc_table = Table(table_data, colWidths=col_widths, repeatRows=0)

    svc_table.setStyle(TableStyle([
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",  (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0,0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",(0, 0), (-1, -1), 6),
        ("LINEBELOW",   (0, 0), (-1, -2), 0.4, GRAY_LIGHT),
        ("BOX",         (0, 0), (-1, -1), 1.0, GOLD),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [OFF_WHITE, WHITE]),
    ]))

    story.append(svc_table)
    story.append(Spacer(1, 16))

    # ── 目標達成ロードマップ ──────────────────────────────────
    story.append(SectionHeader("目標達成ロードマップ", content_w))
    story.append(Spacer(1, 8))

    roadmap_items = [
        {
            "number": "①",
            "phase":  "土台づくり",
            "period": "1ヶ月目",
            "body": [
                "運動習慣の構築。肩甲骨まわり・全身の筋肉を動かしながらほぐす。",
                "飲酒量を無理なく最適化。体調・更年期状態をiMessageで毎日把握。",
                "第1回従業員ボクシング体験レッスン実施",
            ],
            "bg": NAVY,
        },
        {
            "number": "②",
            "phase":  "強化期",
            "period": "2〜3ヶ月目",
            "body": [
                "ウォーキングからジョギングへ段階的に移行。ウェイトトレーニング本格化。",
                "筋力・体力の向上を実感。更年期症状（倦怠感・肩こり）の改善を実感。",
            ],
            "bg": NAVY_MID,
        },
        {
            "number": "③",
            "phase":  "結果期",
            "period": "4ヶ月目",
            "body": [
                "20分続けて走れることが可能に。筋力アップ、体型の変化が目に見える。",
                "ストレス発散ルーティン完成。更年期症状がコントロールできている状態へ。",
            ],
            "bg": NAVY_LIGHT,
        },
    ]

    for item in roadmap_items:
        card = RoadmapCard(
            number=item["number"],
            phase_label=item["phase"],
            period=item["period"],
            body_lines=item["body"],
            width=content_w,
            bg_color=item["bg"],
        )
        story.append(card)
        story.append(Spacer(1, 6))

    story.append(Spacer(1, 8))

    # ── フッター ─────────────────────────────────────────────
    story.append(FooterBlock(content_w))

    doc.build(story)
    print(f"✅ PDF生成完了: {output_path}")


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "premium_plan_tanaka.pdf")
    build_pdf(out)
