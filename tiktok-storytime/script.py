# Part 1 script. Each segment: visual, kind ('cap' = karaoke caption, 'card' = red quote card),
# spoken text (TTS-friendly), display text (what is on screen), pause after (seconds), sfx.
SEGMENTS = [
 # HOOK
 dict(v="clock",   k="card", say="Enjoy waiting here until five P.M.", show="“Enjoy waiting here until 5pm.”", pause=0.45, sfx="boom"),
 dict(v="clock",   k="cap",  say="Her boss said that to her face.", pause=0.2),
 dict(v="clock",   k="cap",  say="So she put it in writing, and sent it straight to H.R.", show="So she put it in writing… and sent it straight to HR.", pause=0.55, sfx="whoosh"),
 # SETUP
 dict(v="hall",    k="cap",  say="Meet Ben. Healthcare director.", pause=0.2),
 dict(v="pip",     k="cap",  say="He's been trying to put his nurse, Tina, on a performance plan.", pause=0.15),
 dict(v="pip",     k="cap",  say="H.R. won't let him.", show="HR won't let him.", pause=0.55),
 dict(v="pip_denied", k="cap", say="Yet.", show="…YET.", pause=0.7, sfx="stamp"),
 # ASSIGNMENT
 dict(v="highway", k="cap",  say="Then, suddenly, her assignments start changing.", pause=0.2, sfx="whoosh"),
 dict(v="highway", k="cap",  say="First, a solo home visit.", pause=0.15),
 dict(v="miles",   k="cap",  say="Seventy miles away. Two hours each way.", show="70 miles away. 2 hours each way.", pause=0.4, sfx="boom"),
 dict(v="miles",   k="cap",  say="Tina says she was promised never more than fifty.", show="Tina says she was promised never more than 50.", pause=0.15),
 dict(v="mom",     k="cap",  say="She's never been trained to go alone.", pause=0.15),
 dict(v="mom",     k="cap",  say="And she has a special needs daughter who needs her close.", show="And she has a special-needs daughter who needs her close.", pause=0.45),
 dict(v="mom",     k="cap",  say="Ben's answer?", pause=0.3),
 dict(v="mom",     k="card", say="You would've been paid mileage.", show="“You would’ve been paid mileage.”", pause=0.6, sfx="boom"),
 # TURN
 dict(v="black",   k="cap",  say="She says no.", pause=0.5, sfx="hit"),
 dict(v="black",   k="cap",  say="And that's when it gets ugly.", pause=0.5),
 # CONFRONTATION
 dict(v="thursday",k="title", say="Thursday. Eleven thirty A.M.", show="THURSDAY. 11:30 AM.", pause=0.35, sfx="boom"),
 dict(v="office",  k="cap",  say="Ben walks up to her desk.", pause=0.15, sfx="whoosh"),
 dict(v="office",  k="cap",  say="She asks him to put it in writing. He refuses.", pause=0.2),
 dict(v="nurses",  k="cap",  say="She asks how anyone is supposed to respond to coercion.", pause=0.3),
 dict(v="nurses",  k="card", say="I'd expect them to say yes and okay.", show="“I’d expect them to say yes and okay.”", pause=0.35, sfx="boom"),
 dict(v="nurses",  k="cap",  say="Then", show="Then…", pause=0.2),
 dict(v="nurses",  k="card", say="Any good nurse would change trash bags.", show="“Any good nurse would change trash bags.”", pause=0.35, sfx="boom"),
 dict(v="nurses",  k="cap",  say="Then", show="Then…", pause=0.2),
 dict(v="nurses",  k="card", say="Are you reconsidering your time here?", show="“Are you reconsidering your time here?”", pause=0.6, sfx="boom"),
 # 5PM LINE
 dict(v="error",   k="cap",  say="Her computer's dead. The backup's dead.", pause=0.2, sfx="glitch"),
 dict(v="error",   k="cap",  say="She says he told her to just sit there until I.T. fixes it.", show="She says he told her to just sit there until IT fixes it.", pause=0.2),
 dict(v="error",   k="cap",  say="And on his way out the door", show="And on his way out the door…", pause=0.45),
 dict(v="clock2",  k="card", say="Enjoy waiting here until five P.M.", show="“Enjoy waiting here until 5pm.”", pause=0.8, sfx="boom"),
 # EMAIL
 dict(v="typing",  k="cap",  say="So Tina did what nurses do best.", pause=0.2, sfx="whoosh"),
 dict(v="typing",  k="cap",  say="She documented. Every quote. Every timestamp.", pause=0.15),
 dict(v="hrcase",  k="cap",  say="Straight into her open H.R. case.", show="Straight into her open HR case.", pause=0.3, sfx="stamp"),
 dict(v="hrcase",  k="cap",  say="And her final line?", pause=0.3),
 dict(v="hrcase",  k="card", say="As mandated, I am remaining stationary at my desk until five P.M.", show="“As mandated, I am remaining stationary at my desk until 5:00 PM.”", pause=0.8, sfx="boom"),
 # CLIFFHANGER
 dict(v="notif",   k="cap",  say="But Ben just replied.", pause=0.3, sfx="ding"),
 dict(v="notif",   k="cap",  say="And he says she left something out", show="And he says she left something out…", pause=0.3),
 dict(v="notif",   k="cap",  say="a working computer. That she refused to use.", show="a working computer. That she REFUSED to use.", pause=0.45, sfx="boom"),
 dict(v="part2",   k="cap",  say="Whose side are you on?", pause=0.25),
 dict(v="part2",   k="cap",  say="Follow. Part two is his reply.", show="Follow. Part 2 is his reply.", pause=1.2),
]
