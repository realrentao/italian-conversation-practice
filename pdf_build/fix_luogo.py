# -*- coding: utf-8 -*-
"""
Normalise every unit's "Luogo e Personaggi" block to the canonical layout:

    地点：<italiano>（<中文>）
    人物：<italiano>（<中文>）、<italiano>（<中文>）

Source data was inconsistent: some units kept a '（地点）：' prefix, some had the
whole Luogo+Personaggi text crammed into `place`, some had Chinese first with the
Italian in parentheses, some carried stray newlines / '•' bullets.
"""
import json, os

BASE = r"D:\意大利语材料\实用意大利语会话"
DATA = os.path.join(BASE, "pdf_build", "units_data.json")

# canonical values, hand-normalised from the PDF source
LUOGO = {
    # ---- CAPITOLO 1 · ALL'ARRIVO IN ITALIA ----
    "c1u1": (
        "in via Santa Chiara（圣嘉勒路上）",
        "Aldo Sparice（奥尔多·斯帕里奇）、una signora in cerca di un'abitazione（一位有意租房的女士）",
    ),
    "c1u2": (
        "In un'edicola, in un negozio TIM, casa di Aldo Sparice（报刊亭、TIM 移动通信公司营业厅、奥尔多·斯帕里奇家）",
        "Aldo Sparice（奥尔多·斯帕里奇）、edicolante（报刊亭老板）、impiegato della TIM（营业厅工作人员）",
    ),
    "c1u3": (
        "Casa di Aldo Sparice, all'ingresso del Banco di Napoli, in un cambio（奥尔多·斯帕里奇家、那不勒斯银行入口、货币兑换处）",
        "Aldo Sparice（奥尔多·斯帕里奇）",
    ),
    "c1u4": (
        "Casa di Aldo Sparice（奥尔多·斯帕里奇家）",
        "Aldo Sparice（奥尔多·斯帕里奇）",
    ),
    # ---- CAPITOLO 2 · MANGIARE IN ITALIA ----
    "c2u1": ("", ""),  # PDF 扫描未包含该单元场景人物
    "c2u2": (
        'Pasticceria "Pastiera Napoletana"（“那不勒斯派”甜品店）',
        "Aldo Sparice（奥尔多·斯帕里奇）、la proprietaria della pasticceria（甜品店女店主）",
    ),
    "c2u3": (
        'Gelateria "Scimmia"（“猴子”冰激凌店）',
        "Aldo Sparice（奥尔多·斯帕里奇）",
    ),
    "c2u4": (
        'Pizzeria "900"（披萨店“900”）',
        "Aldo Sparice（奥尔多·斯帕里奇）、il cameriere（披萨店服务员）、il pizzaiolo（制作披萨的厨师）",
    ),
    "c2u5": (
        "Cucina di Aldo Sparice（奥尔多·斯帕里奇家的厨房）",
        "Aldo Sparice（奥尔多·斯帕里奇）",
    ),
    # ---- CAPITOLO 3 · MUOVERSI IN ITALIA ----
    "c3u1": ("", ""),  # PDF 无该单元场景人物
    "c3u2": (
        "Casa di Aldo Sparice（奥尔多·斯帕里奇家）",
        "Aldo Sparice（奥尔多·斯帕里奇）",
    ),
    "c3u3": (
        "Stazione di Napoli Centrale（那不勒斯中央火车站）",
        "Aldo Sparice（奥尔多·斯帕里奇）",
    ),
    "c3u4": (
        "Aeroporto Internazionale di Napoli（那不勒斯国际机场）",
        "Aldo Sparice（奥尔多·斯帕里奇）、impiegati dell'aeroporto（机场工作人员）",
    ),
    "c3u5": (
        "Posteggio taxi e il parcheggio autonoleggio（出租车停靠点与租车停车场）",
        "Aldo Sparice（奥尔多·斯帕里奇）",
    ),
    # ---- CAPITOLO 4 · DIVERTIRSI IN ITALIA ----
    "c4u1": (
        "Agenzia turistica（旅行社）",
        "Elisa（impiegata，工作人员）、Aldo（turista，游客）",
    ),
    "c4u2": (
        'Albergo "Palazzo Decumani"（宾馆「Palazzo Decumani」）',
        "Aldo Sparice（奥尔多·斯帕里奇）、la receptionist（酒店前台工作人员）",
    ),
    "c4u3": (
        "Museo del Chiostro di Santa Chiara（圣嘉勒修道院博物馆）",
        "Aldo Sparice（奥尔多·斯帕里奇）、impiegato della biglietteria（博物馆售票处工作人员）",
    ),
    "c4u4": (
        "All'interno di un negozio con i prodotti tipici（特产店内）",
        "Aldo Sparice（奥尔多·斯帕里奇）、commesso del negozio（特产店售货员）",
    ),
    # ---- CAPITOLO 5 · VIVERE IN ITALIA ----
    "c5u1": ("", ""),  # PDF 无该单元场景人物
    "c5u2": (
        "All'ingresso della farmacia（药店门口）",
        "Aldo Sparice（奥尔多·斯帕里奇）",
    ),
    "c5u3": (
        "Davanti ad una tabaccheria（一家烟草店门前）",
        "Aldo Sparice（奥尔多·斯帕里奇）",
    ),
    "c5u4": (
        "Casa di Aldo Sparice, ufficio postale di Napoli（奥尔多·斯帕里奇家、那不勒斯邮局）",
        "Aldo Sparice（奥尔多·斯帕里奇）",
    ),
}


def main():
    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)

    hit = set()
    for c in data["chapters"]:
        for u in c["units"]:
            uid = u["id"]
            if uid not in LUOGO:
                print("[WARN] no canonical entry for", uid)
                continue
            place, people = LUOGO[uid]
            hit.add(uid)
            # collapse stray newlines left over from PDF extraction
            place = " ".join(place.split())
            people = " ".join(people.split())
            u["luogo"] = {"place": place, "people": people}

    missing = set(LUOGO) - hit
    if missing:
        print("[WARN] canonical entries not used:", missing)

    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    print(f"[OK] updated luogo for {len(hit)} units")
    for c in data["chapters"]:
        for u in c["units"]:
            lg = u["luogo"]
            flag = "" if (lg["place"] or lg["people"]) else "  (板块将隐藏)"
            print(f"  {u['id']}: 地点={lg['place'][:48]!r} 人物={lg['people'][:40]!r}{flag}")


if __name__ == "__main__":
    main()
