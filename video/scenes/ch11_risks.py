import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from manim import *  # noqa: E402,F403

from style import *  # noqa: E402,F403

# Qualitative facts as stated in visa_report.md (sections 4-6, 9; analysis/data/qualitative_facts.csv)
RED_TEAM = [  # (argument, verdict, survives)
    ("growth multiple in a 5% world", "holds", True),
    ("regulators on every side", "partly", False),
    ("big banks routing around Visa", "holds", True),
    ("state rails take emerging markets", "holds", True),
    ("stablecoins disrupt cross-border", "weak for now", False),
    ("the economy is turning", "near-term only", False),
    ("litigation never ends", "mostly not", False),
    ("+12% in two weeks", "timing only", False),
    ("base rates favour the index", "holds", True),
    ("Norway frictions: ASK, tax, FX", "weak", False),
]


def block(title, lines, color, width=None):
    t = txt(title, size=24, color=color, weight="SEMIBOLD")
    ls = VGroup(*[txt(l, size=19, color=INK2) for l in lines])
    g = VGroup(t, *ls).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
    return g


class Ch11Risks(Chapter):
    KEY = "risks"
    CONCEPTS = ["moat", "routing and steering", "account-to-account rails", "regulatory risk", "red team"]

    def construct(self):
        self.title_card()

        # ---------------------------------------------------------- four attacks on the moat
        h = heading("Four slow attacks on the moat")
        c = [0.6, -0.55, 0]
        moat = Annulus(inner_radius=0.95, outer_radius=1.25, fill_color=BLUE, fill_opacity=0.18, stroke_width=0).move_to(c)
        core = Circle(radius=0.95, fill_color=PANEL, fill_opacity=1, stroke_color=BLUE, stroke_width=3).move_to(c)
        vl = txt("Visa", size=34, weight="BOLD").move_to(c)
        with self.say("m1"):
            self.play(FadeIn(h), FadeIn(moat), FadeIn(core), FadeIn(vl), run_time=0.8)
        b1 = block("1  US routing and steering rules", ["merchants would choose the network", "(most important)"], ORANGE)
        b1.move_to([-4.1, 0.1, 0])
        a1 = Arrow([-2.2, -0.55, 0], [c[0] - 1.3, c[1], 0], buff=0, color=ORANGE, stroke_width=6)
        b1b = block("issuer networks", ["Capital One, owner of Discover:", "~25m debit cards moved, Jul 2026"], ORANGE)
        b1b.next_to(b1, DOWN, buff=0.35, aligned_edge=LEFT)
        with self.say("m2") as d:
            self.play(GrowArrow(a1), FadeIn(b1, shift=0.1 * RIGHT), run_time=0.8)
        with self.say("m3") as d:
            self.at(d * 0.3, FadeIn(b1b, shift=0.1 * RIGHT), run_time=0.7)
        b2 = block("2  State instant payments", ["Pix ~42% of Brazilian online purchases (2025)", "UPI 24.07bn transactions in Sep 2026",
                                                "Europe: Wero, a digital euro"], YELLOW)
        b2.move_to([c[0] + 2.5, 1.65, 0])
        a2 = Arrow([c[0], 1.05, 0], [c[0], c[1] + 1.3, 0], buff=0, color=YELLOW, stroke_width=6)
        with self.say("m4") as d:
            self.play(GrowArrow(a2), FadeIn(b2[0]), run_time=0.6)
            self.at(d * 0.12, FadeIn(b2[1]), run_time=0.5)
            self.at(d * 0.5, FadeIn(b2[2]), run_time=0.5)
            self.at(d * 0.8, FadeIn(b2[3]), run_time=0.5)
        b3 = block("3  Stablecoins", ["in cross-border payments,", "Visa's richest line"], VIOLET).move_to([5.05, -0.9, 0])
        a3 = Arrow([b3.get_left()[0] - 0.2, b3[0].get_y(), 0], [c[0] + 1.3, c[1], 0], buff=0, color=VIOLET, stroke_width=6)
        b4 = block("4  Wallets and AI agents", ["picking the cheapest rail"], MAGENTA).move_to([c[0] + 2.6, -3.0, 0])
        a4 = Arrow([c[0], -2.75, 0], [c[0], c[1] - 1.3, 0], buff=0, color=MAGENTA, stroke_width=6)
        tags = VGroup(tag("F").next_to(b1b[0], RIGHT, buff=0.12), tag("F").next_to(b2[0], RIGHT, buff=0.12))
        with self.say("m5") as d:
            self.play(GrowArrow(a3), FadeIn(b3), run_time=0.7)
            self.at(d * 0.45, GrowArrow(a4), FadeIn(b4), FadeIn(tags), run_time=0.7)
        self.clear()

        # ---------------------------------------------------------- regulation timeline
        h = heading("Regulators are pressing at the same time")
        events = [("2011", "US debit fee cap", "Visa +15% in a day:\nrule looser than feared", BLUE),
                  ("Sep 2024", "DOJ sues Visa", "debit monopolisation", ORANGE),
                  ("Jan 2026", "Credit Card\nCompetition Act", "President's endorsement,\nno vote yet", ORANGE),
                  ("Jun 2026", "merchant settlement", "preliminary approval:\nsurcharges allowed", YELLOW),
                  ("16 Nov 2026", "fairness hearing", "(reported)", YELLOW),
                  ("~2028", "DOJ trial", "expected", ORANGE)]
        line = Line([-6.3, -0.2, 0], [6.3, -0.2, 0], color=FAINT, stroke_width=3)
        xs = [-5.4 + k * 2.16 for k in range(len(events))]
        ev = []
        for k, (when, what, sub, col) in enumerate(events):
            dot = Dot([xs[k], -0.2, 0], radius=0.1, color=col)
            w = txt(when, size=20, color=col, weight="SEMIBOLD")
            a = txt(what, size=20, weight="SEMIBOLD")
            b = txt(sub, size=17, color=INK2)
            lab = VGroup(w, a, b).arrange(DOWN, buff=0.08)
            if k % 2 == 0:
                lab.next_to(dot, UP, buff=0.3)
            else:
                lab.next_to(dot, DOWN, buff=0.3)
            ev.append(VGroup(dot, lab))
        ukeu = chip("UK and EU: fee caps, investigations, damages claims", color=ORANGE, size=21).to_edge(DOWN, buff=0.4)
        with self.say("reg1") as d:
            self.play(FadeIn(h), Create(line), run_time=0.6)
            self.at(d * 0.2, FadeIn(ev[3], shift=0.1 * UP), run_time=0.6)
            self.at(d * 0.75, FadeIn(ev[4], shift=0.1 * UP), run_time=0.6)
        with self.say("reg2") as d:
            self.play(FadeIn(ev[2], shift=0.1 * UP), run_time=0.6)
            self.at(d * 0.4, FadeIn(ev[1], shift=0.1 * UP), FadeIn(ev[5], shift=0.1 * UP), run_time=0.7)
            self.at(d * 0.78, FadeIn(ukeu), run_time=0.6)
        lesson = VGroup(txt("regulation has hit the multiple more than long-run earnings", size=22, color=BLUE), tag("J")).arrange(RIGHT, buff=0.12)
        lesson.next_to(ukeu, UP, buff=0.3)
        with self.say("reg3") as d:
            self.play(FadeIn(ev[0], shift=0.1 * UP), run_time=0.5)
            self.play(Indicate(ev[0][0], color=BLUE), run_time=0.6)     # not in the same play: it would snapshot the faded dot
            self.at(d * 0.62, FadeIn(lesson), run_time=0.6)
        self.clear()

        # ---------------------------------------------------------- macro dashboard
        h = heading("The economy, October 2026")
        tiles_ = [("+29k", "US payrolls, September", ORANGE), ("4.2%", "unemployment, highest since 2021", ORANGE),
                  ("3.7%", "CPI inflation, September", ORANGE), ("+0.25 pt", "Fed rate rise, 16 Sep", ORANGE),
                  ("5.08%", "10-year Treasury yield", ORANGE)]
        tiles = VGroup()
        for v_, l_, c_ in tiles_:
            st = stat(v_, l_, c_, vsize=44, lsize=20)
            tiles.add(boxed(st, color=FAINT, buff=0.25))
        top_row = VGroup(*tiles[:3]).arrange(RIGHT, buff=0.3)
        bot_row = VGroup(*tiles[3:]).arrange(RIGHT, buff=0.3)
        VGroup(top_row, bot_row).arrange(DOWN, buff=0.3).next_to(h, DOWN, buff=0.45).set_x(0)
        ft = tag("F").next_to(h, RIGHT, buff=0.2)
        rj = tag("J")
        rec = VGroup(txt("In a recession:", size=24, weight="SEMIBOLD"),
                     VGroup(mtxt("revenue " + hl("≈ holds", AQUA) + "   ·   share price " + hl("−30% or more", ORANGE) + "  (2008, 2020)", size=24),
                            rj).arrange(RIGHT, buff=0.15),
                     ).arrange(DOWN, buff=0.18, aligned_edge=LEFT).move_to([0, -2.75, 0])
        with self.say("mac") as d:
            self.play(FadeIn(h), run_time=0.4)
            self.play(LaggedStart(*[FadeIn(t_, shift=0.1 * UP) for t_ in tiles], lag_ratio=0.25), FadeIn(ft), run_time=min(d * 0.45, 4))
            self.at(d * 0.58, FadeIn(rec), run_time=0.8)
        self.clear()

        # ---------------------------------------------------------- red team
        h = heading("Red team: ten arguments against buying")
        chips = VGroup()
        rows_ = [VGroup(txt(f"{k:>2}  {arg}", size=19, color=INK), txt(verdict, size=16, color=YELLOW if ok else MUTED)).arrange(RIGHT, buff=0.22)
                 for k, (arg, verdict, ok) in enumerate(RED_TEAM, start=1)]
        bw = max(r_.width for r_ in rows_) + 0.4
        for row in rows_:
            box = RoundedRectangle(corner_radius=0.1, width=bw, height=0.58, fill_color=PANEL, fill_opacity=1,
                                   stroke_color=FAINT, stroke_width=1.5)
            row.move_to(box).align_to(box, LEFT).shift(0.18 * RIGHT)
            chips.add(VGroup(box, row))
        col1 = VGroup(*chips[:5]).arrange(DOWN, buff=0.16)
        col2 = VGroup(*chips[5:]).arrange(DOWN, buff=0.16)
        VGroup(col1, col2).arrange(RIGHT, buff=0.3).next_to(h, DOWN, buff=0.45).set_x(0)
        with self.say("red1") as d:
            self.play(FadeIn(h), run_time=0.4)
            self.play(LaggedStart(*[FadeIn(c_) for c_ in chips], lag_ratio=0.1), run_time=1.6)
            anims = []
            for (arg, verdict, ok), c_ in zip(RED_TEAM, chips):
                if ok:
                    anims.append(c_[0].animate.set_stroke(YELLOW, width=3))
                else:
                    anims.append(c_.animate.set_opacity(0.4))
            self.at(d * 0.3, *anims, run_time=0.8)
        verdict = boxed(VGroup(txt("At $402: full price for a great business", size=28, weight="SEMIBOLD"),
                               txt("whose growth is more likely to slow than speed up", size=24, color=INK2)).arrange(DOWN, buff=0.12),
                        color=YELLOW, buff=0.3)
        verdict.add(tag("J").next_to(verdict, UR, buff=-0.45))
        with self.say("red2") as d:
            self.play(FadeOut(VGroup(col1, col2)), run_time=0.5)
            self.play(FadeIn(verdict, scale=0.95), run_time=0.8)
        self.finish()
