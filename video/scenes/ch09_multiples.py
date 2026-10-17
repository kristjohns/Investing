import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from manim import *  # noqa: E402,F403

import data  # noqa: E402
from style import *  # noqa: E402,F403


class Ch09Multiples(Chapter):
    KEY = "multiples"
    CONCEPTS = ["P/E ratio", "payback time", "trailing vs forward", "FCF yield"]

    def construct(self):
        mu = data.multiples()
        hist = data.history()
        hs = data.history_summary()
        self.title_card()

        # ---------------------------------------------------------- P/E as payback time
        h = heading("Price-to-earnings ratio (P/E)")
        f = tex(r"P/E = \frac{\text{share price}}{\text{earnings per share}}", size=48).next_to(h, DOWN, buff=0.5).set_x(0)
        with self.say("pe1") as d:
            self.play(FadeIn(h), run_time=0.4)
            self.at(d * 0.5, Write(f), run_time=1.3)
        pe = mu["P/E trailing, GAAP"]
        n = int(round(pe))
        w = 0.33
        blocks = VGroup(*[Square(w * 0.86, fill_color=AQUA, fill_opacity=0.85, stroke_width=0) for _ in range(n)])
        blocks.arrange(RIGHT, buff=w * 0.14).move_to([0, -0.6, 0])
        price_bar = Rectangle(width=blocks.width, height=0.22, fill_color=BLUE, fill_opacity=1, stroke_width=0)
        price_bar.next_to(blocks, UP, buff=0.25)
        pl = txt("the share price", size=21, color=BLUE).next_to(price_bar, UP, buff=0.1)
        bl = txt(f"= {n} years of today's earnings (if earnings never grew)", size=22, color=AQUA).next_to(blocks, DOWN, buff=0.25)
        tf = VGroup(txt("trailing: last 12 months' earnings", size=21, color=INK2),
                    txt("forward: analysts' forecast", size=21, color=INK2)).arrange(RIGHT, buff=0.8).next_to(bl, DOWN, buff=0.45)
        with self.say("pe2") as d:
            self.play(GrowFromEdge(price_bar, LEFT), FadeIn(pl), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(b, scale=0.5) for b in blocks], lag_ratio=0.08), run_time=2.0)
            self.play(FadeIn(bl), run_time=0.4)
            self.at(d * 0.62, FadeIn(tf), run_time=0.6)
        self.clear()

        # ---------------------------------------------------------- Visa's multiples
        h = heading("Visa's P/E today, 16 October 2026")
        items = [("trailing, GAAP", mu["P/E trailing, GAAP"], BLUE), ("trailing, non-GAAP", mu["P/E trailing, non-GAAP/adjusted"], BLUE),
                 ("forward, FY2027E", mu["P/E forward FY2027E (consensus)"], BLUE), ("S&P 500, forward", mu["S&P 500 forward P/E (FactSet)"], YELLOW)]
        scale = 0.2
        rows = VGroup()
        for name, val, c in items:
            lab = txt(name, size=24, color=INK2)
            bar = Rectangle(width=val * scale, height=0.5, fill_color=c, fill_opacity=0.9, stroke_width=0)
            num = txt(f"{val:.1f}×", size=24, weight="SEMIBOLD")
            rows.add(VGroup(lab, bar, num))
        for i, row in enumerate(rows):
            yy = 1.3 - 0.85 * i
            row[0].move_to([-2.9, yy, 0], aligned_edge=RIGHT)
            row[1].move_to([-2.7, yy, 0], aligned_edge=LEFT)
            row[2].next_to(row[1], RIGHT, buff=0.15)
        with self.say("vpe1") as d:
            self.play(FadeIn(h), run_time=0.4)
            for k in range(3):
                self.at(d * (0.08 + 0.18 * k), FadeIn(rows[k][0]), GrowFromEdge(rows[k][1], LEFT), FadeIn(rows[k][2]), run_time=0.6)
            self.at(d * 0.68, FadeIn(rows[3][0]), GrowFromEdge(rows[3][1], LEFT), FadeIn(rows[3][2]), run_time=0.6)
            self.play(FadeIn(tag("E").next_to(rows[0][2], RIGHT, buff=0.12)), FadeIn(tag("F").next_to(rows[3][2], RIGHT, buff=0.12)), run_time=0.3)
        self.clear()
        h = heading("P/E on GAAP earnings at each fiscal year-end")
        hx = list(range(2015, 2026))
        hy = [hist.loc[str(y), "pe_gaap"] for y in hx]
        now = hist.loc["now", "pe_gaap"]
        ax = axes([2014.5, 2026.8, 1], [20, 45, 5], 9.6, 4.4, y_ticks=[20, 25, 30, 35, 40, 45], y_fmt=lambda y: f"{y}×",
                  x_ticks=[2015, 2017, 2019, 2021, 2023, 2025, 2026.5], x_fmt=lambda x: "now" if x > 2026 else str(int(x)))
        ax.move_to([-0.6, -0.85, 0])
        ln = line_through(ax, hx, hy, color=BLUE, width=5)
        dots = VGroup(*[Dot(ax.c2p(x, y), radius=0.06, color=BLUE) for x, y in zip(hx, hy)])
        med = hs.loc["pe_gaap", "median_fy2015_2025"]
        ml = dashed(ax.c2p(2014.5, med), ax.c2p(2026.8, med), color=INK2, width=2.5)
        # label where the P/E line runs below the median (FY2022 - 24), so the line never crosses it
        mll = txt(f"median {med:.1f}×", size=20, color=INK2).next_to(ax.c2p(2023.0, med), UP, buff=0.08)
        nd = Dot(ax.c2p(2026.5, now), radius=0.11, color=YELLOW)
        ndl = VGroup(txt(f"{now:.1f}×", size=26, color=YELLOW, weight="BOLD"),
                     txt(f"{ordinal(round(hs.loc['pe_gaap', 'now_percentile_vs_history'] * 100))} percentile", size=19, color=YELLOW)).arrange(DOWN, buff=0.06)
        ndl.next_to(nd, UP, buff=0.15).shift(0.6 * LEFT)
        with self.say("vpe2") as d:
            self.play(FadeIn(h), Create(ax), FadeIn(ax.extras), run_time=0.6)
            self.play(Create(ln), FadeIn(dots), run_time=1.4)
            self.play(Create(ml), FadeIn(mll), run_time=0.6)
            self.at(d * 0.62, FadeIn(nd, scale=0.5), FadeIn(ndl), run_time=0.7)
        self.clear()

        # ---------------------------------------------------------- FCF yield vs the 10-year Treasury
        h = heading("Visa's cash yield vs a risk-free bond")
        fy = [hist.loc[str(y), "fcf_yield"] for y in hx] + [hist.loc["now", "fcf_yield"]]
        ty = [hist.loc[str(y), "us10y"] for y in hx] + [hist.loc["now", "us10y"]]
        xs = hx + [2026.5]
        ax = axes([2014.5, 2026.8, 1], [0, 0.06, 0.01], 9.6, 4.4, y_ticks=[0, 0.02, 0.04, 0.06], y_fmt=lambda y: f"{y:.0%}",
                  x_ticks=[2015, 2017, 2019, 2021, 2023, 2025, 2026.5], x_fmt=lambda x: "now" if x > 2026 else str(int(x)))
        ax.move_to([-0.6, -0.85, 0])
        lf = line_through(ax, xs, fy, color=AQUA, width=5)
        lt = line_through(ax, xs, ty, color=ORANGE, width=5)
        lfl = txt("Visa FCF yield", size=21, color=AQUA).move_to(ax.c2p(2016.6, 0.047))
        ltl = txt("10-year Treasury", size=21, color=ORANGE).move_to(ax.c2p(2016.6, 0.009))
        nf = txt(f"{fy[-1]:.2%}", size=22, color=AQUA, weight="SEMIBOLD").next_to(ax.c2p(2026.5, fy[-1]), DOWN, buff=0.12)
        nt = txt(f"{ty[-1]:.2%}", size=22, color=ORANGE, weight="SEMIBOLD").next_to(ax.c2p(2026.5, ty[-1]), UP, buff=0.12)
        with self.say("fy1") as d:
            self.play(FadeIn(h), Create(ax), FadeIn(ax.extras), run_time=0.6)
            self.play(Create(lf), FadeIn(lfl), run_time=1.2)
            self.at(d * 0.6, Create(lt), FadeIn(ltl), FadeIn(nf), FadeIn(nt), run_time=1.0)
        # spread shading year by year
        fills = VGroup()
        for k in range(len(xs) - 1):
            a, b = xs[k], xs[k + 1]
            poly = Polygon(ax.c2p(a, fy[k]), ax.c2p(b, fy[k + 1]), ax.c2p(b, ty[k + 1]), ax.c2p(a, ty[k]), stroke_width=0,
                           fill_color=AQUA if (fy[k] + fy[k + 1]) > (ty[k] + ty[k + 1]) else ORANGE, fill_opacity=0.25)
            fills.add(poly)
        gap = hist.loc["now", "fcf_yield_minus_10y"]
        gl = VGroup(txt(f"{gap * 100:+.1f} points", size=26, color=ORANGE, weight="BOLD"), tag("E")).arrange(RIGHT, buff=0.12)
        gl.next_to(ax.c2p(2026.5, (fy[-1] + ty[-1]) / 2), RIGHT, buff=0.2)
        with self.say("fy2") as d:
            self.play(FadeIn(fills[:8]), run_time=0.8)
            self.at(d * 0.45, FadeIn(fills[8:]), run_time=0.8)
            self.play(FadeIn(gl), run_time=0.5)
        self.clear()

        # ---------------------------------------------------------- yield + growth
        h = heading("Why accept less than a bond? Growth")
        f = tex(r"r = \frac{\text{FCF}_1}{P} + g", size=58).move_to([-3.2, 1.3, 0])
        fl = txt("Gordon formula, rearranged:\nreturn = cash yield + growth", size=22, color=INK2).next_to(f, DOWN, buff=0.3)
        with self.say("fy3") as d:
            self.play(FadeIn(h), run_time=0.4)
            self.at(d * 0.45, Write(f), run_time=1.2)
            self.play(FadeIn(fl), run_time=0.5)
        r = data.discount_rate()
        y1 = data.forward_fcf_yield()
        g = r - y1
        k = 0.55
        b1 = Rectangle(width=2.0, height=y1 * 100 * k, fill_color=AQUA, fill_opacity=1, stroke_width=0)
        b2 = Rectangle(width=2.0, height=g * 100 * k, fill_color=VIOLET, fill_opacity=1, stroke_width=0)
        b1.move_to([1.6, -3.2 + y1 * 50 * k, 0])
        b2.next_to(b1, UP, buff=0)
        l1 = txt(f"cash yield {y1:.1%}", size=22).next_to(b1, RIGHT, buff=0.2)
        l2 = txt(f"growth needed {g:.1%}", size=22, color=VIOLET, weight="SEMIBOLD").next_to(b2, RIGHT, buff=0.2)
        top = VGroup(txt(f"required return {r:.1%}", size=24, weight="SEMIBOLD"), tag("E")).arrange(RIGHT, buff=0.12).next_to(b2, UP, buff=0.15)
        fv = txt("…forever", size=24, color=VIOLET).next_to(l2, DOWN, buff=0.1, aligned_edge=LEFT)
        with self.say("fy4") as d:
            self.play(GrowFromEdge(b1, DOWN), FadeIn(l1), FadeIn(top), run_time=0.8)
            self.at(d * 0.3, GrowFromEdge(b2, DOWN), FadeIn(l2), run_time=0.8)
            self.play(FadeIn(fv), run_time=0.4)
        self.finish()
