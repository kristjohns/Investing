import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from manim import *  # noqa: E402,F403

import data  # noqa: E402
from style import *  # noqa: E402,F403


class Ch08Reverse(Chapter):
    KEY = "reverse"
    CONCEPTS = ["reverse DCF", "implied growth", "bisection"]

    def construct(self):
        v = data._valuation()
        price = data.price()
        r = v.BASE["discount_rate"]
        rev = data.reverse()
        base = rev[(rev["discount_rate"] == r) & (rev["fcf_margin"] == v.BASE["fcf_margin"])].iloc[0]
        hist = data.growth().loc["net_revenue", "cagr_2017_2025"]
        self.title_card()

        # ---------------------------------------------------------- flip the question
        h = heading("Reverse DCF: what is priced in?")
        def flow(a, b, c, color):
            boxes = VGroup(*[boxed(txt(s, size=24), color=col, buff=0.22) for s, col in ((a, FAINT), (b, color), (c, FAINT))])
            boxes.arrange(RIGHT, buff=0.9)
            arrows = VGroup(*[Arrow(boxes[k].get_right(), boxes[k + 1].get_left(), buff=0.1, color=INK2, stroke_width=3) for k in range(2)])
            return VGroup(boxes, arrows)
        fwd = flow("assumed growth", "DCF model", "value", BLUE).move_to([0, 1.4, 0])
        bwd = flow("today's price", "DCF, inverted", "implied growth", AQUA).move_to([0, -0.2, 0])
        with self.say("rev1") as d:
            self.play(FadeIn(h), FadeIn(fwd), run_time=0.8)
            self.at(d * 0.45, FadeIn(bwd, shift=0.1 * DOWN), run_time=0.8)
        eq = tex(r"f(g) = V(g) - P = 0", size=46, color=AQUA).move_to([0, -1.9, 0])
        with self.say("rev2") as d:
            self.at(d * 0.4, Write(eq), run_time=1.2)
        self.clear()

        # ---------------------------------------------------------- bisection on V(g)
        h = heading("Solving V(g) = price by bisection")
        gs = np.linspace(0.04, 0.14, 41)
        vals = [data.value_at_growth(x) for x in gs]
        ax = axes([0.035, 0.145, 0.01], [260, 560, 50], 9.0, 4.6, y_ticks=[300, 400, 500], y_fmt=lambda y: f"${y:.0f}",
                  x_ticks=[0.04, 0.06, 0.08, 0.10, 0.12, 0.14], x_fmt=lambda x: f"{x:.0%}")
        ax.move_to([-1.3, -0.85, 0])
        curve = line_through(ax, list(gs), vals, color=BLUE, width=5)
        pline = dashed(ax.c2p(0.035, price), ax.c2p(0.145, price), color=INK2, width=2.5)
        pl = txt(f"price ${price:.2f}", size=20, color=INK2).next_to(ax.c2p(0.145, price), RIGHT, buff=0.1)   # clear of the moving brackets
        xl = txt("revenue growth FY2027 – 31", size=19, color=MUTED).next_to(ax, DOWN, buff=0.45)
        steps = data.bisection_steps(n=7)
        lo0, hi0 = steps[0][0], steps[0][1]
        def marker(x, color):
            return Line(ax.c2p(x, 260), ax.c2p(x, 560), color=color, stroke_width=4)
        L, R = marker(lo0, ORANGE), marker(hi0, AQUA)
        Ll = txt("too low", size=19, color=ORANGE).next_to(L, UP, buff=0.08)
        Rl = txt("too high", size=19, color=AQUA).next_to(R, UP, buff=0.08)
        with self.say("bis1") as d:
            self.play(FadeIn(h), Create(ax), FadeIn(ax.extras), FadeIn(xl), run_time=0.6)
            self.play(Create(curve), Create(pline), FadeIn(pl), run_time=1.2)
            self.play(Create(L), Create(R), FadeIn(Ll), FadeIn(Rl), run_time=0.7)
        info = VGroup(txt("step 0", size=24, weight="SEMIBOLD"), txt(f"bracket width {(hi0 - lo0) * 100:.1f} points", size=21, color=INK2))
        info.arrange(DOWN, buff=0.1, aligned_edge=LEFT).move_to([4.9, 1.4, 0])
        with self.say("bis2") as d:
            self.play(FadeIn(info), run_time=0.3)
            per = max((d - 0.6) / len(steps), 0.5)
            for k, (lo, hi, mid, val) in enumerate(steps, 1):
                dot = Dot(ax.c2p(mid, val), radius=0.08, color=YELLOW)
                self.play(FadeIn(dot, scale=0.5), run_time=per * 0.35)
                nlo, nhi = (lo, mid) if val > price else (mid, hi)
                new_info = VGroup(txt(f"step {k}", size=24, weight="SEMIBOLD"),
                                  txt(f"bracket width {(nhi - nlo) * 100:.2f} points", size=21, color=INK2))
                new_info.arrange(DOWN, buff=0.1, aligned_edge=LEFT).move_to(info, aligned_edge=LEFT)
                anims = [L.animate.move_to(ax.c2p(nlo, 410)), R.animate.move_to(ax.c2p(nhi, 410)),
                         Ll.animate.next_to(ax.c2p(nlo, 560), UP, buff=0.08).set_opacity(0 if k > 2 else 1),
                         Rl.animate.next_to(ax.c2p(nhi, 560), UP, buff=0.08).set_opacity(0 if k > 2 else 1),
                         Transform(info, new_info), FadeOut(dot)]
                self.play(*anims, run_time=per * 0.6)
        g1 = base["implied_stage1_growth_fy27_31"]
        root = Dot(ax.c2p(g1, price), radius=0.1, color=YELLOW)
        rl = VGroup(txt(f"g* = {g1:.1%} a year", size=30, color=YELLOW, weight="BOLD"), tag("E")).arrange(RIGHT, buff=0.15)
        rl.move_to([1.4, -1.5, 0])          # below the price line, right of the root: the curve is above it there
        r10 = txt(f"FY2027 – 31, then fading to 4%\n= {base['implied_10y_revenue_cagr']:.1%} a year over ten years", size=21, color=INK2)
        r10.next_to(rl, DOWN, buff=0.2)
        with self.say("bis3") as d:
            self.play(FadeOut(VGroup(L, R, Ll, Rl, info)), FadeIn(root, scale=0.5), run_time=0.6)
            self.play(FadeIn(rl), run_time=0.6)
            self.at(d * 0.55, FadeIn(r10), run_time=0.6)
        self.clear()

        # ---------------------------------------------------------- vs history, and vs the discount rate
        h = heading("Implied growth vs Visa's record")
        m = rev[rev["fcf_margin"] == v.BASE["fcf_margin"]].sort_values("discount_rate")
        ax = axes([0.0775, 0.1025, 0.005], [0.06, 0.16, 0.02], 8.6, 4.4, y_ticks=[0.06, 0.08, 0.10, 0.12, 0.14, 0.16],
                  y_fmt=lambda y: f"{y:.0%}", x_ticks=list(m["discount_rate"]), x_fmt=lambda x: f"{x:.1%}")
        ax.move_to([-1.3, -0.85, 0])
        xl = txt("discount rate", size=19, color=MUTED).next_to(ax, DOWN, buff=0.45)
        yl = txt("growth needed, FY2027 – 31", size=19, color=MUTED).next_to(ax, UP, buff=0.1).align_to(ax, LEFT)
        histl = dashed(ax.c2p(0.0775, hist), ax.c2p(0.1025, hist), color=AQUA, width=3)
        histt = txt(f"Visa's record FY2017 – 25: {hist:.1%}", size=21, color=AQUA).next_to(ax.c2p(0.1025, hist), DOWN, buff=0.1, aligned_edge=RIGHT)
        ln = line_through(ax, list(m["discount_rate"]), list(m["implied_stage1_growth_fy27_31"]), color=YELLOW, width=5)
        dots = VGroup(*[Dot(ax.c2p(a, b), radius=0.07, color=YELLOW) for a, b in zip(m["discount_rate"], m["implied_stage1_growth_fy27_31"])])
        b85 = txt(f"{g1:.1%} at {r:.1%}", size=22, color=YELLOW, weight="SEMIBOLD").next_to(ax.c2p(r, g1), DR, buff=0.1)
        no = txt("no credit for a slowdown", size=24, color=ORANGE).move_to([4.6, 1.3, 0])
        r95 = m[m["discount_rate"] == 0.095].iloc[0]
        p95 = txt(f"{r95['implied_stage1_growth_fy27_31']:.1%} at 9.5%", size=24, color=YELLOW, weight="BOLD")
        p95.next_to(ax.c2p(0.095, r95["implied_stage1_growth_fy27_31"]), UL, buff=0.12)
        with self.say("hist1") as d:
            self.play(FadeIn(h), Create(ax), FadeIn(ax.extras), FadeIn(xl), FadeIn(yl), run_time=0.7)
            self.play(FadeIn(dots[1]), FadeIn(b85), run_time=0.5)
            self.at(d * 0.25, Create(histl), FadeIn(histt), FadeIn(tag("F").next_to(histt, RIGHT, buff=0.1)), run_time=0.8)
            self.at(d * 0.72, FadeIn(no), run_time=0.5)
        with self.say("hist2") as d:
            self.play(Create(ln), FadeIn(dots), run_time=1.2)
            self.at(d * 0.5, FadeIn(p95), Indicate(dots[3], color=YELLOW), run_time=0.8)
        self.finish()
