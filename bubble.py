#!/usr/bin/env python3
"""
AI硬件瓶颈雷达 · 日経バブル進行度計算

从 Yahoo Finance 抓取日経/VIX/USD-JPY/US10Y 等数据，
按 Minsky 5 阶段模型给当下泡沫位置打分，写入 bubble.js。

用法:
    python bubble.py

输出: bubble.js (会被 index.html 自动加载)
"""
import io
import json
import sys
import time
from pathlib import Path
import urllib.request

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = Path(__file__).parent
OUT_JS = ROOT / 'bubble.js'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'

NIKKEI_1989_PEAK = 38915.87  # 1989-12-29 終値


def fetch(symbol, range_='10y', interval='1mo'):
    url = (f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}'
           f'?interval={interval}&range={range_}')
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())


def series(chart_resp):
    r = chart_resp['chart']['result'][0]
    ts = r['timestamp']
    closes = r['indicators']['quote'][0]['close']
    return [(ts[i], closes[i]) for i in range(len(ts)) if closes[i] is not None]


def rsi(values, period=14):
    if len(values) < period + 1:
        return None
    gains, losses = [], []
    for i in range(1, len(values)):
        d = values[i] - values[i - 1]
        gains.append(max(d, 0))
        losses.append(max(-d, 0))
    avg_g = sum(gains[-period:]) / period
    avg_l = sum(losses[-period:]) / period
    if avg_l == 0:
        return 100.0
    rs = avg_g / avg_l
    return 100 - 100 / (1 + rs)


def sma(values, period):
    if len(values) < period:
        return None
    return sum(values[-period:]) / period


def lerp(v, lo, hi, lo_s, hi_s):
    if v <= lo:
        return lo_s
    if v >= hi:
        return hi_s
    return lo_s + (v - lo) / (hi - lo) * (hi_s - lo_s)


def score_nikkei_vs_1989(close):
    pct = (close - NIKKEI_1989_PEAK) / NIKKEI_1989_PEAK * 100
    if pct < -30: s = 10
    elif pct < 0: s = lerp(pct, -30, 0, 10, 50)
    elif pct < 30: s = lerp(pct, 0, 30, 50, 75)
    elif pct < 70: s = lerp(pct, 30, 70, 75, 88)
    else: s = min(98, lerp(pct, 70, 120, 88, 96))
    return s, pct


def score_rsi(r):
    if r < 50: return 20
    if r < 60: return lerp(r, 50, 60, 20, 40)
    if r < 70: return lerp(r, 60, 70, 40, 60)
    if r < 80: return lerp(r, 70, 80, 60, 80)
    if r < 90: return lerp(r, 80, 90, 80, 95)
    return 98


def score_sma_gap(g):
    if g < 0: return max(10, 30 + g)
    if g < 10: return lerp(g, 0, 10, 30, 50)
    if g < 20: return lerp(g, 10, 20, 50, 70)
    if g < 30: return lerp(g, 20, 30, 70, 85)
    return min(95, 85 + (g - 30) * 0.5)


def score_months_since_correction(m):
    if m < 6: return 20
    if m < 12: return 40
    if m < 18: return 55
    if m < 24: return 70
    if m < 36: return 85
    return 92


def score_vix(v):
    if v < 12: return 92
    if v < 14: return lerp(v, 12, 14, 92, 75)
    if v < 18: return lerp(v, 14, 18, 75, 50)
    if v < 25: return lerp(v, 18, 25, 50, 25)
    return 15


def score_usdjpy(j):
    if j < 140: return 25
    if j < 150: return lerp(j, 140, 150, 25, 50)
    if j < 160: return lerp(j, 150, 160, 50, 80)
    if j < 165: return lerp(j, 160, 165, 80, 92)
    return 95


def score_us10y(y):
    if y < 2: return 30
    if y < 3.5: return lerp(y, 2, 3.5, 30, 50)
    if y < 4.5: return lerp(y, 3.5, 4.5, 50, 75)
    if y < 5.5: return lerp(y, 4.5, 5.5, 75, 90)
    return 95


def score_ytd(p):
    if p < 0: return 15
    if p < 10: return lerp(p, 0, 10, 15, 40)
    if p < 20: return lerp(p, 10, 20, 40, 60)
    if p < 30: return lerp(p, 20, 30, 60, 85)
    return min(95, 85 + (p - 30) * 0.3)


def months_since_correction(monthly_closes, depth=0.10, lookback=60):
    recent = monthly_closes[-lookback:]
    if len(recent) < 2:
        return 0
    count = 0
    for i in range(len(recent) - 1, 0, -1):
        window = recent[max(0, i - 12):i + 1]
        local_peak = max(window)
        if recent[i] < local_peak * (1 - depth):
            return count
        count += 1
    return count


def get_stage(score):
    if score < 20: return (1, '蓄積期 (Stealth)', '#22c55e')
    if score < 40: return (2, '認知期 (Awareness)', '#84cc16')
    if score < 60: return (3, '熱狂期 (Mania)', '#eab308')
    if score < 80: return (4, '吹き上げ期 (Blow-off Top)', '#f97316')
    return (5, '崩壊予兆期 (Crash Imminent)', '#ef4444')


def main():
    print('[bubble] fetching Yahoo Finance series...', flush=True)
    n_monthly = series(fetch('^N225', 'max', '1mo'))
    n_daily = series(fetch('^N225', '2y', '1d'))
    vix_d = series(fetch('^VIX', '1mo', '1d'))
    jpy_d = series(fetch('JPY=X', '1mo', '1d'))
    tnx_d = series(fetch('^TNX', '1mo', '1d'))

    n_close = n_daily[-1][1]
    n_date = time.strftime('%Y-%m-%d', time.localtime(n_daily[-1][0]))
    indicators = []

    # 1) Nikkei vs 1989 peak
    s, pct = score_nikkei_vs_1989(n_close)
    indicators.append({
        'key': 'nikkei_vs_1989', 'name': '日経 vs 1989 峰值 (38,915)',
        'display': f'{n_close:,.0f} ({"+" if pct>=0 else ""}{pct:.1f}%)',
        'score': round(s, 1),
        'reason': '心理位 · 历史唯一参照'
    })

    # 2) Monthly RSI(14)
    m_closes = [v for _, v in n_monthly]
    m_rsi = rsi(m_closes, 14)
    if m_rsi is not None:
        indicators.append({
            'key': 'monthly_rsi', 'name': '日経 月線 RSI(14)',
            'display': f'{m_rsi:.1f}', 'score': round(score_rsi(m_rsi), 1),
            'reason': '>85 = 1989 同水準（当時 90+）'
        })

    # 3) 200日線乖離
    d_closes = [v for _, v in n_daily]
    sma200 = sma(d_closes, 200)
    if sma200:
        gap = (n_close - sma200) / sma200 * 100
        indicators.append({
            'key': 'sma200_gap', 'name': '日経 200日線乖離率',
            'display': f'{"+" if gap>=0 else ""}{gap:.1f}%',
            'score': round(score_sma_gap(gap), 1),
            'reason': '>25% 加速段共通の警告'
        })

    # 4) Months since 10% correction
    m_since = months_since_correction(m_closes, 0.10, 60)
    indicators.append({
        'key': 'months_since', 'name': '直近10%調整からの月数',
        'display': f'{m_since} ヶ月', 'score': round(score_months_since_correction(m_since), 1),
        'reason': '>18 ヶ月警戒 · 走得越久反弹越烈'
    })

    # 5) VIX
    vix_now = vix_d[-1][1]
    indicators.append({
        'key': 'vix', 'name': 'VIX (S&P 恐慌指数)',
        'display': f'{vix_now:.2f}', 'score': round(score_vix(vix_now), 1),
        'reason': '<13 极度麻痺・翻车前夜'
    })

    # 6) USD/JPY
    jpy = jpy_d[-1][1]
    indicators.append({
        'key': 'usdjpy', 'name': 'USD/JPY',
        'display': f'¥{jpy:.2f}', 'score': round(score_usdjpy(jpy), 1),
        'reason': '>155 carry trade 风险 · 2024-08 复刻'
    })

    # 7) US 10Y yield (^TNX returns yield in % directly nowadays)
    raw_tnx = tnx_d[-1][1]
    y = raw_tnx / 10 if raw_tnx > 20 else raw_tnx  # 自适应：旧版 Yahoo 给 yield×10
    indicators.append({
        'key': 'us_10y', 'name': 'US 10Y 国债利率',
        'display': f'{y:.2f}%', 'score': round(score_us10y(y), 1),
        'reason': '>4.5% 估值杀手'
    })

    # 8) YTD return
    cur_year = int(time.strftime('%Y'))
    year_start = None
    for t, v in n_daily:
        if time.localtime(t).tm_year == cur_year:
            year_start = v
            break
    if year_start:
        ytd = (n_close - year_start) / year_start * 100
        indicators.append({
            'key': 'ytd', 'name': f'日経 {cur_year}年 YTD 涨幅',
            'display': f'{"+" if ytd>=0 else ""}{ytd:.1f}%',
            'score': round(score_ytd(ytd), 1),
            'reason': '1989 年 +29% 见顶'
        })

    auto_score = sum(i['score'] for i in indicators) / len(indicators)
    stage_num, stage_label, stage_color = get_stage(auto_score)

    out = {
        'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'nikkei_close': n_close,
        'nikkei_date': n_date,
        'auto_score': round(auto_score, 1),
        'stage_num': stage_num,
        'stage_label': stage_label,
        'stage_color': stage_color,
        'indicators': indicators,
        'manual_checklist': [
            {'key': 'taxi',      'label': '出租车/美容師 開口推荐股票',         'weight': 12},
            {'key': 'family',    'label': '同事・亲戚开始问股市',                'weight': 10},
            {'key': 'magazines', 'label': '日経 4万・5万円大特集 媒体连发',      'weight': 10},
            {'key': 'nisa',      'label': '新NISA 月间流入连续创新高',           'weight': 8},
            {'key': 'narrative', 'label': '「今回は違う」「日本復活」论调流行',  'weight': 10},
            {'key': 'ipo',       'label': 'IPO 概念股暴炒・首日翻倍频繁',         'weight': 10},
            {'key': 'margin',    'label': '信用買い残 屡创新高',                 'weight': 10},
            {'key': 'boj',       'label': 'BOJ 加息 / 缩表加速',                'weight': 10},
            {'key': 'earnings',  'label': '出口企业业绩开始下修',                'weight': 10},
            {'key': 'whale',     'label': '大佬明显减仓（巴菲特・孙正义等）',    'weight': 10},
        ],
    }

    js = (
        f'/* Auto-generated by bubble.py at {out["generated_at"]} */\n'
        f'window.BUBBLE_DATA = {json.dumps(out, ensure_ascii=False, indent=2)};\n'
    )
    OUT_JS.write_text(js, encoding='utf-8')

    print(f'[bubble] Nikkei {n_close:,.0f} ({n_date}) → auto score {auto_score:.1f} = {stage_label}', flush=True)
    for ind in indicators:
        print(f'  - {ind["name"]:30s} {ind["display"]:20s} score {ind["score"]}', flush=True)
    print(f'[bubble] Done -> {OUT_JS.name}', flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
