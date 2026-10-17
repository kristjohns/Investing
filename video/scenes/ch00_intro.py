import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from manim import *  # noqa: E402,F403

import data  # noqa: E402
from style import *  # noqa: E402,F403


class Ch00Intro(Chapter):
    KEY = "intro"

    def construct(self):
        price = data.price()
        bb = data.buy_below().set_index(["target_expected_return", "horizon_years"]).loc[(0.10, 10), "buy_below_price"]
        pw = data.scenario_paths()["probability-weighted"]
        idx = data.index_comparison().set_index("horizon_years").loc[10]

        # -- title
        name = txt("Visa Inc.  (NYSE: V)", size=66, weight="BOLD")
        sub = txt("Should you buy it? The investment report, explained", size=32, color=INK2)
        bar = Rectangle(width=1.8, height=0.08, fill_color=BLUE, fill_opacity=1, stroke_width=0)
        head = VGroup(name, bar, sub).arrange(DOWN, buff=0.35, aligned_edge=LEFT).move_to(0.6 * UP).to_edge(LEFT, buff=1.2)
        with self.say("title"):
            self.play(FadeIn(name, shift=0.2 * UP), Create(bar), run_time=0.9)
            self.play(FadeIn(sub, shift=0.1 * UP), run_time=0.7)
        date = txt("Analysis date 17 October 2026  ·  prices: close 16 October 2026", size=24, color=MUTED)
        warn = boxed(txt("Not personal financial advice", size=26, color=YELLOW, weight="SEMIBOLD"), color=YELLOW, buff=0.2)
        VGroup(date, warn).arrange(DOWN, buff=0.35, aligned_edge=LEFT).next_to(head, DOWN, buff=0.7, aligned_edge=LEFT)
        with self.say("date"):
            self.play(FadeIn(date), run_time=0.6)
            self.play(FadeIn(warn, scale=0.95), run_time=0.6)
        self.clear()

        # -- the question
        self.tag_mob = self.chapter_tag()
        self.add(self.tag_mob)
        h = heading("Your question")
        rows = [("Based in Norway, investing in", "NOK"), ("Considering", "NOK 30,000 – 50,000"),
                ("Horizon", "10 – 20 years"), ("Alternative", "a low-cost global index fund")]
        grid = VGroup()
        for a, b in rows:
            grid.add(VGroup(txt(a, size=30, color=INK2), txt(b, size=30, weight="SEMIBOLD")).arrange(RIGHT, buff=0.25))
        grid.arrange(DOWN, buff=0.38, aligned_edge=LEFT).next_to(h, DOWN, buff=0.7, aligned_edge=LEFT)
        with self.say("q1") as d:
            self.play(FadeIn(h), run_time=0.5)
            self.play(LaggedStart(*[FadeIn(r, shift=0.15 * RIGHT) for r in grid], lag_ratio=0.6), run_time=min(d - 0.6, 6))
        q = boxed(mtxt(f"Does Visa at {hl(f'${price:.2f}')} beat the index fund, " + hl("for you", YELLOW) + "?", size=34),
                  color=BLUE, buff=0.32)
        q.next_to(grid, DOWN, buff=0.7).to_edge(LEFT, buff=0.75)
        with self.say("q2"):
            self.play(FadeIn(q, shift=0.15 * UP), run_time=0.8)
        self.clear()

        # -- bottom line
        h = heading("The bottom line")
        verdict = VGroup(txt("HOLD / WAIT", size=88, color=YELLOW, weight="BOLD"), tag("J", 1.6)).arrange(RIGHT, buff=0.3)
        verdict.next_to(h, DOWN, buff=0.45, aligned_edge=LEFT)
        with self.say("bl1"):
            self.play(FadeIn(h), run_time=0.4)
            self.play(FadeIn(verdict, scale=0.9), run_time=0.8)

        # price line: today vs buy-below
        ax = NumberLine(x_range=[300, 420, 20], length=11, color=FAINT, include_ticks=True, tick_size=0.06,
                        stroke_width=2).move_to(0.45 * DOWN)
        ticks = VGroup(*[txt(f"${v}", size=20, color=MUTED).next_to(ax.n2p(v), DOWN, buff=0.18) for v in range(300, 421, 20)])
        p_dot = Dot(ax.n2p(price), radius=0.12, color=ORANGE)
        p_lab = VGroup(txt("Today", size=22, color=INK2), txt(f"${price:.2f}", size=30, color=ORANGE, weight="BOLD")).arrange(DOWN, buff=0.08).next_to(p_dot, UP, buff=0.25)
        b_dot = Dot(ax.n2p(bb), radius=0.12, color=AQUA)
        b_lab = VGroup(txt("Buy at or below", size=22, color=INK2), txt(f"≈ ${round(bb / 5) * 5:.0f}", size=30, color=AQUA, weight="BOLD")).arrange(DOWN, buff=0.08).next_to(b_dot, UP, buff=0.25)
        zone = Rectangle(width=ax.n2p(bb)[0] - ax.n2p(300)[0], height=0.16, fill_color=AQUA, fill_opacity=0.35,
                         stroke_width=0).move_to(ax.n2p(300), aligned_edge=LEFT)
        with self.say("bl2"):
            self.play(Create(ax), FadeIn(ticks), run_time=0.7)
            self.play(FadeIn(p_dot, scale=0.5), FadeIn(p_lab), run_time=0.6)
            self.wait(0.8)
            self.play(FadeIn(zone), FadeIn(b_dot, scale=0.5), FadeIn(b_lab), run_time=0.8)
        price_group = VGroup(ax, ticks, p_dot, p_lab, b_dot, b_lab, zone)

        # expected return vs index
        self.play(FadeOut(price_group), run_time=0.4)
        rx = NumberLine(x_range=[0, 12, 2], length=11, color=FAINT, include_ticks=True, tick_size=0.06,
                        stroke_width=2).move_to(1.2 * DOWN)
        rt = VGroup(*[txt(f"{v}%", size=20, color=MUTED).next_to(rx.n2p(v), DOWN, buff=0.18) for v in range(0, 13, 2)])
        lo, hi = idx["index_expected_return"].min() * 100, idx["index_expected_return"].max() * 100
        band = Rectangle(width=rx.n2p(hi)[0] - rx.n2p(lo)[0], height=0.5, fill_color=YELLOW, fill_opacity=0.35,
                         stroke_color=YELLOW, stroke_width=2).move_to((rx.n2p(lo) + rx.n2p(hi)) / 2 + 0.25 * UP)
        band_lab = txt(f"Global index fund  {lo:.0f}–{hi:.1f}%/yr", size=24, color=YELLOW).next_to(band, UP, buff=0.18)
        v5, v10 = pw[5]["annualised_return_usd"] * 100, pw[10]["annualised_return_usd"] * 100
        vis = Rectangle(width=max(rx.n2p(v5)[0] - rx.n2p(v10)[0], 0.08), height=0.5, fill_color=BLUE, fill_opacity=1,
                        stroke_width=0).move_to((rx.n2p(v5) + rx.n2p(v10)) / 2 + 0.25 * UP)
        vis_lab = VGroup(txt(f"Visa  {v10:.1f}–{v5:.1f}%/yr", size=24, color=BLUE), tag("E")).arrange(RIGHT, buff=0.12)
        vis_lab.next_to(vis, DOWN, buff=1.0)
        lab_line = Line(vis.get_bottom(), vis_lab.get_top() + 0.12 * UP, color=BLUE, stroke_width=2)
        cap = txt("expected return per year, USD", size=20, color=MUTED).next_to(rx.n2p(0), UP, buff=0.3).align_to(rx, LEFT)
        with self.say("bl3") as d:
            self.play(Create(rx), FadeIn(rt), FadeIn(cap), run_time=0.6)
            self.play(FadeIn(band), FadeIn(band_lab), run_time=0.8)
            self.play(FadeIn(vis), Create(lab_line), FadeIn(vis_lab), run_time=0.8)
        self.clear()

        # -- road map
        h = heading("Three parts")
        parts = [("1", "Is it a great business?", "chapters 1 – 4", BLUE),
                 ("2", "What is it worth, and what does the price assume?", "chapters 5 – 10", AQUA),
                 ("3", "What could go wrong, and how does it compare for you?", "chapters 11 – 14", YELLOW)]
        cards = VGroup()
        for n, a, b, c in parts:
            num = txt(n, size=44, color=c, weight="BOLD")
            body = VGroup(txt(a, size=30, weight="SEMIBOLD"), txt(b, size=22, color=MUTED)).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
            row = VGroup(num, body).arrange(RIGHT, buff=0.45)
            cards.add(row)
        cards.arrange(DOWN, buff=0.55, aligned_edge=LEFT).next_to(h, DOWN, buff=0.7, aligned_edge=LEFT).shift(0.3 * RIGHT)
        with self.say("map") as d:
            self.play(FadeIn(h), run_time=0.4)
            self.play(LaggedStart(*[FadeIn(c, shift=0.15 * RIGHT) for c in cards], lag_ratio=0.8), run_time=min(d - 0.5, 5))
        self.clear()

        # -- maths you know
        h = heading("Maths you already know")
        items = [(r"e^{-t\ln(1+r)}", "exponential decay"), (r"\sum_{k=1}^{\infty} a\,q^{k}", "geometric series"),
                 (r"\frac{d}{dt}\ln f", "log-derivatives"), (r"y=\alpha+\beta x", "regression slope"),
                 (r"f(x^{*})=0", "root finding")]
        tiles = VGroup()
        for t, lab in items:
            m = tex(t, size=54, color=INK)
            l = txt(lab, size=22, color=VIOLET)
            tiles.add(VGroup(m, l).arrange(DOWN, buff=0.3))
        tiles.arrange(RIGHT, buff=0.75).next_to(h, DOWN, buff=1.1)
        if tiles.width > 13:
            tiles.scale_to_fit_width(13)
        tiles.set_x(0)
        with self.say("eng") as d:
            self.play(FadeIn(h), run_time=0.4)
            self.play(LaggedStart(*[FadeIn(x, shift=0.2 * UP) for x in tiles], lag_ratio=0.5), run_time=min(d * 0.6, 4))

        # -- tags
        rows = VGroup()
        for k, desc in (("F", "Fact: from Visa's filings and other cited sources"),
                        ("E", "Estimate: from the Python models, with stated assumptions"),
                        ("J", "Judgment: my opinion")):
            rows.add(VGroup(tag(k, 1.3), txt(desc, size=28)).arrange(RIGHT, buff=0.35))
        rows.arrange(DOWN, buff=0.4, aligned_edge=LEFT).to_edge(DOWN, buff=0.8).to_edge(LEFT, buff=1.0)
        with self.say("tags") as d:
            self.play(tiles.animate.set_opacity(0.45), run_time=0.5)
            self.play(LaggedStart(*[FadeIn(r, shift=0.15 * RIGHT) for r in rows], lag_ratio=0.6), run_time=min(d - 0.6, 4))
        self.finish()
