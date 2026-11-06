# Part 1, v7: malicious-compliance framing. Built with the "short-drama-hook-engineering" skill rules
# (conflict in the first 1-3s, start late, pressure fast, reaction/power shift when a beat relaxes,
# last beat pulls into part 2) + "but / so / until" connectors instead of "and then".
# Narration is generated per PARAGRAPH ("p") so it flows; lines are for captions/visuals only.
# Music plan (Batida Funk Medley): P0-P1 over the sax riff, beat switch on P2, P3 card on a hit,
# P4 music cuts out ('cut'), music slams back on "Thursday" ('thurs'), biggest drop on the P8 payoff.
SEGMENTS = [
 # P0 HOOK: accusation + malicious-compliance promise
 dict(p=0, v="clock", k="card", who="HER BOSS", say="Enjoy waiting here until five P.M.", show="“Enjoy waiting here until 5pm.”", sfx="boom"),
 dict(p=0, v="clock", k="cap", say="Her boss said that to her face."),
 dict(p=0, v="clock", k="cap", say="So she did, and turned every word into evidence.", show="So she did… and turned every word into EVIDENCE.", sfx="whoosh"),
 # P1 STAKES
 dict(p=1, v="pip", k="cap", say="Ben's a healthcare director, and he's been trying to put his nurse Tina on a performance plan.",
      tts="Ben's a healthcare director, and he's been trying to put his nurse, Teena, on a performance plan."),
 dict(p=1, v="pip_denied", k="cap", say="But H.R. keeps blocking it.", show="But HR keeps BLOCKING it.", sfx="stamp"),
 # P2 PRESSURE + re-hook
 dict(p=2, v="highway", k="cap", say="Until her assignments start changing.", sfx="whoosh"),
 dict(p=2, v="miles", k="cap", say="A solo home visit. Seventy miles away. Two hours each way.", show="A solo home visit. 70 miles away. 2 hours each way.", sfx="boom"),
 dict(p=2, v="miles", k="cap", mark="promised", say="She was promised never more than fifty.", show="She was promised: never more than 50."),
 dict(p=2, v="mom", k="cap", say="And her special needs daughter needs her close by.", show="And her special-needs daughter needs her close by."),
 dict(p=2, v="mom", k="cap", say="And this is where it gets personal.", show="And this is where it gets PERSONAL."),
 # P3 THE TURN: juxtaposition + reaction beat
 dict(p=3, v="mom", k="cap", say="She tells him about her daughter."),
 dict(p=3, v="mom", k="cap", say="And his answer is about gas money.", show="And his answer… is about GAS MONEY."),
 dict(p=3, v="mom", k="card", who="BEN", say="You would've been paid mileage.", show="“You would’ve been paid mileage.”", sfx="boom"),
 dict(p=3, v="mom", k="cap", say="Her daughter, and he's talking mileage.", show="Her DAUGHTER… and he's talking mileage."),
 # P4 POINT OF NO RETURN (music cuts out)
 dict(p=4, v="black", k="cap", mark="cut", say="So she says no.", sfx="hit"),
 dict(p=4, v="black", k="cap", say="And that's when it gets ugly.", show="And that's when it gets… ugly."),
 # P5 CONFRONTATION (music slams back on "Thursday")
 dict(p=5, v="thursday", k="title", mark="thurs", say="Thursday. Eleven thirty.", show="THURSDAY. 11:30 AM.", sfx="boom"),
 dict(p=5, v="office", k="cap", say="He's at her desk. She asks him to put it in writing.", sfx="whoosh"),
 dict(p=5, v="office", k="cap", say="He refuses.", show="He REFUSES."),
 dict(p=5, v="nurses", k="cap", say="She asks how any reasonable adult is supposed to respond to that kind of pressure."),
 dict(p=5, v="nurses", k="card", who="BEN", say="I'd expect them to say yes and okay.", show="“I’d expect them to say yes and okay.”", sfx="boom"),
 # P6 ESCALATION IN THREES
 dict(p=6, v="nurses", k="cap", say="Then,", show="Then…"),
 dict(p=6, v="nurses", k="card", who="BEN", say="Any good nurse would change trash bags.", show="“Any good nurse would change trash bags.”", sfx="boom"),
 dict(p=6, v="nurses", k="cap", say="Then,", show="Then…"),
 dict(p=6, v="nurses", k="card", who="BEN", say="Are you reconsidering your time here?", show="“Are you reconsidering your time here?”", sfx="boom"),
 # P7 CALLBACK to the hook
 dict(p=7, v="error", k="cap", say="Her computer's dead.", sfx="glitch"),
 dict(p=7, v="error", k="cap", say="She says he told her to just wait at her desk until I.T. fixes it.", show="She says he told her to just wait at her desk until IT fixes it."),
 dict(p=7, v="error", k="cap", say="And on his way out,", show="And on his way out…"),
 dict(p=7, v="clock2", k="card", who="BEN", say="Enjoy waiting here until five P.M.", show="“Enjoy waiting here until 5pm.”", sfx="boom"),
 # P8 PAYOFF: the malicious compliance (biggest drop)
 dict(p=8, v="typing", k="cap", say="So she did.", show="So she DID.", sfx="hit"),
 dict(p=8, v="typing", k="cap", say="She sat right there and wrote it all down."),
 dict(p=8, v="hrcase", k="cap", say="Every quote. Every timestamp. Straight into her open H.R. case.", show="Every quote. Every timestamp. Straight into her open HR case.", sfx="stamp"),
 dict(p=8, v="hrcase", k="cap", say="And she signed off with,", show="And she signed off with…"),
 dict(p=8, v="hrcase", k="card", who="TINA · HER EMAIL", say="As mandated, I am remaining stationary at my desk until five P.M.", show="“As mandated, I am remaining stationary at my desk until 5:00 PM.”", sfx="boom"),
 # P9 EXIT BRIDGE: a real dilemma for the comments
 dict(p=9, v="notif", k="cap", say="Then Ben hit reply.", sfx="ding"),
 dict(p=9, v="notif", k="cap", say="And according to him, she left out a lot.", show="And according to him… she left out A LOT.", sfx="boom"),
 dict(p=9, v="part2", k="cap", say="Was she protecting herself, or refusing to do her job?", show="Was she protecting herself… or refusing to do her job?"),
 dict(p=9, v="part2", k="cap", say="Part two.", show="PART 2 →"),
]
