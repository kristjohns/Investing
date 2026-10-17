import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from manim import *  # noqa: E402,F403

import data  # noqa: E402
from style import *  # noqa: E402,F403


def heat(value, price):
    rel = value / price - 1
    return (BLUE if rel >= 0 else ORANGE), min(0.18 + abs(rel) * 1.6, 0.95)


class Ch07Sensitivity(Chapter):
    KEY = "sensitivity"
    CONCEPTS = ["sensitivity", "pole at r = g", "log-derivative", "duration"]

    def construct(self):
        v = data._valuation()
        r, g = v.BASE["discount_rate"], v.BASE["terminal_growth"]
        price = data.price()
        grid = data.dcf_grid()
        self.title_card()

        # ---------------------------------------------------------- the pole
        h = heading("Value of a growing perpetuity")
        ax = axes([0.03, 0.15, 0.01], [0, 60, 10], 8.4, 4.6, y_ticks=[0, 20, 40, 60], y_fmt=lambda y: f"{y}×",
                  x_ticks=[0.04, 0.06, 0.08, 0.10, 0.12, 0.14], x_fmt=lambda x: f"{x:.0%}")
        ax.move_to([-1.7, -0.9, 0])
        curve = ax.plot(lambda x: 1 / (x - g), x_range=[g + 1 / 60, 0.15, 0.0005], color=BLUE, stroke_width=5)
        pole = dashed(ax.c2p(g, 0), ax.c2p(g, 60), color=ORANGE, width=3)
        pl = txt("pole\nr = g", size=20, color=ORANGE).next_to(ax.c2p(g, 55), RIGHT, buff=0.12)
        f = tex(r"\frac{V}{C} = \frac{1}{r-g}", size=50).move_to([4.5, 1.6, 0])
        xl = txt("discount rate r", size=19, color=MUTED).next_to(ax, DOWN, buff=0.45)
        with self.say("pole1") as d:
            self.play(FadeIn(h), Create(ax), FadeIn(ax.extras), FadeIn(xl), Write(f), run_time=1.0)
            self.at(d * 0.35, Create(curve), run_time=1.6)
            self.play(Create(pole), FadeIn(pl), run_time=0.7)
        pt = Dot(ax.c2p(r, 1 / (r - g)), radius=0.1, color=YELLOW)
        ptl = txt(f"r = {r:.1%}:  V/C = {1 / (r - g):.1f}", size=22, color=YELLOW).next_to(pt, UR, buff=0.12)
        br = BraceBetweenPoints(ax.c2p(g, 2), ax.c2p(r, 2), direction=UP, color=INK2)
        brl = txt(f"{(r - g) * 100:.1f} points", size=19, color=INK2).next_to(br, UP, buff=0.06)
        with self.say("pole2") as d:
            self.play(FadeIn(pt, scale=0.5), FadeIn(ptl), run_time=0.6)
            self.at(d * 0.4, GrowFromCenter(br), FadeIn(brl), run_time=0.7)
        slope = -1 / (r - g)
        tang = ax.plot(lambda x: 1 / (r - g) * (1 + slope * (x - r)), x_range=[r - 0.02, r + 0.03], color=YELLOW, stroke_width=3)
        dur = tex(r"\frac{d \ln V}{dr} = -\frac{1}{r-g} \approx " + f"{slope:.0f}", size=40, color=YELLOW).next_to(f, DOWN, buff=0.5)
        dur2 = txt(f"+1 point on r  →  value ≈ −{abs(slope):.0f}%", size=22, color=INK).next_to(dur, DOWN, buff=0.3)
        dname = txt("bond investors: duration", size=20, color=MUTED).next_to(dur2, DOWN, buff=0.2)
        with self.say("dur1") as d:
            self.play(Write(dur), Create(tang), run_time=1.4)
            self.at(d * 0.45, FadeIn(dur2), run_time=0.6)
            self.at(d * 0.82, FadeIn(dname), run_time=0.5)
        self.clear()

        # ---------------------------------------------------------- full model vs discount rate
        h = heading("Full DCF: value per share vs discount rate")
        col = grid.loc[v.BASE["stage1_growth"]]
        rs = list(col.index)
        ax = axes([0.074, 0.101, 0.005], [250, 600, 50], 8.6, 4.4, y_ticks=[300, 400, 500, 600], y_fmt=lambda y: f"${y:.0f}",
                  x_ticks=rs, x_fmt=lambda x: f"{x:.1%}")
        ax.move_to([-1.4, -0.85, 0])
        ln = line_through(ax, rs, list(col.values), color=BLUE, width=5)
        dots = VGroup(*[Dot(ax.c2p(x, y), radius=0.07, color=BLUE) for x, y in col.items()])
        pr = dashed(ax.c2p(0.074, price), ax.c2p(0.101, price), color=INK2, width=2.5)
        prl = txt(f"price ${price:.2f}", size=20, color=INK2).next_to(ax.c2p(0.101, price), RIGHT, buff=0.1)
        lab = {}
        for x, c_ in ((0.08, AQUA), (0.085, YELLOW), (0.09, ORANGE)):
            # the 9% point sits just under the price line, so its label goes below the curve
            lab[x] = txt(f"${col[x]:.0f}", size=24, color=c_, weight="SEMIBOLD").next_to(ax.c2p(x, col[x]), DL if x == 0.09 else UR, buff=0.08)
        with self.say("dur2") as d:
            self.play(FadeIn(h), Create(ax), FadeIn(ax.extras), Create(pr), FadeIn(prl), run_time=0.8)
            self.play(Create(ln), FadeIn(dots), FadeIn(lab[0.085]), run_time=1.2)
            self.at(d * 0.35, FadeIn(lab[0.09]), Indicate(dots[3], color=ORANGE), run_time=0.7)
            self.at(d * 0.7, FadeIn(lab[0.08]), Indicate(dots[1], color=AQUA), run_time=0.7)
        lo, hi = col[0.09] / price - 1, col[0.08] / price - 1
        ann = VGroup(VGroup(txt("9.0%:", size=24, color=INK2), txt(f"{lo:+.0%}", size=34, color=ORANGE, weight="BOLD")).arrange(RIGHT, buff=0.2),
                     VGroup(txt("8.0%:", size=24, color=INK2), txt(f"{hi:+.0%}", size=34, color=AQUA, weight="BOLD")).arrange(RIGHT, buff=0.2))
        ann.arrange(DOWN, buff=0.3, aligned_edge=LEFT).move_to([4.9, 0.6, 0])
        annt = txt("vs today's price", size=20, color=MUTED).next_to(ann, UP, buff=0.2)
        with self.say("dur3") as d:
            self.play(FadeIn(annt), FadeIn(ann[0]), run_time=0.6)
            self.at(d * 0.55, FadeIn(ann[1]), FadeIn(tag("E").next_to(ann, DOWN, buff=0.2)), run_time=0.6)
        self.clear()

        # ---------------------------------------------------------- growth x discount-rate grid
        h = heading("Value per share: growth × discount rate")
        rows = sorted(grid.index, reverse=True)       # high growth on top
        cols = list(grid.columns)
        cw, ch = 1.25, 0.62
        x0, y0 = -3.0, 1.6
        cells = VGroup()
        cell_at = {}
        for i, gr in enumerate(rows):
            for j, rr in enumerate(cols):
                val = grid.loc[gr, rr]
                c_, op = heat(val, price)
                rect = Rectangle(width=cw, height=ch, fill_color=c_, fill_opacity=op, stroke_color=BG, stroke_width=3)
                rect.move_to([x0 + j * cw, y0 - i * ch, 0])
                t_ = txt(f"{val:.0f}", size=21, color=INK).move_to(rect)
                cells.add(VGroup(rect, t_))
                cell_at[(gr, rr)] = rect
        rl = VGroup(*[txt(f"{gr:.0%}", size=20, color=INK2).next_to(cell_at[(gr, cols[0])], LEFT, buff=0.2) for gr in rows])
        cl = VGroup(*[txt(f"{rr:.1%}", size=20, color=INK2).next_to(cell_at[(rows[-1], rr)], DOWN, buff=0.15) for rr in cols])
        rt = txt("revenue growth\nFY2027 – 31", size=20, color=MUTED).next_to(rl, LEFT, buff=0.25)
        ct = txt("discount rate", size=20, color=MUTED).next_to(cl, DOWN, buff=0.15)
        leg = VGroup(VGroup(Square(0.25, fill_color=BLUE, fill_opacity=0.8, stroke_width=0), txt(f"above ${price:.0f}", size=20)).arrange(RIGHT, buff=0.12),
                     VGroup(Square(0.25, fill_color=ORANGE, fill_opacity=0.8, stroke_width=0), txt("below", size=20)).arrange(RIGHT, buff=0.12))
        leg.arrange(DOWN, buff=0.15, aligned_edge=LEFT).next_to(cells, RIGHT, buff=0.4).align_to(cells, UP)
        with self.say("grid1") as d:
            self.play(FadeIn(h), FadeIn(rl), FadeIn(cl), FadeIn(rt), FadeIn(ct), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(c) for c in cells], lag_ratio=0.02), run_time=1.6)
            self.at(d * 0.55, FadeIn(leg), run_time=0.5)
        # boundary staircase between above- and below-price cells
        pts = []
        for i, gr in enumerate(rows):
            j = next((j for j, rr in enumerate(cols) if grid.loc[gr, rr] < price), len(cols))
            x = x0 + (j - 0.5) * cw
            top, bot = y0 - i * ch + ch / 2, y0 - i * ch - ch / 2
            pts += [[x, top, 0], [x, bot, 0]]
        stair = VMobject(stroke_color=YELLOW, stroke_width=5).set_points_as_corners(pts)
        base = SurroundingRectangle(cell_at[(v.BASE["stage1_growth"], r)], color=INK, buff=0.0, stroke_width=4)
        stairl = VGroup(Line(ORIGIN, 0.25 * RIGHT, color=YELLOW, stroke_width=5), txt("value = price", size=20)).arrange(RIGHT, buff=0.12)
        basel = VGroup(Square(0.25, stroke_color=INK, stroke_width=3, fill_opacity=0), txt("base case", size=20)).arrange(RIGHT, buff=0.12)
        VGroup(stairl, basel).arrange(DOWN, buff=0.15, aligned_edge=LEFT).next_to(leg, DOWN, buff=0.15, aligned_edge=LEFT)
        with self.say("grid2") as d:
            self.play(Create(stair), FadeIn(stairl), run_time=1.4)
            self.at(d * 0.6, Create(base), FadeIn(basel), run_time=0.7)
        self.clear()

        # ---------------------------------------------------------- tornado
        h = heading("Which inputs move the value most?")
        tg, mg = data.dcf_terminal_grid(), data.dcf_margin_grid()
        items = [("discount rate 9.0% → 8.0%", col[0.09], col[0.08]),
                 ("terminal growth 3% → 5%", tg.loc[0.03, r], tg.loc[0.05, r]),
                 ("FCF margin 45% → 57%", mg.loc[0.45, r], mg.loc[0.57, r])]
        base_v = data.dcf_summary()["value_per_share"]
        ax = axes([320, 540, 20], [0, 3, 1], 8.4, 3.4, y_ticks=[], x_ticks=[340, 380, 420, 460, 500, 540],
                  x_fmt=lambda x: f"${x:.0f}", grid=False)
        ax.move_to([1.5, -0.55, 0])
        bars, labs = VGroup(), VGroup()
        for k, (name, a, b) in enumerate(items):
            yk = 2.5 - k
            lo_ = Rectangle(width=ax.c2p(base_v, 0)[0] - ax.c2p(a, 0)[0], height=0.6, fill_color=ORANGE, fill_opacity=0.85, stroke_width=0)
            lo_.move_to(ax.c2p((a + base_v) / 2, yk))
            hi_ = Rectangle(width=ax.c2p(b, 0)[0] - ax.c2p(base_v, 0)[0], height=0.6, fill_color=BLUE, fill_opacity=0.85, stroke_width=0)
            hi_.move_to(ax.c2p((b + base_v) / 2, yk))
            bars.add(VGroup(lo_, hi_, txt(f"${a:.0f}", size=19).next_to(lo_, LEFT, buff=0.08),
                            txt(f"${b:.0f}", size=19).next_to(hi_, RIGHT, buff=0.08)))
            labs.add(txt(name, size=21, color=INK2).next_to(ax.c2p(320, yk), LEFT, buff=0.25))
        bl = Line(ax.c2p(base_v, 0), ax.c2p(base_v, 3), color=INK, stroke_width=2)
        bll = txt(f"base ${base_v:.0f}", size=19).next_to(ax.c2p(base_v, 3), UP, buff=0.08)
        pl_ = dashed(ax.c2p(price, 0), ax.c2p(price, 3), color=YELLOW, width=2.5)
        pll = txt(f"price ${price:.0f}", size=19, color=YELLOW).next_to(ax.c2p(price, 0), DOWN, buff=0.45)
        with self.say("grid3") as d:
            self.play(FadeIn(h), Create(ax), FadeIn(ax.extras), Create(bl), FadeIn(bll), Create(pl_), FadeIn(pll), run_time=0.8)
            self.play(FadeIn(labs[0]), GrowFromCenter(bars[0]), run_time=0.6)
            self.at(d * 0.2, FadeIn(labs[1]), GrowFromCenter(bars[1]), run_time=0.7)
            self.at(d * 0.6, FadeIn(labs[2]), GrowFromCenter(bars[2]), run_time=0.7)
            self.play(FadeIn(tag("E").next_to(bll, RIGHT, buff=0.1)), run_time=0.3)
        verdict = VGroup(txt("about fair value  ·  wide error bars  ·  no margin of safety", size=28, color=YELLOW, weight="SEMIBOLD"),
                         tag("J")).arrange(RIGHT, buff=0.2).to_edge(DOWN, buff=0.35)
        with self.say("grid4"):
            self.play(FadeIn(verdict, shift=0.1 * UP), run_time=0.7)
        self.finish()
