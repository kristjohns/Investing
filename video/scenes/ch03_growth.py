import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from manim import *  # noqa: E402,F403

import data  # noqa: E402
from style import *  # noqa: E402,F403


class Ch03Growth(Chapter):
    KEY = "growth"
    CONCEPTS = ["CAGR", "log-linear growth", "doubling time", "EPS", "growth decomposition"]

    def construct(self):
        f = data.fin()
        g = data.growth()
        yrs = list(range(2015, 2026))
        rev = [f.loc[y, "net_revenue"] / 1000 for y in yrs]
        cagr = g.loc["net_revenue", "cagr_2015_2025"]
        self.title_card()

        # ---------------------------------------------------------- revenue bars + CAGR
        h = heading("Net revenue, fiscal 2015 – 2025")
        ax = axes([2014.4, 2025.6, 1], [0, 45, 10], 7.4, 4.6, y_ticks=[0, 10, 20, 30, 40], y_fmt=lambda v: f"${v}bn",
                  x_ticks=[2015, 2020, 2025])
        ax.move_to([-2.15, -0.85, 0])
        bars = VGroup(*[bar_at(ax, y, 0, v, 0.48, BLUE) for y, v in zip(yrs, rev)])
        ends = VGroup(txt(f"{rev[0]:.1f}", size=20).next_to(bars[0], UP, buff=0.06),
                      txt(f"{rev[-1]:.1f}", size=20).next_to(bars[-1], UP, buff=0.06))
        with self.say("rev"):
            self.play(FadeIn(h), Create(ax), FadeIn(ax.extras), run_time=0.6)
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.12), FadeIn(ends), run_time=2.0)
        f1 = tex(r"\text{CAGR} = \left(\frac{V_n}{V_0}\right)^{1/n} - 1", size=42)
        f1b = txt("geometric mean of the yearly\ngrowth factors, minus one", size=20, color=INK2)
        fg = VGroup(f1, f1b).arrange(DOWN, buff=0.25, aligned_edge=LEFT).move_to([4.15, 1.0, 0])
        with self.say("cagr1") as d:
            self.play(Write(f1), run_time=1.4)
            self.at(d * 0.62, FadeIn(f1b), run_time=0.6)
        f2 = tex(rf"\left(\frac{{40.0}}{{13.88}}\right)^{{1/10}} - 1 = {cagr * 100:.1f}\%", size=34, color=AQUA)
        f2.next_to(fg, DOWN, buff=0.55, aligned_edge=LEFT)
        f2t = tag("E").next_to(f2, RIGHT, buff=0.15)
        with self.say("cagr2"):
            self.play(Write(f2), run_time=1.4)
            self.play(FadeIn(f2t), run_time=0.3)

        # ---------------------------------------------------------- log scale
        lax = axes([2014.4, 2025.6, 1], [math.log(10), math.log(50), 0.1], 7.4, 4.6,
                   y_ticks=[math.log(v) for v in (10, 20, 40)], y_fmt=lambda v: f"${math.exp(v):.0f}bn",
                   x_ticks=[2015, 2020, 2025])
        lax.move_to(ax)
        pts = VGroup(*[Dot(lax.c2p(y, math.log(v)), radius=0.07, color=BLUE) for y, v in zip(yrs, rev)])
        fit = lax.plot(lambda t: math.log(rev[0]) + (t - 2015) * math.log(1 + cagr), x_range=[2015, 2025], color=AQUA,
                       stroke_width=4)
        dbl = data.doubling_time(cagr)
        x2 = 2015 + dbl
        br = VGroup(dashed(lax.c2p(2015, math.log(rev[0])), lax.c2p(x2, math.log(rev[0])), color=YELLOW),
                    dashed(lax.c2p(x2, math.log(rev[0])), lax.c2p(x2, math.log(2 * rev[0])), color=YELLOW))
        brl = txt(f"×2 in {dbl:.1f} years", size=20, color=YELLOW).next_to(br[0], DOWN, buff=0.1)
        slope = tex(r"\text{slope} = \ln(1+g)", size=34, color=AQUA).next_to(fg, DOWN, buff=0.4, aligned_edge=LEFT)
        dt = tex(r"t_{\times 2} = \frac{\ln 2}{\ln(1+g)} \approx " + f"{dbl:.1f}" + r"\ \text{yr}", size=34).next_to(slope, DOWN, buff=0.35, aligned_edge=LEFT)
        lab = txt("log scale", size=19, color=MUTED).next_to(lax, UP, buff=0.1).align_to(lax, RIGHT)
        with self.say("log1") as d:
            self.play(FadeOut(VGroup(bars, ends, f2, f2t)),
                      ReplacementTransform(VGroup(ax, ax.extras), VGroup(lax, lax.extras)), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(p, scale=0.5) for p in pts], lag_ratio=0.08), FadeIn(lab), run_time=1.0)
            self.play(Create(fit), FadeIn(slope), run_time=1.0)
            self.at(d * 0.55, Create(br), FadeIn(brl), FadeIn(dt), run_time=1.0)
        c1 = chip(f"FY2017 – 25:  {g.loc['net_revenue', 'cagr_2017_2025']:.1%} a year", color=BLUE, size=20)
        c2 = chip(f"FY2026, first 9 months:  +{data.ttm()['nine_month_revenue_growth']:.1%}", color=AQUA, size=20)
        chips = VGroup(c1, c2).arrange(DOWN, buff=0.25, aligned_edge=LEFT).next_to(dt, DOWN, buff=0.5, aligned_edge=LEFT)
        with self.say("log2") as d:
            self.play(FadeIn(c1, shift=0.1 * UP), run_time=0.6)
            self.at(d * 0.6, FadeIn(c2, shift=0.1 * UP), run_time=0.6)
        self.clear()

        # ---------------------------------------------------------- EPS decomposition
        h = heading("Earnings per share (EPS)")
        e1 = tex(r"\text{EPS} = \frac{\text{net income}}{\text{shares}}", size=44).next_to(h, DOWN, buff=0.5, aligned_edge=LEFT).shift(0.3 * RIGHT)
        with self.say("eps1"):
            self.play(FadeIn(h), run_time=0.4)
            self.play(Write(e1), run_time=1.2)
        e2 = tex(r"\text{EPS} = \frac{R \cdot m}{N}", r"\;\Rightarrow\;", r"\ln \text{EPS} = \ln R + \ln m - \ln N", size=40)
        e2.next_to(e1, DOWN, buff=0.45, aligned_edge=LEFT)
        e3 = tex(r"g_{\text{EPS}} \approx g_R + g_m - g_N", size=46, color=AQUA).next_to(e2, DOWN, buff=0.45, aligned_edge=LEFT)
        e3l = txt("d/dt of the logs: growth rates add", size=20, color=MUTED).next_to(e3, RIGHT, buff=0.4)
        with self.say("eps2") as d:
            self.play(Write(e2[0]), run_time=1.0)
            self.at(d * 0.3, FadeIn(e2[1]), Write(e2[2]), run_time=1.4)
            self.at(d * 0.68, Write(e3), FadeIn(e3l), run_time=1.2)
        dec = data.eps_decomposition()
        parts = [("revenue", dec["revenue"], BLUE), ("margin", dec["margin"], VIOLET), ("buybacks", dec["buybacks"], AQUA)]
        scale = 5.2 / dec["total_log"]
        bars, labels = VGroup(), VGroup()
        x0 = -5.6
        for name, v, c in parts:
            r = Rectangle(width=v * scale, height=0.62, fill_color=c, fill_opacity=1, stroke_width=0)
            r.move_to([x0 + v * scale / 2, -2.55, 0])
            bars.add(r)
            labels.add(VGroup(txt(f"{v * 100:.1f}", size=24, weight="SEMIBOLD").next_to(r, UP, buff=0.12),
                              VGroup(Square(0.2, fill_color=c, fill_opacity=1, stroke_width=0), txt(name, size=19, color=INK2)).arrange(RIGHT, buff=0.1)))
            x0 += v * scale
        legend_row = VGroup(*[lab[1] for lab in labels]).arrange(RIGHT, buff=0.45).next_to(bars, DOWN, buff=0.2).align_to(bars, LEFT)
        total = tex(rf"= {dec['total_log'] * 100:.1f}\ \text{{log-points}} \;\Rightarrow\; e^{{{dec['total_log']:.3f}}} - 1 = {dec['eps_cagr'] * 100:.1f}\%",
                    size=34).next_to(bars, RIGHT, buff=0.3)
        cap = txt("non-GAAP EPS growth per year, FY2015 – 25, log-points", size=20, color=MUTED).next_to(bars, UP, buff=0.65, aligned_edge=LEFT)
        with self.say("eps3") as d:
            self.play(FadeIn(cap), run_time=0.3)
            for k in range(3):
                self.at(d * (0.3 + 0.18 * k), GrowFromEdge(bars[k], LEFT), FadeIn(labels[k][0]), FadeIn(labels[k][1]), run_time=0.6)
            self.play(Write(total), run_time=1.0)
            self.play(FadeIn(tag("E").next_to(total, RIGHT, buff=0.12)), run_time=0.3)
        self.clear()

        # ---------------------------------------------------------- incentives
        h = heading("Client incentives, % of gross revenue")
        inc = [f.loc[y, "incentives_pct_gross"] for y in yrs]
        ax = axes([2014.5, 2025.5, 1], [0.1, 0.35, 0.05], 10.6, 4.4, y_ticks=[0.1, 0.15, 0.2, 0.25, 0.3, 0.35],
                  y_fmt=lambda v: f"{v:.0%}", x_ticks=[2015, 2017, 2019, 2021, 2023, 2025])
        ax.move_to([0.3, -0.8, 0])
        ln = line_through(ax, yrs, inc, color=ORANGE, width=5)
        dots = VGroup(*[Dot(ax.c2p(y, v), radius=0.06, color=ORANGE) for y, v in zip(yrs, inc)])
        l0 = txt(fmt_pct(inc[0]), size=22, color=ORANGE).next_to(ax.c2p(2015, inc[0]), UP, buff=0.15)
        l1 = txt(fmt_pct(inc[-1]), size=22, color=ORANGE, weight="BOLD").next_to(ax.c2p(2025, inc[-1]), UP, buff=0.15)
        with self.say("inc1") as d:
            self.play(FadeIn(h), Create(ax), FadeIn(ax.extras), run_time=0.6)
            self.play(Create(ln), FadeIn(dots), FadeIn(l0), run_time=2.0)
            self.play(FadeIn(l1), FadeIn(tag("F").next_to(l1, RIGHT, buff=0.1)), run_time=0.4)
        asc = VGroup(dashed(ax.c2p(2019, 0.1), ax.c2p(2019, 0.33), color=MUTED),
                     txt("2019: accounting change\n(ASC 606)", size=18, color=MUTED).next_to(ax.c2p(2019, 0.33), UP, buff=0.05))
        sig = VGroup(dashed(ax.c2p(2014.5, 0.30), ax.c2p(2025.5, 0.30), color=YELLOW),
                     txt("signal to watch: above 30%", size=19, color=YELLOW).next_to(ax.c2p(2014.6, 0.30), UP, buff=0.06, aligned_edge=LEFT))
        gr = VGroup(txt(f"incentives +{g.loc['client_incentives', 'cagr_2015_2025']:.1%}/yr", size=20, color=ORANGE),
                    txt(f"gross revenue +{g.loc['gross_revenue', 'cagr_2015_2025']:.1%}/yr", size=20, color=INK2)).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
        gr.move_to(ax.c2p(2022.6, 0.15))
        with self.say("inc2") as d:
            self.play(Create(asc[0]), FadeIn(asc[1]), FadeIn(gr), run_time=0.8)
            self.at(d * 0.7, Create(sig[0]), FadeIn(sig[1]), run_time=0.8)
        self.clear()

        # ---------------------------------------------------------- downturns
        h = heading("Recessions: the business vs the stock")
        dn = data.downturns()
        eps_ = ["2008-09 financial crisis", "2020 COVID crash", "2022 inflation shock"]
        names = ["2008 – 09\nfinancial crisis", "2020\nCOVID", "2022\ninflation shock"]
        ax = axes([0, 3, 1], [-0.6, 0.3, 0.1], 8.2, 4.2, y_ticks=[-0.6, -0.4, -0.2, 0, 0.2],
                  y_fmt=lambda v: f"{v:+.0%}" if v else "0%")
        ax.move_to([-1.6, -0.75, 0])
        zero = Line(ax.c2p(0, 0), ax.c2p(3, 0), color=INK2, stroke_width=2)
        rb, sb, rl, sl, nl = VGroup(), VGroup(), VGroup(), VGroup(), VGroup()
        for k, e in enumerate(eps_):
            rg_ = dn.loc[e, "visa_revenue_growth_in_downturn_fy"]
            dd = dn.loc[e, "visa_drawdown"]
            b1 = bar_at(ax, k + 0.33, 0, rg_, 0.6, BLUE)
            b2 = bar_at(ax, k + 0.7, 0, dd, 0.6, ORANGE)
            rb.add(b1)
            sb.add(b2)
            rl.add(txt(f"{rg_:+.1%}", size=20, color=BLUE).next_to(b1, UP if rg_ > 0 else DOWN, buff=0.06))
            sl.add(txt(f"{dd:.1%}", size=20, color=ORANGE).next_to(b2, DOWN, buff=0.06))
            nl.add(txt(names[k], size=19, color=INK2).next_to(ax.c2p(k + 0.5, -0.6), DOWN, buff=0.15))
        leg = VGroup(VGroup(Square(0.22, fill_color=BLUE, fill_opacity=1, stroke_width=0), txt("revenue growth\nthat fiscal year", size=20)).arrange(RIGHT, buff=0.15, aligned_edge=UP),
                     VGroup(Square(0.22, fill_color=ORANGE, fill_opacity=1, stroke_width=0), txt("share price,\npeak to trough", size=20)).arrange(RIGHT, buff=0.15, aligned_edge=UP)
                     ).arrange(DOWN, buff=0.3, aligned_edge=LEFT).next_to(ax, RIGHT, buff=0.6).set_y(-0.3)
        with self.say("dn1"):
            self.play(FadeIn(h), Create(ax), FadeIn(ax.extras), Create(zero), FadeIn(nl), run_time=0.8)
        with self.say("dn2") as d:
            self.play(FadeIn(leg[0]), run_time=0.3)
            self.play(GrowFromEdge(rb[0], DOWN), FadeIn(rl[0]), run_time=0.6)
            self.at(d * 0.35, GrowFromEdge(rb[1], UP), FadeIn(rl[1]), run_time=0.6)
            self.play(GrowFromEdge(rb[2], DOWN), FadeIn(rl[2]), run_time=0.6)
        with self.say("dn3") as d:
            self.play(FadeIn(leg[1]), run_time=0.3)
            for k in range(3):
                self.at(d * (0.2 + 0.22 * k), GrowFromEdge(sb[k], UP), FadeIn(sl[k]), run_time=0.6)
            self.play(FadeIn(tag("F").next_to(leg, UP, buff=0.15).align_to(leg, LEFT)), run_time=0.3)
        msg = boxed(tex(r"\text{price} = \text{earnings} \times \underbrace{\text{multiple}}_{\text{depends on interest rates}}", size=32),
                    color=YELLOW, buff=0.2).move_to([3.7, 1.95, 0])
        with self.say("dn4") as d:
            self.at(d * 0.3, FadeIn(msg, shift=0.1 * UP), run_time=0.8)
        self.finish()
