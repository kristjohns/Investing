import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from manim import *  # noqa: E402,F403

import data  # noqa: E402
from style import *  # noqa: E402,F403


class Ch04Cash(Chapter):
    KEY = "cash"
    CONCEPTS = ["free cash flow", "capex", "stock-based compensation", "dividends", "buybacks"]

    def construct(self):
        f = data.fin()
        t = data.ttm()
        yrs = list(range(2015, 2026))
        self.title_card()

        # ---------------------------------------------------------- definition + control volume
        h = heading("Free cash flow")
        eq = tex(r"\text{FCF} = \text{cash from operations} - \text{capital expenditure}", size=42)
        eq.next_to(h, DOWN, buff=0.5).set_x(0)
        with self.say("fcf1") as d:
            self.play(FadeIn(h), run_time=0.4)
            self.at(d * 0.35, Write(eq), run_time=1.4)
        cv = DashedVMobject(RoundedRectangle(corner_radius=0.2, width=4.4, height=2.6, color=INK2, stroke_width=3),
                            num_dashes=40).move_to([0, -1.3, 0])
        cvl = txt("control volume: Visa", size=22, color=INK2).next_to(cv, UP, buff=0.1)
        cin = Arrow([-5.6, -1.3, 0], cv.get_left() + 0.1 * RIGHT, buff=0, color=BLUE, stroke_width=6)
        cinl = txt("cash from\ncustomers", size=20, color=BLUE).next_to(cin, UP, buff=0.1)
        cost = Arrow(cv.get_bottom() + 0.9 * LEFT + 0.1 * UP, cv.get_bottom() + 0.9 * LEFT + 1.0 * DOWN, buff=0, color=ORANGE, stroke_width=5)
        costl = txt("running costs, tax", size=19, color=ORANGE).next_to(cost, LEFT, buff=0.12)
        capx = Arrow(cv.get_bottom() + 0.9 * RIGHT + 0.1 * UP, cv.get_bottom() + 0.9 * RIGHT + 1.0 * DOWN, buff=0, color=YELLOW, stroke_width=4)
        capxl = txt("capex", size=19, color=YELLOW).next_to(capx, RIGHT, buff=0.12)
        out = Arrow(cv.get_right() + 0.1 * LEFT, [5.6, -1.3, 0], buff=0, color=AQUA, stroke_width=8)
        outl = txt("free cash flow\n→ owners", size=20, color=AQUA).next_to(out, UP, buff=0.1)
        with self.say("fcf2") as d:
            self.play(Create(cv), FadeIn(cvl), run_time=0.8)
            self.play(GrowArrow(cin), FadeIn(cinl), run_time=0.6)
            self.at(d * 0.35, GrowArrow(cost), FadeIn(costl), GrowArrow(capx), FadeIn(capxl), run_time=0.8)
            self.at(d * 0.7, GrowArrow(out), FadeIn(outl), run_time=0.8)
        self.clear()

        # ---------------------------------------------------------- FCF history + margin
        h = heading("Visa's free cash flow")
        fcf = [f.loc[y, "fcf"] / 1000 for y in yrs]
        ax = axes([2014.4, 2025.6, 1], [0, 25, 5], 6.0, 4.2, y_ticks=[0, 5, 10, 15, 20, 25], y_fmt=lambda v: f"${v}bn",
                  x_ticks=[2015, 2020, 2025])
        ax.move_to([-2.65, -0.9, 0])
        bars = VGroup(*[bar_at(ax, y, 0, v, 0.42, AQUA) for y, v in zip(yrs, fcf)])
        ends = VGroup(txt(f"{fcf[0]:.1f}", size=19).next_to(bars[0], UP, buff=0.06),
                      txt(f"{fcf[-1]:.1f}", size=19, weight="SEMIBOLD").next_to(bars[-1], UP, buff=0.06))
        cg = data.growth().loc["fcf", "cagr_2015_2025"]
        cagr = VGroup(txt(f"+{cg:.1%} a year", size=24, color=AQUA), tag("E")).arrange(RIGHT, buff=0.12)
        cagr.next_to(ax, UP, buff=0.15).align_to(ax, LEFT).shift(0.6 * RIGHT)
        with self.say("fcf3") as d:
            self.play(FadeIn(h), Create(ax), FadeIn(ax.extras), run_time=0.6)
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.12), run_time=1.8)
            self.play(FadeIn(ends), run_time=0.3)
            self.at(d * 0.6, FadeIn(cagr), run_time=0.5)
        mx = yrs + [2026]
        mv = [f.loc[y, "fcf_margin"] for y in yrs] + [t["fcf_margin"]]
        ax2 = axes([2014.4, 2026.6, 1], [0.3, 0.7, 0.1], 5.2, 4.2, y_ticks=[0.3, 0.4, 0.5, 0.6, 0.7],
                   y_fmt=lambda v: f"{v:.0%}", x_ticks=[2015, 2020, 2026], x_fmt=lambda v: "TTM" if v == 2026 else str(v))
        ax2.move_to([3.9, -0.9, 0])
        ml = line_through(ax2, mx, mv, color=BLUE, width=4)
        md = VGroup(*[Dot(ax2.c2p(x, v), radius=0.055, color=BLUE) for x, v in zip(mx, mv)])
        mt = txt("FCF margin (FCF / revenue)", size=20, color=INK2).next_to(ax2, UP, buff=0.15)
        hi_ = Rectangle(width=ax2.c2p(2023.4, 0)[0] - ax2.c2p(2020.6, 0)[0], height=0.5, fill_color=BLUE, fill_opacity=0.15,
                        stroke_width=0).move_to(ax2.c2p(2022, 0.6))
        last = VGroup(Dot(ax2.c2p(2026, mv[-1]), radius=0.09, color=ORANGE),
                      txt(fmt_pct(mv[-1]), size=20, color=ORANGE, weight="SEMIBOLD").next_to(ax2.c2p(2026, mv[-1]), DOWN, buff=0.12))
        with self.say("fcf4") as d:
            self.play(Create(ax2), FadeIn(ax2.extras), FadeIn(mt), run_time=0.5)
            self.play(Create(ml), FadeIn(md), run_time=1.5)
            self.play(FadeIn(hi_), run_time=0.4)
            self.play(FadeIn(last), run_time=0.4)
        self.clear()

        # ---------------------------------------------------------- stock-based compensation
        h = heading("Stock-based compensation is a real cost")
        eq = tex(r"\text{FCF after SBC} = \text{FCF} - \text{stock-based compensation}", size=40)
        eq.next_to(h, DOWN, buff=0.5).set_x(0)
        sb = VGroup(txt(f"SBC = {f.loc[2025, 'sbc_pct_rev']:.1%} of revenue, FY2025", size=24, color=INK2), tag("F")).arrange(RIGHT, buff=0.12)
        sb.next_to(eq, DOWN, buff=0.3)
        with self.say("sbc1") as d:
            self.play(FadeIn(h), run_time=0.4)
            self.at(d * 0.5, Write(eq), run_time=1.3)
            self.play(FadeIn(sb), run_time=0.4)
        labels = ["FY2023", "FY2024", "FY2025", "TTM"]
        vals = [f.loc[2023, "fcf_after_sbc_margin"], f.loc[2024, "fcf_after_sbc_margin"], f.loc[2025, "fcf_after_sbc_margin"],
                t["fcf_after_sbc_margin"]]
        mean = round(sum(vals) / 4, 3)
        ax = axes([0, 4, 1], [0, 0.7, 0.1], 7.0, 3.0, y_ticks=[0, 0.2, 0.4, 0.6], y_fmt=lambda v: f"{v:.0%}")
        ax.move_to([-1.6, -2.0, 0])           # leaves room on the right for the margin label
        bars = VGroup(*[bar_at(ax, k + 0.5, 0, v, 1.0, AQUA, 0.8) for k, v in enumerate(vals)])
        bl = VGroup(*[txt(l, size=19, color=INK2).next_to(ax.c2p(k + 0.5, 0), DOWN, buff=0.1) for k, l in enumerate(labels)])
        bv = VGroup(*[txt(fmt_pct(v), size=19).next_to(b, UP, buff=0.06) for b, v in zip(bars, vals)])
        ml = dashed(ax.c2p(0, mean), ax.c2p(4, mean), color=YELLOW, width=3)
        mlab = VGroup(txt(f"normal margin {mean:.1%}", size=22, color=YELLOW, weight="SEMIBOLD"), tag("J")).arrange(RIGHT, buff=0.12)
        mlab.next_to(ax.c2p(4, mean), RIGHT, buff=0.15)
        with self.say("sbc2") as d:
            self.play(Create(ax), FadeIn(ax.extras), FadeIn(bl), run_time=0.5)
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.25), FadeIn(bv), run_time=1.4)
            self.at(d * 0.55, Create(ml), FadeIn(mlab), run_time=0.8)
        self.clear()

        # ---------------------------------------------------------- capital returns
        h = heading("Where the cash went, fiscal 2015 – 2025")
        r = f.loc[2015:2025]
        tot_fcf, bb, dv = r["fcf"].sum() / 1000, r["buybacks"].sum() / 1000, r["dividends_paid"].sum() / 1000
        k = 8.2 / tot_fcf
        y0 = 0.6
        fbar = Rectangle(width=tot_fcf * k, height=0.75, fill_color=AQUA, fill_opacity=0.35, stroke_color=AQUA, stroke_width=2)
        fbar.move_to([-5.6 + tot_fcf * k / 2, y0, 0])
        fl = txt(f"free cash flow ${tot_fcf:.0f}bn", size=22, color=AQUA).next_to(fbar, UP, buff=0.12).align_to(fbar, LEFT)
        bbar = Rectangle(width=bb * k, height=0.75, fill_color=BLUE, fill_opacity=1, stroke_width=0)
        bbar.move_to([-5.6 + bb * k / 2, y0 - 1.05, 0])
        dbar = Rectangle(width=dv * k, height=0.75, fill_color=VIOLET, fill_opacity=1, stroke_width=0)
        dbar.next_to(bbar, RIGHT, buff=0)
        bl = txt(f"buybacks ${bb:.0f}bn", size=22).move_to(bbar)
        dl = txt(f"dividends ${dv:.0f}bn", size=19).next_to(dbar, DOWN, buff=0.12)
        pct = VGroup(txt(f"{(bb + dv) / tot_fcf:.0%} of FCF returned", size=28, color=INK, weight="SEMIBOLD"), tag("E")).arrange(RIGHT, buff=0.12)
        pct.next_to(VGroup(bbar, dbar), DOWN, buff=0.75).align_to(bbar, LEFT)
        with self.say("ret1") as d:
            self.play(FadeIn(h), run_time=0.4)
            self.play(GrowFromEdge(fbar, LEFT), FadeIn(fl), run_time=0.8)
            self.at(d * 0.4, GrowFromEdge(bbar, LEFT), FadeIn(bl), run_time=0.7)
            self.play(GrowFromEdge(dbar, LEFT), FadeIn(dl), run_time=0.5)
            self.play(FadeIn(pct), run_time=0.4)
        returned = VGroup(fbar, fl, bbar, dbar, bl, dl, pct)
        # buyback pie: 10 slices -> 8 slices, your slice grows
        c = [-4.4, -1.55, 0]
        def pie(n, mine_color=BLUE):
            return VGroup(*[AnnularSector(inner_radius=0, outer_radius=1.25, angle=TAU / n, start_angle=PI / 2 + j * TAU / n,
                                          fill_color=mine_color if j == 0 else FAINT, fill_opacity=1 if j == 0 else 0.55,
                                          stroke_color=BG, stroke_width=3).move_arc_center_to(c) for j in range(n)])
        p10, p8 = pie(10), pie(8)
        lab10 = txt("your share: 1 of 10", size=22, color=BLUE).next_to(p10, DOWN, buff=0.25)
        lab8 = txt("after a buyback: 1 of 8", size=22, color=BLUE).next_to(p10, DOWN, buff=0.25)
        div = VGroup(txt("dividend:", size=22, color=VIOLET, weight="SEMIBOLD"), txt("cash paid to you", size=22)).arrange(RIGHT, buff=0.15)
        div.move_to([-1.5, -0.9, 0], aligned_edge=LEFT)
        bbk = VGroup(txt("buyback:", size=22, color=BLUE, weight="SEMIBOLD"), txt("shares bought and cancelled", size=22)).arrange(RIGHT, buff=0.15)
        bbk.next_to(div, DOWN, buff=0.3, aligned_edge=LEFT)
        with self.say("ret2") as d:
            self.play(returned.animate.scale(0.7).next_to(h, DOWN, buff=0.35, aligned_edge=LEFT), run_time=0.6)
            self.play(FadeIn(div), run_time=0.5)
            self.at(d * 0.3, FadeIn(bbk), FadeIn(p10), FadeIn(lab10), run_time=0.7)
            self.at(d * 0.62, Transform(p10, p8), Transform(lab10, lab8), run_time=1.2)
        self.clear()
        h = heading("Fewer shares each year")
        sh = [f.loc[y, "diluted_shares_derived"] for y in yrs]
        ax = axes([2014.4, 2025.6, 1], [1800, 2600, 200], 8.0, 4.0, y_ticks=[1800, 2000, 2200, 2400, 2600],
                  y_fmt=lambda v: f"{v:,.0f}m", x_ticks=[2015, 2020, 2025])
        ax.move_to([-1.6, -0.9, 0])
        sl = line_through(ax, yrs, sh, color=BLUE, width=5)
        s0 = txt(f"{sh[0]:,.0f}m", size=20, color=BLUE).next_to(ax.c2p(2015, sh[0]), UP, buff=0.12)
        s1 = txt(f"{sh[-1]:,.0f}m", size=20, color=BLUE, weight="SEMIBOLD").next_to(ax.c2p(2025, sh[-1]), DOWN, buff=0.15)
        rate = VGroup(txt(f"{data.growth().loc['diluted_shares_derived', 'cagr_2015_2025']:.1%} a year", size=26, color=BLUE), tag("E")).arrange(RIGHT, buff=0.12)
        rate.move_to([4.6, 0.8, 0])
        dy = stat(f"{data.multiples()['Dividend yield (%, $0.67 x 4)']:.2f}%", "dividend yield", VIOLET, vsize=44, lsize=20, kind="F")
        dy.next_to(rate, DOWN, buff=0.8)
        with self.say("ret3") as d:
            self.play(FadeIn(h), Create(ax), FadeIn(ax.extras), run_time=0.6)
            self.play(Create(sl), FadeIn(s0), run_time=1.4)
            self.play(FadeIn(s1), FadeIn(rate), run_time=0.5)
            self.at(d * 0.7, FadeIn(dy), run_time=0.5)
        self.finish()
