# -*- coding: utf-8 -*-
"""
Replace Unità 1 (c1u1) video-text segments 1-4 with the authoritative text
supplied by the user, and complete its lexical notes (the parsed PDF only
captured the first note group; the second group was missing entirely, and
'da parte più bassa' was a mis-parse of 'la parte più bassa').
"""
import json, os

BASE = r"D:\意大利语材料\实用意大利语会话"
DATA = os.path.join(BASE, "pdf_build", "units_data.json")

SEGMENTS = [
    # ---------- Testo 1 ----------
    {
        "it": [
            "Dove si trovano gli annunci di locazione? 哪儿能找到房屋出租信息？",
            "Sei appena giunto qui a Napoli, o in un'altra città italiana?",
            "Sicuramente hai bisogno di una stanza, di un appartamento, cioè di una sistemazione.",
            "Spesso trovi dei cartelli tipo questo: Affittasi, o anche Fittasi.",
            "E sotto, qui, nella parte più bassa, spesso ci sono dei piccoli pezzetti di carta, con un numero di telefono, che puoi chiamare, per chiedere tutte le informazioni che ti occorrono.",
            "È abbastanza comune trovare dei fogli come questo.",
            "Spesso li puoi trovare all'entrata dell'università, nella bacheca, se sei uno studente universitario.",
            "Altrimenti è meglio che li cerchi per strada, nelle zone dove ti interessa affittare una stanza o un appartamento.",
        ],
        "zh": [
            "你是刚到那不勒斯，或者是意大利的某个其他城市吗？",
            "你一定需要一个房间，或者一套公寓，总之一个落脚的地方。",
            "通常你会找到这一类的广告：“租房”或者“出租”。",
            "下面，在这个位置，这张纸的最下面，常常有一些小纸条，上面写着电话号码，你可以打过去问一下你需要的所有信息。",
            "这类纸质出租信息随处可见。",
            "如果你是大学生，通常可以在学校门口的宣传栏里找到这类信息。",
            "不然的话，也可以在你想租房间或公寓的区域沿路找一找。",
        ],
    },
    # ---------- Testo 2 ----------
    {
        "it": [
            "Posso fare un sopralluogo?",
            "Buongiorno signore!",
            "Buongiorno!",
            "Ho visto l'annuncio e sono interessata ad affittare questa casa. Posso vederla?",
            "Oh, prego, s'accomodi.",
            "Eh... la troverà un po' in disordine, perché l'inquilina precedente sta per partire, ma ha ancora alcune cose qui. Prego.",
            "Grazie!",
            "Questo è un angolo cottura, con un frigorifero, due fuochi, quindi un fornello a due fuochi, un lavandino, un mobile.",
            "Qui c'è una piccola dispensa, dove si possono porre piatti, stoviglie, anche cibo.",
            "Poi, questo è un piccolo disimpegno, quindi anche la zona pranzo, molto luminoso.",
            "L'appartamento, come ha visto, si trova in una zona centralissima. È all'incrocio di due strade principali, proprio al centro, il centro antico della città.",
            "Eh... qui c'è il bagno, con i servizi igienici. Non c'è una vasca da bagno, ma c'è una doccia, una cabina doccia.",
            "Non c'è finestra, ma c'è un areatore, su in alto.",
        ],
        "zh": [
            "您好，先生！",
            "您好！",
            "我看到了出租告示，有兴趣租这个房子，我可以看看房吗？",
            "噢，好的，请进。",
            "呃……您会发现房间有点乱，因为上一个房客正要搬走，还有一些东西暂存在这里。请进。",
            "谢谢！",
            "这是做饭的地方：有一台冰箱、两个炉灶（也就是两个灶眼的燃气灶）、一个洗碗池、一个橱柜。",
            "这里有一个小的食品柜，里面可以放盘子、餐具和食物。",
            "然后，这里的小空地，可以当作餐厅，光线很好。",
            "您也看到了，这套公寓位于城市最中心的区域，是两条主要干道的交叉口，绝对的中心，老城区中心。",
            "这里……这里是洗手间，有洗浴设施。虽然没有浴缸，但是有淋浴，一个淋浴间。",
            "没有窗户，但是有换气扇，在上面。",
        ],
    },
    # ---------- Testo 3 ----------
    {
        "it": [
            "Poi ci sono due camere da letto, o due stanze in ogni caso, dipende dall'uso che ne vuole fare.",
            "Ha intenzione di affittarla da sola o con un'altra persona? Anche perché il prezzo varia.",
            "Se da sola, quindi con uso singolo, ha un prezzo un po' più alto, altrimenti può condividere (può dividere) questo appartamento con una persona e credo che possa risparmiare qualcosa.",
            "Qui c'è una scrivania, una doppia scrivania.",
            "Eventualmente possiamo spostare la poltrona e questo mobile, e aggiungere un letto singolo, oppure se preferisce usarla da sola...",
            "Questa è una camera da letto, con due letti separati, aria condizionata, riscaldamento (lo chiamiamo termosifone), televisione, una finestra che dà su una zona molto bella (è una piccola finestra).",
            "C'è anche un lucernario, perché siamo sul piano più alto, quindi è sotto tetto.",
        ],
        "zh": [
            "还有两间卧室，或者说是两个房间，看您想怎么利用它们。",
            "您打算自己租还是跟另一个人合租？因为这两种方式的价格会有所不同。",
            "如果自己租，也就是单用，价格会稍高，不然您可以跟另一个人合租这间房，我觉得这样能省些钱。",
            "这里有一张写字台，一张双人写字台。",
            "如果有需要，我们可以把这张扶手椅和这套家具移走，增加一张单人床，当然，您也可以单独住这套房子……",
            "这是卧室，有两张独立的单人床、空调、取暖器（termosifone）、电视、一扇窗户（一扇小窗户），窗外风景不错。",
            "还有一扇天窗，因为我们在顶层，上面就是楼顶。",
        ],
    },
    # ---------- Testo 4 ----------
    {
        "it": [
            "Una curiosità, quanto costa l'affitto al mese?",
            "Se per uso individuale cioè l'affitta solo per Lei, 400 euro, in più ci sono da pagare le spese di gestione, che sono praticamente l'acqua, l'energia elettrica (spesso diciamo « la luce »), e il gas, per il fornello, quindi per la cucina, per l'ambiente cucina, eh... ancora c'è da pagare una quota condominiale, ma è una piccola quota.",
            "Ancora, la descrizione... c'è un divanetto, una poltrona, un armadio a quattro ante, un comodino, e un tavolino che può usare come comodino anche.",
            "Eh... fra quanto tempo sarà libera?",
            "Diciamo che tra circa due ore sarà libera. Quindi se vuole, mi può lasciare un recapito e la richiamo oppure può ritornare forse un pomeriggio. Nel pomeriggio sono qui.",
            "OK, grazie, ci penso un attimo e poi le faccio sapere.",
            "Va bene.",
            "Grazie, arrivederci!",
            "Buona giornata.",
            "Anche a Lei.",
        ],
        "zh": [
            "我想问一下，每个月的房租多少钱？",
            "如果一个人住，也就是您单独租的话，是400欧元，再加上其他日常费用，主要包括水费、电费（我们通常称为“电灯费”）、炉灶（也就是厨房消耗的燃气费），还有一定的物业费，但是金额很小。",
            "还有，再介绍一下这里，这里有一张小沙发、一把扶手椅、一个四门衣橱、一个床头柜，还有一个茶几，也可以摆在床头。",
            "呃……这房子还要多长时间能腾空出来？",
            "再有2个小时就腾空了。所以如果您愿意租的话，可以给我留一个联系方式，或者您下午再来也行，下午我在这边。",
            "好的。",
            "祝您一天愉快！",
            "您也是！",
        ],
    },
]

NOTES = [
    {
        "term": "avere bisogno di...",
        "explain": "需要……。该词组既可接名词，也可接动词不定式现在时。",
        "examples": [
            "Hai bisogno di andare in bagno? 你需要去卫生间吗？",
            "Abbiamo bisogno di tre ore per finire la traduzione del testo. 我们需要3个小时来完成这篇文章的翻译。",
        ],
    },
    {
        "term": "Affittasi (Fittasi)",
        "explain": '有……招租。这是一种较为通俗的口语化说法，并不完全符合语法规则。此处的 si 具有被动含义，更为规范的说法是 "Si affitta..."。',
        "examples": [],
    },
    {
        "term": "la parte più bassa",
        "explain": "最下面的位置。意大利语中的形容词（及部分副词）分为原级、比较级和最高级形式。绝大多数形容词（副词）的比较级由più或meno加上形容词（副词）的原级构成，表达“更加……”或“没那么……”的含义。在比较级的前面加上形容词（副词）的词尾变为“-issimo”，可构成绝对最高级，含义为“极其……”。少数不规则形容词（副词）有独特的比较级和最高级变化形式。",
        "examples": [
            "Carlo è lo studente più sensibile della classe. 卡罗是班里最敏感的学生。",
            "Roma è una delle città più belle dell'Italia. 罗马是意大利最美丽的城市之一。",
        ],
    },
    {
        "term": "c'è... / ci sono...",
        "explain": "有……。ci sono是esserci变位后的直陈式现在时形式。动词essere的主语是后面存在的物品或人。若作为主语的物品或人为单数时，应使用单数形式c'è；为复数，应使用ci sono。",
        "examples": [
            "Ci sono due libri sul banco. 桌子上有两本书。",
            "C'è qualcuno? 有人吗？",
        ],
    },
    {
        "term": "occorrere",
        "explain": "对……有必要。",
        "examples": [
            "Mi occorrono almeno tre settimane per terminare il lavoro. 我需要至少三个星期完成这项工作。",
            "Ci occorre appoggio reciproco nei momenti difficili. 在困难的时候我们需要互相支持。",
        ],
    },
    {
        "term": "li",
        "explain": "它们。文中的li是直接宾语代词，代替上文中的“dei fogli come questo”。直接宾语代词有 mi, ti, ci, vi, lo, la, li, le, ne，位于变位动词前面，或紧跟着动词不定式后面。",
        "examples": [
            "Mario conosce una nuova professoressa italiana, ma non la conosco. 马里奥认识一个新的意大利女教师，但我不认识她。",
            "La mia mamma mi ha comprato un libro ma non voglio leggerlo. 我的妈妈给我买了一本书，但我不想读。",
        ],
    },
    {
        "term": "altrimenti",
        "explain": "不然，否则。",
        "examples": [
            "Dovrai affrettarti, altrimenti perderai il treno. 你要快点，不然就要赶不上火车了。",
            "Devi imparare a collaborare con gli altri, altrimenti nessuno vorrà lavorare con te. 你应该学习与别人合作，否则没有人愿意跟你一起工作。",
        ],
    },
    {
        "term": "è meglio...",
        "explain": "最好……。可与动词不定式现在时连用，也可用che引导出从句，从句中应使用虚拟式动词。",
        "examples": [
            "Di sera è meglio non tornare a casa da solo. 晚上最好不要一个人回家。",
            "È meglio che tu faccia tutto il possibile per superare l'esame. 你最好尽一切可能通过考试。",
        ],
    },
    {
        "term": "in disordine",
        "explain": "混乱的，乱七八糟的。",
        "examples": [
            "Il nemico fuggiva in disordine. 敌人仓皇逃跑。",
            "Ho visto la sua camera in disordine. 我发现你的她的房间",
        ],
    },
    {
        "term": "stare per...",
        "explain": "正要做某事。per后面应加动词不定式现在时。",
        "examples": [
            "Stanno per andare alla mensa. 他们正要去食堂。",
            "Visto che sta per piovere, stasera vuoi restare a casa mia? 既然马上就要下雨了，今晚你就住在我家好吗？",
        ],
    },
    {
        "term": "si possono porre piatti",
        "explain": "可以放盘子。这里的si是被动意义的 si，用 si 加上及物动词的第三人称单数或复数（取决于作为主语的名词的单复数），可构成被动语态。",
        "examples": [
            "La mostra si è inaugurata ieri. 展览会已于昨天开幕。",
            "I biglietti dell'Alibus si vendono in tabaccheria. 机场大巴票在烟草店出售。",
        ],
    },
    {
        "term": "si trova",
        "explain": "位于，处在",
        "examples": [
            "Dove si trova la tua casa? 你的家在哪里？",
            "Si trovava proprio lì quando ci fu lo scoppio.",
        ],
    },
    {
        "term": "in ogni caso",
        "explain": "无论是在何种情况下，无论如何。",
        "examples": [
            "In ogni caso avresti potuto telefonarmi! 无论如何，你至少能给我打个电话吧！",
            "In ogni caso devo partire domani. 无论如何，我明天要出发。",
        ],
    },
    {
        "term": "dipendere da...",
        "explain": "取决于……。",
        "examples": [
            "Talvolta lo sviluppo degli avvenimenti dipende da circostanze casuali. 事态发展有时受偶然情况影响。",
            "Il futuro della nostra amicizia dipende da te. 我们友谊的未来取决于你。",
        ],
    },
    {
        "term": "avere intenzione di...",
        "explain": "有意图做……，打算做……。",
        "examples": [
            "Non ho nessuna intenzione di partire domani. 我根本没打算明天走。",
            "Che intenzioni hai con quel coltellaccio in mano? 你拿着那把破刀子，究竟想干什么？",
        ],
    },
    {
        "term": "condividere... con...",
        "explain": "与某人分享。",
        "examples": [
            "Ho deciso di condividere questo appartamento con una mia amica. 我决定了跟我朋友同住这套公寓。",
            "Vorrei condividere gioie e dolori con te. 我想与你同甘共苦。",
        ],
    },
    {
        "term": "eventualmente",
        "explain": "如果有情况。",
        "examples": [
            "Eventualmente telefonerò al medico. 如果有情况，我就给医生打电话。",
            "Non credo di poter venire, eventualmente te lo farò sapere qualche giorno prima. 我估计来不了，如果有新情况，我会提前几天告诉你。",
        ],
    },
    {
        "term": "oppure",
        "explain": "或者。",
        "examples": [
            "Hai deciso di partire oppure vuoi rimanere a Milano ancora per qualche giorno? 你是决定走，还是在米兰再呆几天",
            "Vino oppure birra, per me è uguale. 葡萄酒或者啤酒，对我来说都一样。",
        ],
    },
    {
        "term": "al mese",
        "explain": "每月。意大利语中经常用介词a搭配时间名词，表示动作发生的频率。类似的表达有：al giorno（每天），alla settimana（每周），all'anno（每年）。",
        "examples": [
            "La frequenza cardiaca è il numero di battiti del cuore al minuto. 心律是指心脏每分钟跳动的次数。",
            "Facciamo spese una volta alla settimana. 我们每周采购一次。",
        ],
    },
    {
        "term": "in più",
        "explain": "另外，外加。",
        "examples": [
            "Non vengo al cinema perché quel film non mi va e in più sono stanco. 我不想去电影院，因为那部片子我不喜欢，而且我累了。",
            "Devi chiedere la restituzione del debito di 500 euro, in più il pagamento degli interessi di 30 euro. 你应该要求归还500欧元的欠款，外加30欧元的利息。",
        ],
    },
    {
        "term": "da pagare",
        "explain": "有……的费用要付。名词与介词 da 连用，后面加上及物动词，意为“某物需要被……”。",
        "examples": [
            "C'è una tassa di 45 euro da pagare. 有45欧元的税要付。",
            "Ho molto lavoro da fare. 我有许多工作要做。",
        ],
    },
    {
        "term": "un attimo",
        "explain": "一刻，一瞬间。",
        "examples": [
            "Sarò da te in un attimo. 我马上到你那里。",
            "Aspettami un attimo, per favore. 请稍等一会儿。",
        ],
    },
    {
        "term": "fare sapere",
        "explain": "让……知道。fare... fare... 表示让某人或物做某事。",
        "examples": [
            "Mia madre non mi ha fatto entrare in casa ieri sera. 我妈妈昨天晚上不让我进门。",
            "I miei amici mi hanno fatto partecipare ad un concorso. 我的朋友们让我参加一场竞赛。",
        ],
    },
    {
        "term": "andare bene",
        "explain": "好的，可以的。在该结构中，主语是物品或事情，以名词或者动词不定式现在时的形式置于 andare bene之后。如果需要强调对谁是好的，可在andare前加上间接宾语代词的非重读形式。有时，bene一词也可以省略。",
        "examples": [
            "Ti va (bene) andare a scuola a piedi oggi? 你今天走路去上学可以吗？",
            "A quest'ora non mi va il caffè, preferisco un latte caldo. 此刻我不宜喝咖啡，还是来一杯热牛奶吧。",
        ],
    },
    {
        "term": "buona giornata",
        "explain": "祝你一天愉快！作分别时的祝福语，祝对方在当天接下来的活动和事务中愉快顺利。类似的有：buongiorno（祝你一天愉快），buon proseguimento di giornata（祝你今天其他事情顺利）。若是双方道别时，天色已晚，则可用 buona serata（祝你晚间活动愉快）。",
        "examples": [],
    },
]


def main():
    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)

    target = None
    for c in data["chapters"]:
        for u in c["units"]:
            if u["id"] == "c1u1":
                target = u
    if target is None:
        raise SystemExit("c1u1 not found")

    before_segs = len(target.get("dialogue", []))
    before_notes = len(target.get("notes", []))

    target["dialogue"] = [
        {"it": "\n".join(s["it"]), "zh": "\n".join(s["zh"])} for s in SEGMENTS
    ]
    target["notes"] = NOTES

    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    print(f"[OK] c1u1 dialogue {before_segs} -> {len(target['dialogue'])}")
    print(f"[OK] c1u1 notes    {before_notes} -> {len(target['notes'])}")
    for i, s in enumerate(target["dialogue"], 1):
        print(f"  Testo {i}: it={len(s['it'])}字 zh={len(s['zh'])}字")


if __name__ == "__main__":
    main()
