# -*- coding: utf-8 -*-
"""v2予算JSON → Webサイト用スリムデータ生成
出力: site/data/r8.json
  {"total": 千円, "year":"R8",
   "tree": [{n,v,c:[...]}],          # 款→項→目→事業→節→細目（ツリーマップ用）
   "flat": [{p:[款,項,目], n:事業名, t:担当課, v:合計, s:"節・細目テキスト"}]}  # 検索/AI用
実行: PYTHONIOENCODING=utf-8 python site/build_data.py
"""
import json
import os
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'json', '予算構造_R8.json')
OUT = os.path.join(ROOT, 'site', 'data', 'r8.json')

data = json.load(open(SRC, encoding='utf-8'))

kans = OrderedDict()
flat = []
for me in data:
    kan = kans.setdefault(me['款名'], OrderedDict())
    ko = kan.setdefault(me['項名'], [])
    me_node = {'n': me['目名'], 'v': me['本年度'] or 0, 'c': []}
    for j in me['事業']:
        jn = {'n': j['名称'], 'v': j['合計'] or 0}
        if j.get('担当課'):
            jn['t'] = j['担当課']
        cs = []
        search_text = []
        for s in j['節']:
            sn = {'n': s['名称'], 'v': s['合計'] or 0}
            search_text.append(s['名称'])
            leaf = []
            for sm in s['細目']:
                item = {'n': sm['名称'], 'v': sm['金額'] if sm['金額'] is not None else 0}
                if sm['金額'] is None:
                    item['nd'] = 1   # 原文非表示（工事内訳等）
                leaf.append(item)
                search_text.append(sm['名称'])
            if leaf:
                sn['c'] = leaf
            cs.append(sn)
        if cs:
            jn['c'] = cs
        me_node['c'].append(jn)
        # 検索用フラットレコード（事業単位）
        if (j['合計'] or 0) > 0:
            flat.append({
                'p': [me['款名'], me['項名'], me['目名']],
                'n': j['名称'],
                't': j.get('担当課', ''),
                'v': j['合計'] or 0,
                's': ' '.join(search_text),
            })
    if not me_node['c']:
        del me_node['c']
    ko.append(me_node)

tree = []
for kan_name, kos in kans.items():
    kan_node = {'n': kan_name, 'c': []}
    kan_total = 0
    for ko_name, mes in kos.items():
        ko_total = sum(m['v'] for m in mes)
        kan_total += ko_total
        # 項が1つで款と同名なら階層を省略（議会費/議会費/議会費 の冗長を回避）
        if len(kos) == 1 and ko_name == kan_name and len(mes) == 1 and mes[0]['n'] == kan_name:
            kan_node = {'n': kan_name, 'v': ko_total, 'c': mes[0].get('c', [])}
            break
        kan_node['c'].append({'n': ko_name, 'v': ko_total, 'c': mes})
    kan_node.setdefault('v', kan_total)
    tree.append(kan_node)

total = sum(k['v'] for k in tree)

# ── 4か年推移（款別・M6用）──
KAN_ORDER = ['議会費', '総務費', '民生費', '衛生費', '労働費', '農林水産業費', '商工費',
             '土木費', '消防費', '教育費', '公債費', '諸支出金', '予備費']
YEARS = ['R5', 'R6', 'R7', 'R8']
year_kan = {}   # year -> {kan: 千円}
for y in YEARS:
    d = json.load(open(os.path.join(ROOT, 'json', f'予算構造_{y}.json'), encoding='utf-8'))
    agg = {}
    for me in d:
        agg[me.get('款名', '')] = agg.get(me.get('款名', ''), 0) + (me.get('本年度') or 0)
    year_kan[y] = agg
trend = {
    'years': YEARS,
    'totals': [sum(year_kan[y].values()) for y in YEARS],
    'kans': [{'n': k, 'v': [year_kan[y].get(k, 0) for y in YEARS]} for k in KAN_ORDER],
}

# ── 歳入（税金はどこから来る）──
JISHU = {'市税', '分担金及び負担金', '使用料及び手数料', '財産収入', '寄附金',
         '繰入金', '繰越金', '諸収入'}  # 自主財源（残りは依存財源）
rev = json.load(open(os.path.join(ROOT, 'json', '歳入構造_R8.json'), encoding='utf-8'))
rev_kan = OrderedDict()
for m in rev:
    rev_kan[m['款名']] = rev_kan.get(m['款名'], 0) + (m['本年度'] or 0)
rev_list = sorted(
    [{'n': k, 'v': v, 'j': (k in JISHU)} for k, v in rev_kan.items()],
    key=lambda x: -x['v'])
revenue = {
    'total': sum(rev_kan.values()),
    'kans': rev_list,
    'jishu': sum(x['v'] for x in rev_list if x['j']),
    'izon': sum(x['v'] for x in rev_list if not x['j']),
}

out = {'total': total, 'year': 'R8', 'tree': tree, 'flat': flat, 'trend': trend,
       'revenue': revenue}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
print(f"total={total:,}千円  款={len(tree)}  事業(flat)={len(flat)}  size={os.path.getsize(OUT):,}bytes")
