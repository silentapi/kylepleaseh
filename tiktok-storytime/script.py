# Part 1 script, written as storytelling: cold open, dramatic irony, narrator asides, setup/payoff,
# escalation in threes, callback, false ending, cliffhanger.
# Fields: v = visual, k = 'cap' (karaoke caption) | 'card' (red quote card) | 'title' (visual carries the text)
#   say = words spoken (also used for caption timing), show = on-screen text, tts = text fed to the voice model
#   d = delivery: N natural, B building, D dramatic, P peak    who = label on quote cards
#   mark = 'cut' (music tape-stop) | 'thurs' (music re-enters on the sax) | 'promised' (50-mile pill)
#   pause = breath after the line (s), sfx = sound effect at line start
SEGMENTS = [
 # COLD OPEN
 dict(v="clock", k="card", d="P", who="HER BOSS", say="Enjoy waiting here until five P.M.", show="“Enjoy waiting here until 5pm.”",
      tts="Enjoy waiting here... until five P.M.", pause=0.45, sfx="boom"),
 dict(v="clock", k="cap", d="B", say="That's the last thing her boss said before he walked out.", pause=0.3),
 dict(v="clock", k="cap", d="B", say="What he didn't know, she was writing down every single word.",
      show="What he didn't know… she was writing down every single word.", tts="What he didn't know? She was writing down... every single word.", pause=0.6, sfx="whoosh"),
 # SETUP
 dict(v="hall", k="cap", d="N", say="Okay. Let me back up.", pause=0.3),
 dict(v="hall", k="cap", d="N", say="Ben runs a healthcare department. Tina's one of his nurses.", pause=0.2),
 dict(v="pip", k="cap", d="N", say="And Ben's been trying to get her on a performance plan.", pause=0.2),
 dict(v="pip", k="cap", d="B", say="Just one problem.", pause=0.35),
 dict(v="pip", k="cap", d="N", say="H.R. keeps telling him", show="HR keeps telling him…", tts="H.R. keeps telling him...", pause=0.35),
 dict(v="pip_denied", k="cap", d="D", say="Not yet.", show="…NOT YET.", tts="Not yet.", pause=0.7, sfx="stamp"),
 # THE ASSIGNMENT
 dict(v="highway", k="cap", d="N", say="Then, out of nowhere, her assignments start changing.", pause=0.25, sfx="whoosh"),
 dict(v="highway", k="cap", d="N", say="First up? A solo home visit.", pause=0.25),
 dict(v="miles", k="cap", d="B", say="Seventy miles away. Two hours there. Two hours back.", show="70 miles away. 2 hours there. 2 hours back.",
      pause=0.4, sfx="boom"),
 dict(v="miles", k="cap", d="N", mark="promised", say="Tina says when she was hired, she was promised never more than fifty.",
      show="Tina says when she was hired, she was promised never more than 50.", pause=0.3),
 dict(v="mom", k="cap", d="N", say="And this part matters.", pause=0.3),
 dict(v="mom", k="cap", d="N", say="Tina has a daughter with special needs, who needs her mom nearby.", pause=0.4),
 dict(v="mom", k="cap", d="B", say="So she tells Ben all of this. And his answer?", pause=0.35),
 dict(v="mom", k="card", d="D", who="BEN", say="You would've been paid mileage.", show="“You would’ve been paid mileage.”", pause=0.6, sfx="boom"),
 # THE TURN
 dict(v="black", k="cap", d="D", mark="cut", say="So she says no.", pause=0.5, sfx="hit"),
 dict(v="black", k="cap", d="P", say="And that's when it gets ugly.", show="And that's when it gets… ugly.", tts="And that's when it gets... ugly.", pause=0.5),
 # THE CONFRONTATION
 dict(v="thursday", k="title", d="B", mark="thurs", say="Thursday. Eleven thirty A.M.", show="THURSDAY. 11:30 AM.", pause=0.35, sfx="boom"),
 dict(v="office", k="cap", d="N", say="Ben walks up to her desk, and Tina asks him for one thing.", pause=0.3, sfx="whoosh"),
 dict(v="office", k="cap", d="N", say="Put it in writing.", show="“Put it in writing.”", pause=0.35),
 dict(v="office", k="cap", d="D", say="He refuses.", pause=0.45),
 dict(v="nurses", k="cap", d="N", say="So she asks how any reasonable adult is supposed to respond to coercion.", pause=0.3),
 dict(v="nurses", k="cap", d="B", say="And he says", show="And he says…", tts="And he says...", pause=0.3),
 dict(v="nurses", k="card", d="D", who="BEN", say="I'd expect them to say yes and okay.", show="“I’d expect them to say yes and okay.”", pause=0.45, sfx="boom"),
 dict(v="nurses", k="cap", d="N", say="And he wasn't done.", pause=0.25),
 dict(v="nurses", k="card", d="D", who="BEN", say="Any good nurse would change trash bags.", show="“Any good nurse would change trash bags.”", pause=0.45, sfx="boom"),
 dict(v="nurses", k="cap", d="B", say="And then, the big one.", pause=0.3),
 dict(v="nurses", k="card", d="P", who="BEN", say="Are you reconsidering your time here?", show="“Are you reconsidering your time here?”", pause=0.6, sfx="boom"),
 # THE 5PM LINE
 dict(v="error", k="cap", d="N", say="Oh, and her computer? Broken. The backup? Also broken.", pause=0.25, sfx="glitch"),
 dict(v="error", k="cap", d="N", say="Tina says he told her to just sit there until I.T. fixes it.", show="Tina says he told her to just sit there until IT fixes it.", pause=0.3),
 dict(v="error", k="cap", d="B", say="And on his way out the door", show="And on his way out the door…", tts="And on his way out the door...", pause=0.45),
 dict(v="clock2", k="card", d="P", who="BEN", say="Enjoy waiting here until five P.M.", show="“Enjoy waiting here until 5pm.”",
      tts="Enjoy waiting here... until five P.M.", pause=0.8, sfx="boom"),
 # THE PAYOFF
 dict(v="typing", k="cap", d="N", say="But remember what I said at the start?", pause=0.35, sfx="whoosh"),
 dict(v="typing", k="cap", d="B", say="She was writing it all down.", pause=0.3),
 dict(v="hrcase", k="cap", d="N", say="Every quote. Every timestamp. Straight into her open H.R. case.",
      show="Every quote. Every timestamp. Straight into her open HR case.", pause=0.3, sfx="stamp"),
 dict(v="hrcase", k="cap", d="B", say="And the last line of her email?", pause=0.35),
 dict(v="hrcase", k="card", d="D", who="TINA · HER EMAIL", say="As mandated, I am remaining stationary at my desk until five P.M.",
      show="“As mandated, I am remaining stationary at my desk until 5:00 PM.”", pause=0.8, sfx="boom"),
 # FALSE ENDING + CLIFFHANGER
 dict(v="notif", k="cap", d="B", say="But it's not over. Because Ben just replied.", pause=0.3, sfx="ding"),
 dict(v="notif", k="cap", d="B", say="And he says Tina left out one very important detail", show="And he says Tina left out one very important detail…",
      tts="And he says Tina left out one very important detail...", pause=0.35),
 dict(v="notif", k="cap", d="D", say="A working computer. That she refused to use.", show="…a working computer. That she REFUSED to use.", pause=0.45, sfx="boom"),
 dict(v="part2", k="cap", d="B", say="So, whose side are you on?", show="So… whose side are you on?", tts="So... whose side are you on?", pause=0.3),
 dict(v="part2", k="cap", d="N", say="Follow, because part two is his side of the story.", show="Follow. Part 2 is his side of the story.", pause=1.2),
]
