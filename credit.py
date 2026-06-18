#!/usr/bin/env python3
"""
AI硬件瓶颈雷达 · 信用·杠杆危机前兆监控（雷曼型）

核心论点：别盯日経 PER 找顶，盯 AI 相关信用利差与 GPU 抵押贷款再融资。
雷曼的本质是信用·杠杆危机，不是估值危机——信用市场比股市早半年到一年示警。

本脚本抓取信用市场领先指标，按「信用危机临界度」打分，写入 credit.js。
数据源：FRED（信用利差 OAS，首选）+ Yahoo Finance（股价/MOVE/汇率/利差代理）。
FRED 抓不到时自动退回 HYG/LQD 利差代理。

用法: python credit.py   →   输出 credit.js
依赖: 仅标准库
"""
import io
import json
import sys
import time
from pathlib import Path
import urllib.request
import urllib.parse

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = Path(__file__).parent
OUT_JS = ROOT / 'credit.js'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'


def http_get(url, timeout=20):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': '*/*'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode('utf-8', errors='ignore')


def yahoo_series(symbol, range_='1y', interval='1d'):
    url = (f'https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(symbol)}'
           f'?interval={interval}&range={range_}')
    data = json.loads(http_get(url))
    r = data['chart']['result'][0]
    ts = r['timestamp']
    closes = r['indicators']['quote'][0]['close']
    out = [(ts[i], closes[i]) for i in range(len(ts)) if closes[i] is not None]
    return out, r.get('meta', {})


def fred_latest(series_id, timeout=15):
    """从 FRED 抓取最新值 + 约1月前值（用于算变动）。失败返回 None。"""
    url = f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}'
    csv = http_get(url, timeout=timeout)
    rows = []
    for line in csv.strip().split('\n')[1:]:
        parts = line.split(',')
        if len(parts) >= 2 and parts[1] not in ('', '.'):
            try:
                rows.append((parts[0], float(parts[1])))
            except ValueError:
                pass
    if not rows:
        return None
    last_date, last_val = rows[-1]
    prev_val = rows[-22][1] if len(rows) >= 22 else (rows[0][1] if rows else None)
    return {'date': last_date, 'value': last_val, 'prev': prev_val}


def lerp(v, lo, hi, lo_s, hi_s):
    if v <= lo:
        return lo_s
    if v >= hi:
        return hi_s
    return lo_s + (v - lo) / (hi - lo) * (hi_s - lo_s)


def drawdown_from_high(closes):
    hi = max(closes)
    last = closes[-1]
    return (last - hi) / hi * 100, hi, last  # 负数=回撤幅度


def pct_change_over(closes, n):
    if len(closes) <= n:
        n = len(closes) - 1
    if n <= 0:
        return 0.0
    return (closes[-1] - closes[-1 - n]) / closes[-1 - n] * 100


# ---------- 打分函数 ----------
def score_hy_oas(bp):
    if bp < 300: return lerp(bp, 200, 300, 5, 12)
    if bp < 450: return lerp(bp, 300, 450, 12, 35)
    if bp < 600: return lerp(bp, 450, 600, 35, 58)
    if bp < 800: return lerp(bp, 600, 800, 58, 80)
    return min(96, lerp(bp, 800, 1200, 80, 96))


def score_hyg_lqd(decline_pct):  # decline_pct = HY/IG 比值距6月高点的下跌幅度(正数)
    d = abs(decline_pct)
    if d < 2: return lerp(d, 0, 2, 10, 18)
    if d < 5: return lerp(d, 2, 5, 18, 42)
    if d < 10: return lerp(d, 5, 10, 42, 66)
    if d < 18: return lerp(d, 10, 18, 66, 86)
    return min(96, lerp(d, 18, 30, 86, 96))


def score_move(v):
    if v < 80: return lerp(v, 50, 80, 8, 18)
    if v < 100: return lerp(v, 80, 100, 18, 38)
    if v < 130: return lerp(v, 100, 130, 38, 64)
    if v < 160: return lerp(v, 130, 160, 64, 86)
    return min(96, lerp(v, 160, 200, 86, 96))


def score_drawdown(dd):  # dd 为负数
    d = abs(dd)
    if d < 10: return lerp(d, 0, 10, 10, 20)
    if d < 25: return lerp(d, 10, 25, 20, 42)
    if d < 40: return lerp(d, 25, 40, 42, 64)
    if d < 60: return lerp(d, 40, 60, 64, 86)
    return min(96, lerp(d, 60, 80, 86, 96))


def score_jpy_appreciation(chg_pct):  # chg_pct: USD/JPY 近20日%变动，负=円高
    if chg_pct >= 0: return lerp(chg_pct, 0, 5, 22, 12)
    c = abs(chg_pct)
    if c < 3: return lerp(c, 0, 3, 22, 42)
    if c < 6: return lerp(c, 3, 6, 42, 66)
    if c < 10: return lerp(c, 6, 10, 66, 88)
    return min(96, lerp(c, 10, 16, 88, 96))


def stage(score):
    if score < 25: return (1, '平静 (Calm)', '#22c55e', '信用市场正常')
    if score < 50: return (2, '利差走阔 (Widening)', '#eab308', '开始示警·留意')
    if score < 75: return (3, '信用收缩 (Contraction)', '#f97316', '警戒·减杠杆')
    return (4, '雷曼型临界 (Lehman-type)', '#ef4444', '信用冻结风险')


def main():
    print('[credit] fetching credit-market leading indicators...', flush=True)
    indicators = []

    # 1) HY 信用利差 OAS —— FRED 首选, 失败退回 HYG/LQD 代理
    hy_oas = None
    try:
        hy_oas = fred_latest('BAMLH0A0HYM2')
    except Exception as e:
        print(f'  FRED HY OAS 不可达 ({str(e)[:40]})，将用 HYG/LQD 代理', flush=True)
    if hy_oas:
        bp = hy_oas['value'] * 100  # FRED 单位是百分点, 转 bp
        prev_bp = (hy_oas['prev'] or hy_oas['value']) * 100
        chg = bp - prev_bp
        indicators.append({
            'key': 'hy_oas', 'name': 'HY 信用利差 (ICE BofA OAS)',
            'display': f'{bp:.0f} bp  ({"+" if chg>=0 else ""}{chg:.0f} bp / 1月)',
            'score': round(score_hy_oas(bp), 1), 'weight': 1.6,
            'reason': '最领先·信用市场比股市早半年示警', 'src': 'FRED',
        })

    # 2) HY/IG 相对强度 (HYG/LQD) —— 利差代理, 始终可用
    try:
        hyg, _ = yahoo_series('HYG', '1y')
        lqd, _ = yahoo_series('LQD', '1y')
        n = min(len(hyg), len(lqd))
        ratio = [hyg[-n+i][1] / lqd[-n+i][1] for i in range(n)]
        win = ratio[-126:] if len(ratio) >= 126 else ratio  # ~6个月
        hi = max(win); cur = ratio[-1]
        decline = (cur - hi) / hi * 100  # 负数
        indicators.append({
            'key': 'hyg_lqd', 'name': 'HY/IG 相对强度 (HYG÷LQD)',
            'display': f'距6月高点 {decline:+.1f}%',
            'score': round(score_hyg_lqd(decline), 1), 'weight': 1.4,
            'reason': '比值下跌=高收益债跑输=信用利差走阔', 'src': 'Yahoo',
        })
    except Exception as e:
        print(f'  HYG/LQD FAIL {e}', flush=True)

    # 3) MOVE 债市波动率
    try:
        move, _ = yahoo_series('^MOVE', '1y')
        v = move[-1][1]
        indicators.append({
            'key': 'move', 'name': 'MOVE 债市波动率',
            'display': f'{v:.1f}', 'score': round(score_move(v), 1), 'weight': 1.2,
            'reason': '债市"恐慌指数"·信用应力直接读数', 'src': 'Yahoo',
        })
    except Exception as e:
        print(f'  MOVE FAIL {e}', flush=True)

    # 4) Oracle 回撤 —— "贝尔斯登候选"
    try:
        orcl, _ = yahoo_series('ORCL', '1y')
        dd, hi, last = drawdown_from_high([c for _, c in orcl])
        indicators.append({
            'key': 'orcl', 'name': 'Oracle 回撤 (距52周高)',
            'display': f'{dd:+.1f}%  (${last:.0f})',
            'score': round(score_drawdown(dd), 1), 'weight': 1.3,
            'reason': '循环融资/AI债务"贝尔斯登候选"·CDS已飙升', 'src': 'Yahoo',
        })
    except Exception as e:
        print(f'  ORCL FAIL {e}', flush=True)

    # 5) CoreWeave 回撤 —— GPU 抵押贷款发行人
    try:
        crwv, _ = yahoo_series('CRWV', '1y')
        dd, hi, last = drawdown_from_high([c for _, c in crwv])
        indicators.append({
            'key': 'crwv', 'name': 'CoreWeave 回撤 (距52周高)',
            'display': f'{dd:+.1f}%  (${last:.0f})',
            'score': round(score_drawdown(dd), 1), 'weight': 1.1,
            'reason': 'GPU抵押贷款·11%利率·2026起还款碰上抵押品贬值', 'src': 'Yahoo',
        })
    except Exception as e:
        print(f'  CRWV FAIL {e}', flush=True)

    # 6) USD/JPY 急升信号 —— 对日本的传导确认
    try:
        jpy, _ = yahoo_series('JPY=X', '6mo')
        closes = [c for _, c in jpy]
        chg20 = pct_change_over(closes, 20)
        indicators.append({
            'key': 'usdjpy_move', 'name': 'USD/JPY 近20日变动',
            'display': f'{chg20:+.1f}%  (¥{closes[-1]:.1f})',
            'score': round(score_jpy_appreciation(chg20), 1), 'weight': 1.0,
            'reason': '急速円高=危机向日本传导(2008:107→90)·出口利润蒸发', 'src': 'Yahoo',
        })
    except Exception as e:
        print(f'  USDJPY FAIL {e}', flush=True)

    # 综合分（加权平均）
    tw = sum(i['weight'] for i in indicators)
    auto_score = sum(i['score'] * i['weight'] for i in indicators) / tw if tw else 0
    snum, slabel, scolor, snote = stage(auto_score)

    out = {
        'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'auto_score': round(auto_score, 1),
        'stage_num': snum, 'stage_label': slabel, 'stage_color': scolor, 'stage_note': snote,
        'fred_ok': hy_oas is not None,
        'thesis': '雷曼=信用·杠杆危机，非估值危机。别盯日経 PER 找顶，盯 AI 信用利差与 GPU 抵押贷款再融资——信用市场会先告诉你。',
        'transmission': '若引爆：路径同 2008 = 急速円高 + 出口利润蒸发。你的持仓(5803 フジクラ/5016 JX 等)处 AI capex 受益链下游——信用驱动的 capex 冻结会经①订单取消 ②円高 双重打击，故以 USD/JPY 急升作二次确认。',
        'indicators': indicators,
        'manual_checklist': [
            {'key': 'orcl_cds',   'label': 'Oracle 5Y CDS > 150bp（信用市场重定价）', 'weight': 14,
             'link': 'https://www.google.com/search?q=Oracle+5+year+CDS+spread'},
            {'key': 'gpu_refi',   'label': 'GPU抵押贷款(CoreWeave类)再融资失败/利率飙升', 'weight': 14,
             'link': 'https://www.google.com/search?q=CoreWeave+debt+refinancing'},
            {'key': 'pc_redeem',  'label': '私募信贷基金 赎回冻结 / 大幅减记', 'weight': 13,
             'link': 'https://www.google.com/search?q=private+credit+fund+redemption+freeze+markdown'},
            {'key': 'capex_gap',  'label': '超大厂 capex 翻倍指引触发抛售(如 Alphabet)', 'weight': 11,
             'link': 'https://www.google.com/search?q=hyperscaler+capex+free+cash+flow+gap'},
            {'key': 'circular',   'label': '循环融资被揭示为"圈内打转"(Nvidia↔OpenAI↔CoreWeave)', 'weight': 12,
             'link': 'https://www.google.com/search?q=Nvidia+OpenAI+circular+financing'},
            {'key': 'bank_expo',  'label': '杠杆传导至储户银行体系(→升级为系统性)', 'weight': 14,
             'link': 'https://www.google.com/search?q=banks+exposure+AI+data+center+private+credit'},
            {'key': 'jpy_spike',  'label': 'USD/JPY 单周急升 >5%(carry unwind 确认)', 'weight': 10,
             'link': 'https://finance.yahoo.com/quote/JPY=X'},
        ],
    }

    js = (f'/* Auto-generated by credit.py at {out["generated_at"]} */\n'
          f'window.CREDIT_DATA = {json.dumps(out, ensure_ascii=False, indent=2)};\n')
    OUT_JS.write_text(js, encoding='utf-8')

    print(f'[credit] auto score {auto_score:.1f} = {slabel}  (FRED {"OK" if hy_oas else "代理"})', flush=True)
    for i in indicators:
        print(f'  - {i["name"]:32s} {i["display"]:28s} score {i["score"]}', flush=True)
    print(f'[credit] Done -> {OUT_JS.name}', flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
