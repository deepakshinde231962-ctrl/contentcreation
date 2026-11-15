"""
Storyboard for "The Richest Man in Babylon — Niyam 1: Pehle Khud Ko Do".

This file is the single source of truth for the video:
  * narration text (per scene -> one TTS clip per scene)
  * caption lines (burned as subtitles)
  * kinetic text cards (drawn by build_video.py)
  * which still image + camera move each scene uses

Timing is NOT hard-coded: build_video.py measures each narration clip and
derives scene duration, caption timing and the total timeline. That means you
can edit a sentence here and the whole video re-times itself.

Run:  python scripts/build_video.py --help
"""

FPS = 25
WIDTH, HEIGHT = 1920, 1080

# --------------------------------------------------------------------------
# Scene definition
# --------------------------------------------------------------------------
# narration : spoken by TTS (one clip per scene)
# captions  : short subtitle lines, timed automatically inside the scene
# cards     : on-screen typography; start/end are seconds INSIDE the scene
#             (after pad_in). roles -> kicker / big / sub / source / steps
# motion    : camera move on the still image
# --------------------------------------------------------------------------

SCENES = [
    dict(
        id="hook",
        image="assets/img/01_babylon.png",
        motion="zoom_in",
        pad_in=0.9,
        pad_out=0.7,
        narration=(
            "चालीस हज़ार की सैलरी, और महीने के तीसरे हफ़्ते खाता खाली। "
            "EMI, रेंट, यूपीआई — सब पहले, बचत सबसे बाद में। "
            "यही समस्या उन्नीस सौ छब्बीस में एक अमेरिकी लेखक ने हल की थी — बेबीलोन की कहानी से। "
            "आज वो नियम विज्ञान में सबसे ज़्यादा टेस्ट हुआ है। "
            "लेकिन उसमें एक कमी है, जो कोई हिंदी वीडियो नहीं बताता।"
        ),
        captions=[
            "₹40,000 सैलरी — और तीसरे हफ़्ते खाता खाली",
            "EMI, रेंट, UPI — सब पहले। बचत सबसे बाद में।",
            "1926 में एक लेखक ने यही समस्या हल की — बेबीलोन की कहानी से",
            "आज वो नियम विज्ञान में सबसे ज़्यादा टेस्ट हुआ है",
            "पर उसमें एक कमी है, जो कोई नहीं बताता...",
        ],
        cards=[
            dict(start=0.0, end=3.2, kicker="₹40,000 · TEESRA HAFTA",
                 big="खाता", big2="खाली?"),
            dict(start=3.2, end=99, kicker="1926 · BABYLON",
                 big="एक नियम", big2="जो आज भी टेस्ट होता है",
                 sub="और एक कमी, जो कोई नहीं बताता"),
        ],
    ),
    dict(
        id="rule",
        image="assets/img/02_arkad.png",
        motion="zoom_out",
        pad_in=0.5,
        pad_out=0.7,
        narration=("कहानी में अर्काड है — बेबीलोन का सबसे अमीर आदमी। दोस्त बंसीर और कोबी पूछते हैं: मेहनत तो हम भी करते हैं, फिर पैसा क्यों नहीं बचता? अर्काड कहता है — जो कमाओ, उसका एक हिस्सा सबसे पहले खुद को दो; बाद में दुकानदार, मकान मालिक और बैंक को। यानी बचत वो नहीं जो महीने के आख़िर में बचती है। बचत वो है जो शुरू में ही निकाल ली जाती है। कम से कम दसवां हिस्सा। और याद रखिए — ये दान नहीं है, ये पैसा आपके पास ही रहता है।"),
        captions=[
            "Arkad — बेबीलोन का सबसे अमीर आदमी",
            "Bansir और Kobbi पूछते हैं: मेहनत तो हम भी करते हैं",
            "...फिर पैसा क्यों नहीं बचता?",
            "जवाब: जो कमाओ, उसका हिस्सा पहले खुद को दो",
            "बचत वो नहीं जो आख़िर में बचे",
            "बचत वो है जो शुरू में ही निकाल ली जाए",
            "कमाई का कम से कम 10% — अपने पास",
            "ये दान नहीं है। ये पैसा आपके पास ही रहता है।",
        ],
        cards=[
            dict(start=0.0, end=99, kicker="NIYAM 1",
                 big="पहले खुद को दो", sub="Pay yourself first"),
        ],
    ),
    dict(
        id="science",
        image="assets/img/06_roadmap.png",
        motion="pan_left",
        pad_in=0.4,
        pad_out=0.7,
        narration=("क्या ये सच में काम करता है? दो हज़ार एक में मैड्रियन और शी ने देखा — रिटायरमेंट प्लान में अपने आप जुड़ने की वजह से नए कर्मचारियों की भागीदारी सैंतीस प्रतिशत से छियासी प्रतिशत हो गई। सिर्फ़ डिफ़ॉल्ट बदला था। दो हज़ार चार में थेलर और बेनार्ज़ी ने सेव मोर टुमॉरो चलाया — लोगों ने पहले तय किया कि अगली बढ़ोतरी का हिस्सा बचत में जाएगा। अट्ठाईस महीनों में औसत बचत दर साढ़े तीन प्रतिशत से ग्यारह दशमलव छह प्रतिशत हो गई। मतलब — इरादा नहीं, सिस्टम काम करता है।"),
        captions=[
            "क्या ये सच में काम करता है? हाँ — पर वजह आपकी सोच नहीं है",
            "Madrian और Shea, 2001: नए कर्मचारियों की भागीदारी",
            "37% से 86% — सिर्फ़ default बदलने से",
            "सैलरी नहीं बढ़ी थी, बस अपने आप जुड़ना शुरू हुआ",
            "Thaler और Benartzi, 2004: Save More Tomorrow",
            "28 महीनों में औसत बचत दर 3.5% से 11.6%",
            "मतलब: इरादा नहीं, system काम करता है",
        ],
        cards=[
            dict(start=0.0, end=3.4, kicker="EVIDENCE", big="क्या ये काम करता है?"),
            dict(start=3.4, end=7.6, kicker="MADRIAN & SHEA · 2001",
                 big="37% से 86%", sub="नए कर्मचारियों की भागीदारी",
                 source="केवल default बदला — सैलरी नहीं"),
            dict(start=7.6, end=12.2, kicker="THALER & BENARTZI · 2004",
                 big="3.5% से 11.6%", sub="28 महीनों में औसत बचत दर",
                 source="Save More Tomorrow · JPE"),
            dict(start=12.2, end=99, kicker="सबक",
                 big="इरादा नहीं,", big2="system काम करता है"),
        ],
    ),
    dict(
        id="india",
        image="assets/img/04_india.png",
        motion="zoom_in",
        pad_in=0.4,
        pad_out=0.7,
        narration=("भारत का हिसाब। सैलरी चालीस हज़ार रुपये। अगले दिन ऑटो ट्रांसफर से चार हज़ार अलग खाते में। बाकी छत्तीस हज़ार में महीना चलता है। बारह महीने में अड़तालीस हज़ार — बिना कोई बढ़िया टिप अपनाए। और साल की बढ़ोतरी का आधा हिस्सा भी उसी खाते में।"),
        captions=[
            "भारत का हिसाब: सैलरी ₹40,000",
            "सैलरी के अगले दिन auto-transfer — ₹4,000 अलग खाते में",
            "बाकी ₹36,000 में महीना चलता है",
            "12 महीने = ₹48,000 — बिना कोई बढ़िया tip अपनाए",
            "बढ़ोतरी का आधा हिस्सा भी उसी खाते में",
        ],
        cards=[
            dict(start=0.0, end=3.2, kicker="INDIA EXAMPLE", big="₹40,000", sub="महीने की सैलरी"),
            dict(start=3.2, end=7.0, kicker="SALARY + 1 DAY", big="− ₹4,000", sub="auto-transfer, हाथ से नहीं"),
            dict(start=7.0, end=11.0, kicker="जीना इसी में", big="₹36,000", sub="महीने का खर्च"),
            dict(start=11.0, end=99, kicker="12 महीने", big="₹48,000",
                 sub="बिना कोई बढ़िया tip अपनाए"),
        ],
    ),
    dict(
        id="limits",
        image="assets/img/05_inflation.png",
        motion="zoom_out",
        pad_in=0.4,
        pad_out=0.7,
        narration=("अब ईमानदारी — ये नियम तीन जगह फेल होता है। पहली, महँगाई: बैंक में पड़ी बचत अगर महँगाई से धीमी है, तो पैसा काग़ज़ पर बढ़ता है और असल में घटता है। दूसरी, कम आमदनी: जहाँ दस प्रतिशत निकालने से किराया या दवाई कटती है, वहाँ पहले आपदा फंड और स्किल ज़रूरी है। तीसरी, और सबसे बड़ी — क्लासन की कहानियाँ काल्पनिक हैं। ये हिस्ट्री नहीं, पैरेबल है। उस बेबीलोन में क्रेडिट कार्ड नहीं था, मेडिकल इमरजेंसी का इंतज़ाम नहीं था, और नियम मानने वाला हर किरदार अमीर हो जाता है। असल ज़िंदगी में बचत करने वाला भी एक मेडिकल बिल से ख़त्म हो सकता है।"),
        captions=[
            "अब ईमानदारी — ये नियम तीन जगह फेल होता है",
            "1. महँगाई: बैंक में पड़ा पैसा काग़ज़ पर बढ़ता है, असल में घटता है",
            "2. कम आमदनी: जहाँ 10% निकालने से किराया कटता है",
            "वहाँ पहले आपदा फंड और skill ज़रूरी है",
            "3. Clason की कहानियाँ काल्पनिक हैं — history नहीं, parable",
            "उस बेबीलोन में credit card या medical emergency नहीं थी",
            "कहानी में नियम मानने वाला अमीर हो जाता है",
            "असल ज़िंदगी में एक मेडिकल बिल सब ख़त्म कर सकता है",
        ],
        cards=[
            dict(start=0.0, end=2.6, kicker="THE FINE PRINT", big="ये कहाँ फेल होता है"),
            dict(start=2.6, end=7.4, kicker="कमी 1", big="महँगाई",
                 sub="बचत अगर महँगाई से धीमी है, तो वो घाटा है"),
            dict(start=7.4, end=11.8, kicker="कमी 2", big="कम आमदनी",
                 sub="10% निकालने से घर नहीं चलता? पहले आपदा फंड"),
            dict(start=11.8, end=99, kicker="कमी 3", big="कहानी, इतिहास नहीं",
                 sub="Arkad काल्पनिक है · credit card, tax, medical shock — कुछ नहीं"),
        ],
    ),
    dict(
        id="fix1",
        image="assets/img/07_transfer.png",
        motion="pan_right",
        pad_in=0.4,
        pad_out=0.6,
        narration=("तो यहाँ है दो हज़ार छब्बीस वाला सुधरा हुआ वर्ज़न। एक — ऑटो ट्रांसफर सैलरी के अगले दिन, हाथ से नहीं। दो — पहले छोटा इमरजेंसी फंड, लक्ष्य तीन महीने का खर्च, शुरुआत पाँच सौ रुपये से भी। तीन — बचत को महँगाई से लड़ने वाली जगह पर ले जाइए; किसी स्कीम का नाम मैं नहीं दूँगा, जोखिम और समय आपका।"),
        captions=[
            "दो हज़ार छब्बीस वाला सुधरा हुआ version",
            "1. Auto-transfer — सैलरी के अगले दिन, हाथ से नहीं",
            "2. पहले छोटा emergency fund — लक्ष्य 3 महीने का खर्च",
            "शुरुआत ₹500 से भी हो सकती है",
            "3. बचत को महँगाई से लड़ने वाली जगह पर ले जाइए",
            "किसी scheme का नाम नहीं दूँगा — जोखिम और समय आपका",
        ],
        cards=[
            dict(start=0.0, end=2.4, kicker="2026 VERSION", big="सुधरा हुआ नियम"),
            dict(start=2.4, end=6.6, kicker="STEP 1", big="Auto-transfer",
                 sub="सैलरी के अगले दिन · हाथ से कभी नहीं"),
            dict(start=6.6, end=99, kicker="STEP 2", big="Emergency fund पहले",
                 sub="लक्ष्य 3 महीने का खर्च · शुरुआत ₹500 से"),
        ],
    ),
    dict(
        id="fix2",
        image="assets/img/08_skill.png",
        motion="zoom_in",
        pad_in=0.3,
        pad_out=0.6,
        narration=("चार — सबसे महँगा कर्ज़ पहले ख़त्म कीजिए; क्रेडिट कार्ड का ब्याज आपकी बचत की कमाई से कहीं ज़्यादा होता है। पाँच — हर महीने एक स्किल पर कुछ रुपये। क्लासन का सातवाँ नियम यही था, और सबसे ज़्यादा कमाने वाला भी।"),
        captions=[
            "4. सबसे महँगा कर्ज़ पहले ख़त्म कीजिए",
            "क्रेडिट कार्ड का ब्याज बचत की कमाई से कहीं ज़्यादा",
            "5. हर महीने एक skill पर कुछ रुपये",
            "Clason का सातवाँ नियम — और सबसे ज़्यादा कमाने वाला",
        ],
        cards=[
            dict(start=0.0, end=3.6, kicker="STEP 3", big="महँगा कर्ज़ पहले",
                 sub="36–48% सालाना वाला बैलेंस सबसे पहले"),
            dict(start=3.6, end=99, kicker="STEP 4", big="खुद पर invest",
                 sub="हर महीने एक skill · Clason का 7वाँ नियम"),
        ],
    ),
    dict(
        id="mistakes",
        image="assets/img/04_india.png",
        motion="pan_left",
        pad_in=0.3,
        pad_out=0.6,
        narration=("और वो गलतियाँ जो हर कोई करता है। एक — जो बचेगा वो बचा लेंगे; ये कभी नहीं होता। दो — बचत टालना, जबकि कर्ज़ का ब्याज रोज़ काम करता है। तीन — दस प्रतिशत को कानून बना देना; आमदनी कम है तो सौ रुपये भी शुरुआत है। चार — खाता देखना बंद कर देना।"),
        captions=[
            "और वो गलतियाँ जो हर कोई करता है",
            "1. 'जो बचेगा वो बचा लेंगे' — ये कभी नहीं होता",
            "2. बचत को टालना — जबकि कर्ज़ का ब्याज रोज़ काम करता है",
            "3. 10% को कानून बनाना — ₹100 भी शुरुआत है",
            "4. खाता देखना बंद कर देना",
        ],
        cards=[
            dict(start=0.0, end=2.2, kicker="COMMON MISTAKES", big="गलतियाँ"),
            dict(start=2.2, end=6.2, kicker="गलती 1", big="'जो बचेगा, वो बचा लेंगे'",
                 sub="ये कभी नहीं होता"),
            dict(start=6.2, end=10.2, kicker="गलती 2", big="बचत को टालना",
                 sub="कर्ज़ का ब्याज रोज़ काम करता है"),
            dict(start=10.2, end=99, kicker="गलती 3 और 4",
                 big="10% कानून नहीं है", sub="और खाता देखना बंद मत कीजिए"),
        ],
    ),
    dict(
        id="outro",
        image="assets/img/01_babylon.png",
        motion="zoom_out",
        pad_in=0.3,
        pad_out=1.2,
        narration=("एक लाइन में — अमीरी कमाई बढ़ने से नहीं, कमाई का हिस्सा पहले अपने पास रखने से शुरू होती है। अगले वीडियो में अर्काड का दूसरा नियम — ख़र्चे काबू में कैसे आएँ। काम की लगी तो सब्सक्राइब कीजिए — हर हफ़्ते एक किताब, आसान हिंदी में।"),
        captions=[
            "अमीरी कमाई बढ़ने से नहीं शुरू होती",
            "वो तब शुरू होती है जब हिस्सा पहले अपने पास रखा जाए",
            "अगला वीडियो: Arkad का दूसरा नियम — ख़र्चे काबू में",
            "हर हफ़्ते एक किताब, आसान हिंदी में — subscribe कीजिए",
        ],
        cards=[
            dict(start=0.0, end=4.4, kicker="TAKEAWAY", big="पहले खुद को दो",
                 sub="बाकी सब बाद में"),
            dict(start=4.4, end=99, kicker="NEXT WEEK", big="Niyam 2: ख़र्चे काबू में",
                 sub="Subscribe · Deep Explains"),
        ],
    ),
    # ---------------------------------------------------------------------
    # YouTube end screen. 18s of clean, dark frame with the exact placeholder
    # boxes where the channel owner drops YouTube's end-screen elements
    # (subscribe circle + two video cards). See content/07-end-screen.md.
    # ---------------------------------------------------------------------
    dict(
        id="endscreen",
        kind="endscreen",
        image="assets/img/01_babylon.png",
        motion="zoom_out",
        pad_in=0.0,
        pad_out=0.0,
        fixed_dur=12.0,
        narration="",
        captions=[],
        cards=[],
    ),
]

BRAND = "Deep Explains"
HANDLE = "@DeepExplainsOfficial"
SERIES = "The Richest Man in Babylon"

# End-screen targets (URLs from the channel's own public feed)
NEXT_EPISODE = dict(kicker="NEXT · EPISODE 2", title="Niyam 2: ख़र्चे काबू में", meta="~4 min · Hindi")
PREV_VIDEO = dict(kicker="पहले देखें", title="30-Day Money Reset Plan", meta="Joseph Murphy · Part 3")
