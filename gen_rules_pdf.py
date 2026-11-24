#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成《交易规则手册》PDF"""
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from fpdf.fonts import FontFace
from fpdf.enums import TableCellFillMode

FONT = "/Library/Fonts/Arial Unicode.ttf"
OUT = "/Users/yanansun/WorkBuddy/2026-10-12-01-49-36/交易规则手册.pdf"

INK = (28, 32, 38)
MUTE = (108, 116, 128)
ACCENT = (176, 42, 42)
LINE = (206, 212, 220)
BG = (244, 246, 249)


class Doc(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("CN", size=7.5)
        self.set_text_color(*MUTE)
        self.cell(0, 6, "交易规则手册 · v1.0 · 2026-11-19",
                  align="L", new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.cell(0, 6, "账户：300,000 元商品期货与期权", align="R")
        self.ln(7)
        self.set_draw_color(*LINE)
        self.set_line_width(0.2)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-14)
        self.set_font("CN", size=7.5)
        self.set_text_color(*MUTE)
        self.cell(0, 6, f"第 {self.page_no()} 页 / 共 {{nb}} 页", align="C")


pdf = Doc(format="A4")
pdf.set_margins(18, 16, 18)
pdf.set_auto_page_break(True, margin=20)
pdf.add_font("CN", "", FONT)
pdf.alias_nb_pages()

W = pdf.w - pdf.l_margin - pdf.r_margin


def h1(num, text, sub=""):
    pdf.ln(3)
    pdf.set_x(pdf.l_margin)
    pdf.set_fill_color(*ACCENT)
    pdf.rect(pdf.l_margin, pdf.get_y(), 1.6, 8, style="F")
    pdf.set_x(pdf.l_margin + 5)
    pdf.set_font("CN", size=14)
    pdf.set_text_color(*INK)
    pdf.cell(12, 8, num, new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(0, 8, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    if sub:
        pdf.set_x(pdf.l_margin + 5)
        pdf.set_font("CN", size=8)
        pdf.set_text_color(*MUTE)
        pdf.cell(0, 5, sub, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(*INK)
    pdf.ln(2)


def h2(text):
    pdf.ln(1.5)
    pdf.set_x(pdf.l_margin)
    pdf.set_font("CN", size=10.5)
    pdf.set_text_color(*ACCENT)
    pdf.cell(0, 6.5, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(*INK)
    pdf.ln(1)


def body(text, size=9, indent=0, gap=1.6):
    pdf.set_font("CN", size=size)
    pdf.set_text_color(*INK)
    pdf.set_x(pdf.l_margin + indent)
    pdf.multi_cell(W - indent, 5.2, text, align="L", wrapmode="CHAR", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(gap)


def rule(no, title, text):
    """规则条目：编号 + 标题 + 说明"""
    if pdf.get_y() > pdf.h - 34:
        pdf.add_page()
    y0 = pdf.get_y()
    pdf.set_font("CN", size=9.6)
    pdf.set_text_color(*ACCENT)
    pdf.cell(15, 5.6, no, new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.set_text_color(*INK)
    pdf.set_font("CN", size=9.6)
    pdf.multi_cell(W - 15, 5.6, title, align="L", wrapmode="CHAR", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    if text:
        pdf.set_font("CN", size=8.8)
        pdf.set_text_color(60, 66, 74)
        pdf.set_x(pdf.l_margin + 15)
        pdf.multi_cell(W - 15, 5.0, text, align="L", wrapmode="CHAR", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_text_color(*INK)
    pdf.ln(1.4)


def table(rows, widths, header=True, size=8.6, align=None):
    pdf.set_font("CN", size=size)
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(*LINE)
    pdf.set_line_width(0.2)
    with pdf.table(
        col_widths=widths,
        text_align=align or tuple(["LEFT"] * len(widths)),
        line_height=size * 0.62,
        padding=1.6,
        borders_layout="HORIZONTAL_LINES",
        first_row_as_headings=header,
        headings_style=FontFace(emphasis="", color=(255, 255, 255),
                                fill_color=(58, 64, 74)),
    ) as t:
        for i, r in enumerate(rows):
            row = t.row()
            for j, c in enumerate(r):
                row.cell(str(c))
    pdf.ln(2)


# ============ 封面 ============
pdf.add_page()
pdf.ln(38)
pdf.set_font("CN", size=9)
pdf.set_text_color(*MUTE)
pdf.cell(0, 6, "DISCIPLINE  /  交易纪律", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.ln(4)
pdf.set_font("CN", size=30)
pdf.set_text_color(*INK)
pdf.cell(0, 14, "交易规则手册", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.ln(2)
pdf.set_font("CN", size=11)
pdf.set_text_color(*MUTE)
pdf.cell(0, 7, "账户纪律 · 入场 · 止损 · 套利 · 期权 · 自检清单",
         new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.ln(10)
pdf.set_draw_color(*ACCENT)
pdf.set_line_width(0.8)
pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + 46, pdf.get_y())
pdf.ln(12)

pdf.set_font("CN", size=9)
pdf.set_text_color(*INK)
info = [
    ("版本", "v1.0"),
    ("生效日期", "2026-11-19"),
    ("适用范围", "300,000 元商品期货 + 商品期权账户"),
    ("交易所", "郑商所 / 大商所 / 上期所 / 广期所"),
    ("规则条数", "仓位 6 条 · 入场 7 条 · 止损 5 条 · 套利 4 条 · 期权 7 条"),
]
for k, v in info:
    pdf.set_text_color(*MUTE)
    pdf.cell(30, 6.4, k, new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.set_text_color(*INK)
    pdf.cell(0, 6.4, v, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

pdf.ln(16)
pdf.set_fill_color(*BG)
pdf.rect(pdf.l_margin, pdf.get_y(), W, 26, style="F")
pdf.set_xy(pdf.l_margin + 6, pdf.get_y() + 5)
pdf.set_font("CN", size=9)
pdf.set_text_color(*MUTE)
pdf.multi_cell(W - 12, 5.4,
               "本手册只做一件事：把已经写下来的规矩固定住，避免在持仓压力下临时改判。\n"
               "规则可以修订，但修订必须显式发生、重新论证，不能靠行情走势事后豁免。",
               align="L", wrapmode="CHAR", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

# ============ 第一章 账户与仓位 ============
pdf.add_page()
h1("01", "账户与仓位规则", "长期有效，不随单笔交易调整")

h2("1.1 基本参数")
table([
    ["项目", "数值 / 规则"],
    ["总资金", "300,000 元（2026-11-09 由 20 万上调）"],
    ["1 份仓位", "20,000 元 = 6.7%"],
    ["单策略上限", "3 份 = 60,000 元 = 20%"],
    ["组合总占用上限", "60% = 180,000 元"],
    ["保证金标准", "交易所保证金 + 0（券商不加收）"],
], widths=(46, 116))

h2("1.2 止损预算")
table([
    ["仓位", "止损预算（占用的 10%）"],
    ["1 份（20,000）", "2,000 元"],
    ["2 份（40,000）", "4,000 元"],
    ["3 份（60,000）", "6,000 元"],
], widths=(60, 102))

body("止损预算取绝对值固定，不随资金放大 —— 相对 30 万本金已自动降杠杆。"
     "上调资金不意味着放宽单笔止损金额，只意味着可以容纳更多独立策略。", size=8.8)

h2("1.3 仓位门槛")
rule("R1", "仓位金额不构成否决理由",
     "保证金 ≤ 60,000 元即进入实盘评估，只看三件事：路径检验胜率、赔率、状态条件。"
     "不得以“仓位太重”“金额太大”作为否决理由。")
rule("R2", "3 份仓位额外要求",
     "动用 3 份（60,000 元）时，额外要求赔率 ≥ 1.2 且已完成逐日路径检验。"
     "未做路径检验的交易最多 2 份。")

h2("1.4 期权卖方定仓（2026-11-06 定）")
body("品种预算：常规 30,000 元 / 最多 60,000 元。", size=8.8, gap=0.8)
body("禁止用保证金定仓。可开张数按压力亏损计算：", size=8.8, gap=0.8)
pdf.set_fill_color(*BG)
pdf.rect(pdf.l_margin, pdf.get_y(), W, 11, style="F")
pdf.set_xy(pdf.l_margin + 5, pdf.get_y() + 3)
pdf.set_font("CN", size=9)
pdf.multi_cell(W - 10, 5,
               "可开张数 =（品种预算 − 同品种其他策略已占用止损额度）÷ 单张压力亏损",
               align="L", wrapmode="CHAR", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.ln(2)
body("压力档统一取标的 +22%（卖方最痛的方向）。报价必须同时给出两个口径：", size=8.8, gap=0.8)
table([
    ["口径", "含义", "常见误判"],
    ["保证金占用", "交易所收取的履约保证", "看着只用了一半"],
    ["压力亏损", "标的 +22% 时的实际亏损", "往往已经用满甚至超支"],
], widths=(34, 76, 52), size=8.4)
body("保证金口径与压力亏损口径必须并列报出。保证金看起来只用一半时，风险常常已经用满。",
     size=8.8)

# ============ 第二章 入场纪律 ============
pdf.add_page()
h1("02", "入场纪律", "决定“能不能进”，与仓位大小无关")

rule("E1", "入场开关必须是状态变量",
     "基差、库存、开工率、产能、通关车数、现货涨跌 —— 只有状态变量才能当开关。"
     "价格只是执行位，不是理由。（L-PP 11-02：原油崩盘误触发）")
rule("E2", "开仓前必须写下归因",
     "写下“这笔钱赚的是谁的、为什么现在赚”。归因被证伪时先重估论点，不要只盯止损线。"
     "（J-JM 11-18：归因写的是供给，实际驱动是需求负反馈）")
rule("E3", "双窗口一致性",
     "250 日 z 与全历史 z 必须同向，且均 > 1.5 才算候选。"
     "两个窗口方向相反时，说明窗口被某段极端行情污染，结论不成立。")
rule("E4", "20 日胜率门槛",
     "历史 20 日胜率 < 60% 的形态不进实盘。胜率不足的形态只能观察。")
rule("E5", "整数关口留缺口",
     "挂单不要贴在整数位，留 1-2 点缺口。（JM 三次止步 1,439）")
rule("E6", "赔率门槛",
     "一般交易赔率 ≥ 1.2；3 份仓位要求赔率 ≥ 1.2 且已完成路径检验。"
     "赔率 = 目标点数 ÷ 止损点数，两端都必须用同一口径的点值。")
rule("E7", "引用数据前先确认日期",
     "库存、基差、开工率必须核对数据截止日。旧数据不得当现状使用。"
     "（MA 40.7 万吨旧数据案例）")

# ============ 第三章 止损与硬线 ============
h1("03", "止损与硬线", "这一章是全部规则里最不能通融的部分")

rule("S1", "止损宽度 ≥ 历史最大逆行",
     "止损不能凭感觉设。价差套利必须做逐日路径检验，止损宽度必须大于历史最大逆行。"
     "（L-PP：1σ = 49 点，真实逆行 −211 点 → 必被扫）")
rule("S2", "止损紧贴现价 = 接受跳空成本",
     "止损贴在现价附近，等价于把跳空风险全额承担。处置只有两条：日内减半，或留足振幅。"
     "（SI、FG 卖权两次验证）")

h2("3.1 硬线的两层含义必须分开（J-JM 11-18 教训）")
table([
    ["类型", "定义", "确认方式", "举例"],
    ["止损线", "风险容忍度", "价格 + 时间确认（收盘站稳 / 持续 N 分钟）", "fee 560 收盘全平"],
    ["论点作废线", "状态变量切换", "可验证的状态变量（车数 / 库存 / 开工 / 现货止涨）",
     "甘其毛都通关车数跌破阈值"],
], widths=(26, 40, 66, 30), size=8.2)
pdf.ln(1)
body("把两层含义绑在同一个价格上，就会出现“38 分钟脉冲破线即宣称论点作废”的错误。"
     "脉冲最高价创出但收盘未站稳，不构成止损触发；而当日基本面恰恰显示所假设的状态变量在减弱。",
     size=8.8)
body("禁止：用结果（价格收回来）事后豁免已触发的硬线 —— 这是挪线。"
     "正确处置只有两种：按纪律执行，或明确声明“这是主动改规则”并重新论证新规则。"
     "不能既不平仓、又不改规则、还用事后走势自我安慰。", size=8.8)

rule("S3", "持仓必须逐腿列示",
     "两腿分开写，禁止只写“合计”。合计会掩盖单腿的尾部风险。")
rule("S4", "盈利保护线触发立即执行",
     "成本保护线、时间了结线一旦触发即执行，不因为“还差一点”而延后。"
     "（M-RM、J-JM 第一轮 1 组直接 T1 全平）")

# ============ 第四章 价差与套利 ============
h1("04", "价差与套利专项", "点值口径与路径检验")

h2("4.1 逐腿法定理（规则 17）")
body("合约吨数之比 = 手数比 = 价差系数比 时，价差 1 点的盈亏 = 单腿每手点值。"
     "ΔS 已包含两腿贡献，不可再乘 2。", size=8.8, gap=1.2)
table([
    ["情形", "处理方式", "示例"],
    ["匹配型（1:1）", "直接用单腿每手点值", "JD / FG / SH / M-RM / L-PP"],
    ["不匹配", "必须拆腿，逐腿计算", "J-JM（J − 1.3×JM）"],
], widths=(32, 64, 66), size=8.4)
body("三条铁律：", size=8.8, gap=0.8)
body("① 永不把两腿吨数相加。", size=8.8, indent=4, gap=0.4)
body("② “点值 × 手数”只能乘一次。吨/手 × 手数 = 组合点值，已含手数；再乘手数就是双计。",
     size=8.8, indent=4, gap=0.4)
body("③ 核算法则：先算「每手点数 × 每手点值 = 单手盈亏」，再乘手数。两步分开写，"
     "不要在一步里既乘吨数又乘手数。", size=8.8, indent=4, gap=1.6)
pdf.set_fill_color(*BG)
pdf.rect(pdf.l_margin, pdf.get_y(), W, 13, style="F")
pdf.set_xy(pdf.l_margin + 5, pdf.get_y() + 3.5)
pdf.set_font("CN", size=8.8)
pdf.multi_cell(W - 10, 5,
               "反例（J-JM 11-18）：JM 60 吨/手、2 手 = 120 元/点，已含手数。"
               "又乘 2 得 −2,520，把 +190 的盈利算成 −1,070。",
               align="L", wrapmode="CHAR", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.ln(2)

rule("A1", "价差套利必须做逐日路径检验",
     "不能只看终值。要逐日看“在这个止损宽度下，历史上有没有先被打掉再回来”。")
rule("A2", "季节性须按结构状态分层",
     "状态不匹配 = 伪信号。库存结构、进出口状态、深浅倒挂年份不同，季节性系数完全不同。"
     "（豆棕倒挂年、L-PP 深倒挂、棕油交割月流动性假象）")
rule("A3", "脉冲极值会回吐",
     "单腿脉冲形成的价差极值，会随脉冲消退而回吐。但趋势市中的 z 极值是动量确认，"
     "不是反转信号 —— 两者必须先分清状态。")
rule("A4", "入场位是唯一不可补的东西",
     "价差已经跑掉主要空间后追单，即使统计仍支持，赔率也会被压缩到门槛以下。"
     "错过位置就等下一次，不要用“方向还对”说服自己。")

# ============ 第五章 期权 ============
pdf.add_page()
h1("05", "期权专项", "卖 vol 与买 vol 是两套完全不同的门槛")

rule("O1", "卖波动率要求 IV/HV20 ≥ 1.17",
     "低于 1.17 说明期权没有溢价可卖。IV 与 HV 必须同口径：hitick ATM IV 用 ACT/365，"
     "与 HV(252) 比较须乘 0.8313。")
rule("O2", "触发线必须用实时盘口重算",
     "期权价格随标的和 IV 实时变化，静态触发线会失效。每次评估都要重新取盘口，"
     "并算清对冲腿的补贴。（MA P3200 已 4 次失效：137 → 161 → 222.5）")
rule("O3", "卖 put 前先算剩余溢价",
     "先算「剩余未回吐的基本面溢价」，若大于保本缓冲即否决。溢价还没吐完就卖 put，"
     "等于替多头接最后一棒。")
rule("O4", "事件日看 β/IV 位置比值",
     "中国商品期权的事件日表现是 IV 塌（与美股相反）。事件前买 vol 通常亏在 IV 塌上。")
rule("O5", "有无期权只看挂牌清单",
     "不得凭印象判断某品种有没有期权，必须以交易所挂牌清单为准。（FU 传错到期日误判）")
rule("O6", "增仓加速段不卖 call",
     "增仓加速意味着趋势资金在进场，卖出 call 的尾部风险不可控。"
     "日盘减仓收阴也可能被夜盘增仓否决。（FG 11-06）")
rule("O7", "波动率背离是体检工具，不是入场信号",
     "价涨 + IV 下降 + put 被卖方接走 + ATM call 获利了结 = 期权市场证伪“这波是恐慌对冲”。"
     "空头持仓遇到这种背离应立即离场，不等价格止损线。反向同理：价跌 IV 升 = 下跌有真筹码。"
     "背离判读的优先级高于价格形态。")
body("补充：短期 IV 高企多来自到期 gamma 泡沫（剩余 5-7 天时 ATM vega 集中），"
     "不可当作可卖的溢价。", size=8.6)

# ============ 第六章 数据与执行 ============
h1("06", "数据与执行口径", "避免因口径错误得出反向结论")

h2("6.1 行情字段")
table([
    ["来源 / 字段", "含义"],
    ["新浪 nf_ · f[8]", "最新价"],
    ["新浪 nf_ · f[10]", "昨结算"],
    ["新浪 nf_ · f[3] / f[4]", "最高 / 最低"],
    ["新浪 nf_ · f[13]", "持仓量 OI"],
    ["新浪 nf_ · f[14]", "成交量"],
    ["新浪日 K · p / v", "持仓量 / 成交量"],
], widths=(58, 104), size=8.4)
body("持仓变化相关的全部判断（增仓/减仓、单日增仓阈值、减仓下跌含义）都依赖 f[13]。此字段曾写反，"
     "导致三张卡片口径全错。", size=8.6)

h2("6.2 合约选择")
body("XX0 连续合约 ≠ 主力合约价（JD0 3,542 vs JD2701 3,147，加权口径）。"
     "算价差一律用具体月份合约。", size=8.6)

h2("6.3 夜盘清单")
table([
    ["类别", "品种"],
    ["无夜盘", "郑商所 UR / AP / CJ 等；大商所 JD / LH 等"],
    ["有夜盘", "TA / PX / FG / SH / MA / RM / CF / SR / OI / CY / PF / SO；J / JM / L / PP / CU"],
], widths=(26, 136), size=8.4)
body("无夜盘品种在晚间返回的是日盘收盘定格值，不可当夜盘行情解读。其止损与清仓只在日盘 "
     "9:00-15:00 执行，隔夜跳空无法用夜盘对冲。夜间扫盘前必须先过这张清单。", size=8.6)

h2("6.4 IV 口径")
body("hitick ATM IV 为 ACT/365；OpenVlab ATMV 为日级口径。盘中看 hitick，日级位置看 OpenVlab，"
     "两者不混用。", size=8.6)

# ============ 第七章 自检清单 ============
pdf.add_page()
h1("07", "自检清单", "下单前逐条过，任何一条不过就不进")


def checklist(items, start=1):
    for i, t in enumerate(items, start):
        pdf.set_font("CN", size=9)
        pdf.set_text_color(*ACCENT)
        pdf.cell(9, 6.2, f"{i:02d}", new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.set_text_color(*INK)
        pdf.multi_cell(W - 9, 6.2, t, align="L", wrapmode="CHAR", new_x=XPos.LMARGIN, new_y=YPos.NEXT)


h2("7.1 开仓前")
checklist([
    "归因写下来了吗？它是状态变量，还是只是价格。",
    "双窗口 z 同向且均 > 1.5 吗？",
    "赔率 ≥ 1.2 吗？（3 份要求 ≥ 1.2 且已做路径检验）",
    "止损宽度 ≥ 历史最大逆行吗？做过逐日路径检验吗？",
    "止损金额在预算内吗？（1 份 2,000 / 2 份 4,000 / 3 份 6,000）",
    "组合占用 ≤ 60% 吗？单策略 ≤ 3 份吗？",
    "该形态 20 日胜率 ≥ 60% 吗？",
    "期权：IV/HV20 ≥ 1.17 吗？触发线用实时盘口重算了吗？卖 put 算过剩余溢价吗？",
    "价位是整数关口吗？挂单留了 1-2 点缺口吗？",
])

pdf.ln(4)
h2("7.2 持仓中")
checklist([
    "这条硬线是价格线还是状态线？两层含义分开了吗？",
    "归因被证伪了吗？如果被证伪，论点还成立吗？",
    "出现波动率背离了吗？出现即离场，不等价格线。",
    "到时间线或了结线了吗？到了就执行，不延后。",
])

pdf.ln(6)
pdf.set_fill_color(*BG)
pdf.rect(pdf.l_margin, pdf.get_y(), W, 30, style="F")
pdf.set_xy(pdf.l_margin + 6, pdf.get_y() + 6)
pdf.set_font("CN", size=9.5)
pdf.set_text_color(*INK)
pdf.multi_cell(W - 12, 6,
               "规则的作用不是让你少亏一笔，而是让你在连续亏损之后仍然执行同一套动作。\n"
               "任何一次“这次情况特殊”，都必须以修订规则的方式发生，并且留下新的论证。",
               align="L", wrapmode="CHAR", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

pdf.output(OUT)
print("OK", OUT)
