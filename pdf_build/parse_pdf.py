# -*- coding: utf-8 -*-
import fitz, re, json, os

PDF = r"C:\Users\迪丽希斯\OneDrive\Desktop\未命名文档 (6).pdf"
OUT = r"D:\意大利语材料\实用意大利语会话\pdf_build\units_data.json"

ROMAN = {'I':1,'II':2,'III':3,'IV':4,'V':5,'VI':6,'VII':7,'VIII':8,'IX':9,'X':10}

def is_cjk(s):
    return any('\u4e00' <= ch <= '\u9fff' for ch in s)

def is_latin(s):
    return bool(re.search(r'[A-Za-z]', s)) and not is_cjk(s)

def is_bullet(s):
    return s.strip() in ('•','◦','·','-','—','*','·') or re.fullmatch(r'[•◦·\-\—*]+', s.strip()) is not None

def strip_footer(text):
    # remove page footers like "  1 / 143" and "未命名文档"
    lines = text.split('\n')
    out = []
    for ln in lines:
        s = ln.strip()
        if re.fullmatch(r'\d+\s*/\s*143', s):
            continue
        if s == '未命名文档':
            continue
        out.append(ln)
    return '\n'.join(out)

doc = fitz.open(PDF)
pages = [strip_footer(doc[i].get_text()) for i in range(doc.page_count)]
full = "\n".join(pages)

# ---- find chapter & unit boundaries by scanning lines ----
unit_re = re.compile(r'^UNIT[ÀA]\s+(\d+)\s+(.*)$')
chap_re = re.compile(r'^CAPITOLO\s+([IVX]+)\s+(.*)$')

chapters = []          # list of dict
cur_chap = None
cur_unit = None

def finalize_unit(u):
    if u is not None:
        u['raw'] = u['raw'].strip()
        cur_chap['units'].append(u)

for ln in full.split('\n'):
    s = ln.strip()
    mchap = chap_re.match(s)
    if mchap:
        finalize_unit(cur_unit); cur_unit=None
        roman = mchap.group(1); rest = mchap.group(2).strip()
        if '｜' in rest:
            it_t, cn = rest.split('｜',1)
        else:
            # chinese is trailing CJK run
            mm = re.search(r'([\u4e00-\u9fff].*)$', rest)
            if mm:
                cn = mm.group(1); it_t = rest[:mm.start()].strip()
            else:
                cn = ''; it_t = rest
        cur_chap = {'roman': roman, 'title': it_t.strip(), 'subtitle': cn.strip(), 'units': []}
        chapters.append(cur_chap)
        continue
    mun = unit_re.match(s)
    if mun:
        finalize_unit(cur_unit)
        num = int(mun.group(1)); rest = mun.group(2).strip()
        if '｜' in rest:
            it_t, cn = rest.split('｜',1)
        else:
            mm = re.search(r'([\u4e00-\u9fff].*)$', rest)
            if mm:
                cn = mm.group(1); it_t = rest[:mm.start()].strip()
            else:
                cn=''; it_t=rest
        cur_unit = {'num': num, 'title': it_t.strip(), 'subtitle': cn.strip(), 'raw': ''}
        continue
    if cur_unit is not None:
        cur_unit['raw'] += ln + '\n'

finalize_unit(cur_unit)

# ---- section parsing ----
SECTION_PATTERNS = {
    'luogo':       r'Luogo e Personaggi|场景及人物',
    'vocab':       r'Parole chiave|关键词',
    'frasi':       r"Frasi d'uso comune|常用句",
    'testo':       r'Testo\s|视频文本',
    'traduzione':  r'Traduzione|文本翻译',
    'note':        r'Note lessicali|词法解析',
}

def find_markers(raw):
    markers = []  # (lineno, name)
    for i, ln in enumerate(raw.split('\n')):
        s = ln.strip()
        for name, pat in SECTION_PATTERNS.items():
            if re.match(pat, s):
                markers.append((i, name))
                break
    markers.sort()
    return markers

def block_between(raw_lines, start_idx, markers):
    # content from line start_idx+1 until next marker line
    end = len(raw_lines)
    for (mi, _) in markers:
        if mi > start_idx:
            end = mi; break
    return raw_lines[start_idx+1:end]

def parse_luogo(block_lines):
    txt = '\n'.join(l.strip() for l in block_lines if l.strip())
    txt = txt.replace('**', '')
    parts = re.split(r'(?:Personaggi|Personaggio)\s*[（(]?人物[)）]?\s*[:：]?', txt)
    if len(parts) >= 2:
        place = re.sub(r'^Luogo\s*[：:]?\s*', '', parts[0]).strip()
        people = parts[1].strip()
        return {'place': place, 'people': people}
    mp = re.search(r'Luogo\s*[（(]?地点[)）]?\s*[:：]?\s*(.*)', txt, re.S)
    if mp:
        return {'place': mp.group(1).strip(), 'people': ''}
    return {'place': txt.strip(), 'people': ''}

def is_placeholder(s):
    return re.fullmatch(r'[\s〔【(（]*[?？][\s〕】)）]*', s) is not None

def parse_vocab(block_lines):
    seq=[]
    for l in block_lines:
        s=l.strip()
        if not s: continue
        if s in ('意大利语','中文'): continue
        if is_bullet(s): continue
        seq.append(s)
    pairs=[]; pending=None
    for s in seq:
        if is_placeholder(s):
            if pending is not None:
                pending['zh']=s; pairs.append(pending); pending=None
            continue
        if is_cjk(s):
            if pending is not None:
                pending['zh']=s; pairs.append(pending); pending=None
            continue
        # latin -> new it
        if pending is not None:
            pairs.append(pending)
        pending={'it':s,'zh':''}
    if pending is not None:
        pairs.append(pending)
    return pairs

def parse_frasi(block_lines):
    items=[]; it_parts=[]; zh=''
    def flush():
        nonlocal it_parts, zh
        if it_parts and zh:
            items.append({'it':' '.join(it_parts), 'zh':zh})
        it_parts=[]; zh=''
    for l in block_lines:
        s=l.strip()
        if not s or is_bullet(s):
            flush(); continue
        if is_cjk(s) and is_latin(s):
            # line contains both italian and chinese on same line
            cm = re.search(r'[\u4e00-\u9fff]', s)
            latin_part = s[:cm.start()].strip()
            cjk_part = s[cm.start():].strip()
            if latin_part:
                it_parts.append(latin_part)
            zh = cjk_part; flush(); continue
        if is_cjk(s):
            zh=s; flush(); continue
        else:
            it_parts.append(s)
    flush()
    return items

def split_paragraphs(block_lines):
    paras=[]; cur=[]
    for l in block_lines:
        s=l.strip()
        if not s:
            if cur:
                paras.append(' '.join(cur)); cur=[]
        else:
            cur.append(s)
    if cur:
        paras.append(' '.join(cur))
    return [p for p in paras if p]

def dedupe_consec(lines):
    out=[]
    for x in lines:
        if out and out[-1].strip() == x.strip():
            continue
        out.append(x)
    return out

def parse_testo_traduzione(testo_blocks, tradu_blocks):
    tp = dedupe_consec(split_paragraphs(testo_blocks))
    cp = dedupe_consec(split_paragraphs(tradu_blocks))
    # strip leading Italian key that is duplicated inside the Chinese block
    if tp and cp and tp[0].strip() == cp[0].strip():
        cp = cp[1:]
    pairs=[]
    n=max(len(tp), len(cp))
    for i in range(n):
        it = tp[i] if i < len(tp) else ''
        zh = cp[i] if i < len(cp) else ''
        pairs.append({'it': it, 'zh': zh})
    return pairs, len(tp), len(cp)

def parse_notes(block_lines):
    notes=[]
    cur=None
    for l in block_lines:
        s=l.strip()
        if not s: continue
        if is_bullet(s): continue
        m = re.match(r'\*\*(.+?)\*\*[:：]?(.*)$', s)
        if m:
            if cur: notes.append(cur)
            cur = {'term': m.group(1).strip(), 'explain': m.group(2).strip(), 'examples': []}
        else:
            if cur is None:
                cur = {'term':'', 'explain':'', 'examples':[]}
            # example line, possibly a)/b) italian+chinese on one line
            cur['examples'].append(s)
    if cur: notes.append(cur)
    return notes

# ---- process each unit ----
result_chapters=[]
warn=[]
for ci, chap in enumerate(chapters):
    rc = {'title': chap['title'], 'subtitle': chap['subtitle'], 'units': []}
    for uni in chap['units']:
        raw = uni['raw']
        lines = raw.split('\n')
        markers = find_markers(raw)
        # build index of marker name -> list of start line idx
        idx = {}
        for (li, name) in markers:
            idx.setdefault(name, []).append(li)
        # single sections
        def get_block(name):
            if name not in idx: return []
            li = idx[name][0]
            return block_between(lines, li, markers)
        luogo = parse_luogo(get_block('luogo'))
        vocab = parse_vocab(get_block('vocab'))
        frasi = parse_frasi(get_block('frasi'))
        notes = parse_notes(get_block('note'))
        # testo + traduzione: each Testo segment -> one Italian block paired with its Traduzione block.
        # (Chinese paragraph breaks are unreliable on extraction, so we keep whole-segment blocks.)
        td_pairs = []
        pending_testo = None
        def block_text(lines):
            out=[]
            for l in lines:
                s=l.strip()
                if not s or is_bullet(s):
                    continue
                out.append(s)
            return '\n'.join(out)
        for (li, name) in markers:
            if name == 'testo':
                if pending_testo is not None:
                    td_pairs.append({'it': block_text(pending_testo), 'zh': ''})
                pending_testo = block_between(lines, li, markers)
            elif name == 'traduzione':
                blk = block_between(lines, li, markers)
                it_lines = [l.strip() for l in pending_testo] if pending_testo else []
                it_lines = [x for x in it_lines if x and not is_bullet(x)]
                zh_lines = [l.strip() for l in blk if l.strip()]
                zh_lines = [x for x in zh_lines if not is_bullet(x)]
                # strip leading Italian key duplicated inside the Chinese block
                if it_lines and zh_lines and it_lines[0] == zh_lines[0]:
                    zh_lines = zh_lines[1:]
                td_pairs.append({'it': '\n'.join(it_lines), 'zh': '\n'.join(zh_lines)})
                pending_testo = None
        if pending_testo is not None:
            td_pairs.append({'it': block_text(pending_testo), 'zh': ''})
        td = td_pairs
        ntp = sum(1 for x in td if x['it'])
        ncp = sum(1 for x in td if x['zh'])
        # build unit id
        uid = f"c{ci+1}u{uni['num']}"
        unit = {
            'id': uid,
            'num': f"Unità {uni['num']}",
            'title': uni['title'],
            'subtitle': uni['subtitle'],
            'luogo': luogo,
            'vocab': vocab,
            'sentences': frasi,
            'dialogue': td,
            'notes': notes,
        }
        # validations
        if len(vocab) and any((is_cjk(p['it']) or not p['zh']) for p in vocab):
            warn.append(f"{uid}: vocab parity/issue -> {[(p['it'],p['zh']) for p in vocab if is_cjk(p['it']) or not p['zh']]}")
        if ntp != ncp:
            warn.append(f"{uid}: testo({ntp}) != traduzione({ncp})")
        rc['units'].append(unit)
    result_chapters.append(rc)

data = {'chapters': result_chapters}
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=1)

# report
print("Chapters:", len(result_chapters))
total_units=0; total_vocab=0; total_frasi=0; total_dialogue=0; total_notes=0
for c in result_chapters:
    print(f"  {c['title']} ({c['subtitle']}): {len(c['units'])} units")
    for u in c['units']:
        total_units+=1; total_vocab+=len(u['vocab']); total_frasi+=len(u['sentences'])
        total_dialogue+=len(u['dialogue']); total_notes+=len(u['notes'])
        print(f"    {u['id']} {u['title']} | vocab={len(u['vocab'])} frasi={len(u['sentences'])} dialogo={len(u['dialogue'])} note={len(u['notes'])}")
print(f"TOTAL units={total_units} vocab={total_vocab} frasi={total_frasi} dialogo={total_dialogue} note={total_notes}")
print("WARNINGS:")
for w in warn:
    print("  ", w)
