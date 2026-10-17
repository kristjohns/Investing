import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from manim import *  # noqa: E402,F403

import data  # noqa: E402
from style import *  # noqa: E402,F403


class Ch14Conclusion(Chapter):
    KEY = "conclusion"
    CONCEPTS = []

    def construct(self):
        price = data.price()
        bb = data.buy_below().set_index(["target_expected_return", "horizon_years"]).loc[(0.10, 10)]
        grid = data.dcf_grid()
        self.title_card()

        # ---------------------------------------------------------- three questions, three answers
        h = heading("Three questions, three answers")
        qs = [("Is Visa a great business?", "Yes", AQUA, "F", "a toll on global spending · margins above 60% · almost no capital · grew in 2009"),
              ("Is the price attractive?", "No", ORANGE, "E", "priced for its track record · expected ≈ 8.5% a year, like the index"),
              ("Better than the index fund for you?", "Not at this price", YELLOW, "J", "concentrated risk without extra expected return")]
        rows = VGroup()
        for q, a, c_, k_, why in qs:
            qt = txt(q, size=28, weight="SEMIBOLD")
            at = VGroup(txt(a, size=30, color=c_, weight="BOLD"), tag(k_)).arrange(RIGHT, buff=0.12)
            wt = txt(why, size=19, color=INK2)
            rows.add(VGroup(qt, at, wt))
        for i, r_ in enumerate(rows):
            yy = 1.75 - 1.45 * i
            r_[0].move_to([-6.3, yy, 0], aligned_edge=LEFT)
            r_[1].move_to([3.0, yy, 0], aligned_edge=LEFT)
            r_[2].move_to([-6.3, yy - 0.5, 0], aligned_edge=LEFT)
        with self.say("a0") as d:
            self.play(FadeIn(h), LaggedStart(*[FadeIn(r_[0], shift=0.1 * RIGHT) for r_ in rows], lag_ratio=0.3), run_time=1.2)
        for i, key in enumerate(("a1", "a2", "a3")):
            with self.say(key) as d:
                self.at(d * 0.18, FadeIn(rows[i][1], scale=0.9), run_time=0.5)
                self.at(d * 0.4, FadeIn(rows[i][2]), run_time=0.6)
        self.clear()

        # ---------------------------------------------------------- the recommendation
        h = heading("The recommendation")
        verdict = VGroup(txt("HOLD / WAIT", size=80, color=YELLOW, weight="BOLD"), tag("J", 1.6)).arrange(RIGHT, buff=0.3)
        conf = txt("confidence: medium  ·  keep the money in the index fund for now", size=24, color=INK2)
        VGroup(verdict, conf).arrange(DOWN, buff=0.25, aligned_edge=LEFT).next_to(h, DOWN, buff=0.45, aligned_edge=LEFT)
        with self.say("rec1") as d:
            self.play(FadeIn(h), FadeIn(verdict, scale=0.9), run_time=0.8)
            self.at(d * 0.45, FadeIn(conf), run_time=0.6)
        # price ladder
        lad = NumberLine(x_range=[320, 420, 20], length=11.6, color=FAINT, include_ticks=True, tick_size=0.06, stroke_width=2).move_to(1.6 * DOWN)
        ticks = VGroup(*[txt(f"${v}", size=20, color=MUTED).next_to(lad.n2p(v), DOWN, buff=0.18) for v in range(320, 421, 20)])
        def zone(a, b, col, label):
            r_ = Rectangle(width=lad.n2p(b)[0] - lad.n2p(a)[0], height=0.5, fill_color=col, fill_opacity=0.35, stroke_width=0)
            r_.move_to((lad.n2p(a) + lad.n2p(b)) / 2 + 0.25 * UP)
            l_ = txt(label, size=20, color=col).next_to(r_, UP, buff=0.12)
            return VGroup(r_, l_)
        buy_at = round(bb["buy_below_price"] / 5) * 5
        z1 = zone(320, buy_at, AQUA, f"≤ ${buy_at:.0f}: buy")
        z2 = zone(buy_at, 380, YELLOW, "starter, ≤ 1/3")
        z3 = zone(380, 420, ORANGE, "wait")
        now = VGroup(Dot(lad.n2p(price), radius=0.11, color=INK),
                     txt(f"today ${price:.2f}", size=21, weight="SEMIBOLD"))
        now[1].next_to(now[0], DOWN, buff=0.55)
        steps = txt("consider buying in two or three steps", size=21, color=INK2).to_edge(DOWN, buff=0.35)
        with self.say("rec2") as d:
            self.play(Create(lad), FadeIn(ticks), FadeIn(now), run_time=0.6)
            self.play(FadeIn(z1), run_time=0.5)
            self.at(d * 0.45, FadeIn(z2), FadeIn(z3), run_time=0.7)
            self.at(d * 0.78, FadeIn(steps), run_time=0.5)
        self.clear()
        h = heading("Revisit after two dates")
        dates = VGroup(chip("27 October 2026: fiscal 2026 results", color=BLUE, size=26),
                       chip("16 November 2026: settlement fairness hearing (reported)", color=BLUE, size=26)).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        dates.next_to(h, DOWN, buff=0.55, aligned_edge=LEFT)
        with self.say("rec3") as d:
            self.play(FadeIn(h), FadeIn(dates[0], shift=0.1 * RIGHT), run_time=0.6)
            self.at(d * 0.5, FadeIn(dates[1], shift=0.1 * RIGHT), run_time=0.6)
        r8 = grid.loc[0.10, 0.08]
        why = boxed(VGroup(txt("why only medium confidence", size=24, weight="SEMIBOLD"),
                           mtxt(f"at an {hl('8.0%', AQUA)} discount rate the DCF gives {hl(f'${r8:.0f}', AQUA)}: that would be a buy", size=24)
                           ).arrange(DOWN, buff=0.15, aligned_edge=LEFT), color=FAINT, buff=0.3)
        why.next_to(dates, DOWN, buff=0.6, aligned_edge=LEFT)
        with self.say("rec4") as d:
            self.play(FadeIn(why, shift=0.1 * UP), run_time=0.7)
        self.clear()

        # ---------------------------------------------------------- five signals
        h = heading("Five signals that the case is breaking")
        sigs = ["client incentives above 30% of gross revenue while growth slows",
                "US volume growing clearly slower than consumer spending,\nor more issuers moving cards to their own networks",
                "a Senate vote on the CCCA, a court remedy in the debit case,\nor merchants actually surcharging",
                "account-to-account payments winning,\ne.g. Pix above half of Brazilian e-commerce",
                "revenue growth below 8% in constant currency outside a recession"]
        items = VGroup()
        for k, s_ in enumerate(sigs, start=1):
            n = txt(str(k), size=30, color=YELLOW, weight="BOLD")
            t_ = txt(s_, size=23)
            n.align_to(t_, UP)
            items.add(VGroup(n, t_).arrange(RIGHT, buff=0.35, aligned_edge=UP))
        items.arrange(DOWN, buff=0.36, aligned_edge=LEFT).next_to(h, DOWN, buff=0.5, aligned_edge=LEFT).shift(0.2 * RIGHT)
        for it in items[1:]:                  # digits differ in width: line the texts up, not the numbers' right edges
            it[1].align_to(items[0][1], LEFT)
        with self.say("sig0"):
            self.play(FadeIn(h), run_time=0.5)
        for k in range(5):
            with self.say(f"sig{k + 1}"):
                self.play(FadeIn(items[k], shift=0.1 * RIGHT), run_time=0.6)
        self.clear()

        # ---------------------------------------------------------- rerun it yourself, and goodbye
        h = heading("Rerun it with your own assumptions")
        code = VGroup(Text("python analysis/run_all.py --skip-download", font="DejaVu Sans Mono", font_size=24, color=AQUA),
                      Text("python video/build.py render --final", font="DejaVu Sans Mono", font_size=24, color=AQUA))
        code.arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        code = boxed(code, color=FAINT, buff=0.3).next_to(h, DOWN, buff=0.6, aligned_edge=LEFT)
        knobs = txt("assumptions: top of analysis/valuation.py and analysis/scenarios.py", size=21, color=INK2).next_to(code, DOWN, buff=0.35, aligned_edge=LEFT)
        with self.say("end1") as d:
            self.play(FadeIn(h), FadeIn(code, shift=0.1 * UP), run_time=0.8)
            self.at(d * 0.5, FadeIn(knobs), run_time=0.6)
        self.clear()
        name = txt("Visa Inc.  (NYSE: V)", size=56, weight="BOLD")
        sub = txt("Analysis date 17 October 2026", size=26, color=INK2)
        warn = boxed(txt("Not personal financial advice", size=28, color=YELLOW, weight="SEMIBOLD"), color=YELLOW, buff=0.22)
        end = VGroup(name, sub, warn).arrange(DOWN, buff=0.4).move_to(ORIGIN)
        with self.say("end2") as d:
            self.play(FadeIn(name, shift=0.1 * UP), FadeIn(sub), run_time=0.8)
            self.at(d * 0.45, FadeIn(warn, scale=0.95), run_time=0.6)
        self.finish()
