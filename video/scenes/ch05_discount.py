import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from manim import *  # noqa: E402,F403

import data  # noqa: E402
from style import *  # noqa: E402,F403

RF, ERP, BETA = 0.0508, 0.042, 0.75   # same inputs as analysis/valuation.py (checked below)


class Ch05Discount(Chapter):
    KEY = "discount"
    CONCEPTS = ["present value", "discount rate", "risk-free rate", "equity risk premium", "beta", "CAPM"]

    def construct(self):
        v = data._valuation()
        assert (v.RISK_FREE, v.ERP, v.BETA) == (RF, ERP, BETA)
        r = data.discount_rate()
        self.title_card()

        # ---------------------------------------------------------- a dollar today vs later
        h = heading("A dollar today is worth more than a dollar later")
        ax = axes([0, 10, 1], [0, 2.4, 0.5], 7.4, 3.8, y_ticks=[0, 2], y_fmt=lambda y: f"${y:.0f}",
                  x_ticks=[5, 10], x_fmt=lambda x: f"year {x}")
        ax.move_to([-2.5, -0.9, 0])
        grow = ax.plot(lambda t: (1 + r) ** t, x_range=[0, 10], color=AQUA, stroke_width=5)
        d0 = Dot(ax.c2p(0, 1), color=INK, radius=0.09)
        l0 = txt("$1 today", size=22).next_to(d0, DR, buff=0.1)
        l1 = txt(f"${(1 + r) ** 10:.2f} in 10 years at {r:.1%}", size=22, color=AQUA).next_to(ax.c2p(10, (1 + r) ** 10), UP, buff=0.12).shift(1.2 * LEFT)
        with self.say("tvm1") as d:
            self.play(FadeIn(h), Create(ax), FadeIn(ax.extras), run_time=0.6)
            self.play(FadeIn(d0), FadeIn(l0), run_time=0.4)
            self.at(d * 0.45, Create(grow), run_time=1.6)
            self.play(FadeIn(l1), run_time=0.4)
        f1 = tex(r"\text{grows to } (1+r)^t", size=40).move_to([4.6, 1.2, 0])
        f2 = tex(r"PV = \frac{C}{(1+r)^t}", size=48, color=AQUA).next_to(f1, DOWN, buff=0.4)
        with self.say("tvm2") as d:
            self.play(FadeIn(f1), run_time=0.6)
            self.at(d * 0.5, Write(f2), run_time=1.2)
        lab = VGroup(txt("present value", size=20, color=AQUA), txt("r = discount rate", size=20, color=INK2)).arrange(DOWN, buff=0.08)
        lab.next_to(f2, DOWN, buff=0.2)
        with self.say("tvm3"):
            self.play(FadeIn(lab), run_time=0.6)
        self.clear()

        # ---------------------------------------------------------- discount curves
        h = heading("Discounting is exponential decay")
        ax = axes([0, 30, 5], [0, 1, 0.25], 8.6, 4.4, y_ticks=[0, 0.25, 0.5, 0.75, 1], y_fmt=lambda y: f"{y:.2f}",
                  x_ticks=[0, 10, 20, 30], x_fmt=lambda x: f"{x} yr")
        ax.move_to([-1.6, -0.75, 0])
        c85 = ax.plot(lambda t: (1 + r) ** -t, x_range=[0, 30], color=BLUE, stroke_width=5)
        c5 = ax.plot(lambda t: 1.05 ** -t, x_range=[0, 30], color=AQUA, stroke_width=4)
        c12 = ax.plot(lambda t: 1.12 ** -t, x_range=[0, 30], color=ORANGE, stroke_width=4)
        def key(c, s_):
            return VGroup(Line(ORIGIN, 0.45 * RIGHT, color=c, stroke_width=5), txt(s_, size=20, color=c)).arrange(RIGHT, buff=0.12)
        l5, l85, l12 = key(AQUA, "r = 5%"), key(BLUE, f"r = {r:.1%}"), key(ORANGE, "r = 12%")
        VGroup(l5, l85, l12).arrange(DOWN, buff=0.12, aligned_edge=LEFT).move_to(ax.c2p(24, 0.8))
        f = tex(r"\frac{1}{(1+r)^t} = e^{-t\ln(1+r)}", size=40).move_to([4.3, 1.6, 0])
        cool = VGroup(txt("Newton's law of cooling:", size=20, color=MUTED),
                      tex(r"\Delta T(t) = \Delta T_0\, e^{-t/\tau}", size=32, color=MUTED)).arrange(DOWN, buff=0.12)
        cool.next_to(f, DOWN, buff=0.45)
        yl = txt("value today of $1 due in t years", size=19, color=MUTED).next_to(ax, UP, buff=0.1).align_to(ax, LEFT)
        with self.say("tvm4") as d:
            self.play(FadeIn(h), Create(ax), FadeIn(ax.extras), FadeIn(yl), run_time=0.6)
            self.play(Create(c85), FadeIn(l85), Write(f), run_time=1.6)
            self.at(d * 0.6, FadeIn(cool), run_time=0.7)
        hl_ = data.half_life(r)
        hv = VGroup(dashed(ax.c2p(0, 0.5), ax.c2p(hl_, 0.5), color=YELLOW), dashed(ax.c2p(hl_, 0.5), ax.c2p(hl_, 0), color=YELLOW))
        hlab = txt(f"half-life\n{hl_:.1f} years", size=20, color=YELLOW).next_to(ax.c2p(0.4, 0.5), DR, buff=0.1)
        hf = tex(r"t_{1/2} = \frac{\ln 2}{\ln(1+r)}", size=36, color=YELLOW).next_to(cool, DOWN, buff=0.45)
        with self.say("half1") as d:
            self.play(Create(hv), FadeIn(hlab), FadeIn(hf), run_time=1.0)
            self.at(d * 0.68, Create(c12), FadeIn(l12), Create(c5), FadeIn(l5), run_time=1.0)
        far = Rectangle(width=ax.c2p(30, 0)[0] - ax.c2p(10, 0)[0], height=ax.c2p(0, 1)[1] - ax.c2p(0, 0)[1],
                        fill_color=VIOLET, fill_opacity=0.12, stroke_width=0).move_to(ax.c2p(20, 0.5))
        farl = txt("most of Visa's value\nlies out here", size=22, color=VIOLET).move_to(ax.c2p(21.5, 0.53))
        with self.say("half2") as d:
            self.at(d * 0.45, FadeIn(far), FadeIn(farl), run_time=0.8)
        self.clear()

        # ---------------------------------------------------------- building the discount rate
        h = heading("Which discount rate? Your opportunity cost")
        k = 0.45  # scene units per percentage point
        base_y = -3.1
        def block(lo, hi, color, x=-4.0, w=2.2, op=1.0):
            b = Rectangle(width=w, height=(hi - lo) * 100 * k, fill_color=color, fill_opacity=op, stroke_width=0)
            b.move_to([x, base_y + (lo + hi) / 2 * 100 * k, 0])
            return b
        rf_b = block(0, RF, BLUE)
        rf_l = VGroup(txt(f"risk-free rate {RF:.2%}", size=24, weight="SEMIBOLD"), txt("US 10-year Treasury, 16 Oct 2026", size=19, color=INK2))
        rf_l.arrange(DOWN, buff=0.06, aligned_edge=LEFT).next_to(rf_b, RIGHT, buff=0.35)
        rf_t = tag("F").next_to(rf_l, RIGHT, buff=0.15).align_to(rf_l, UP)
        oc = txt("the return you could earn elsewhere for the same risk", size=24, color=INK2).next_to(h, DOWN, buff=0.35, aligned_edge=LEFT)
        with self.say("opp1") as d:
            self.play(FadeIn(h), run_time=0.4)
            self.at(d * 0.4, FadeIn(oc), run_time=0.6)
        with self.say("opp2") as d:
            self.play(GrowFromEdge(rf_b, DOWN), run_time=0.8)
            self.play(FadeIn(rf_l), FadeIn(rf_t), run_time=0.5)
        erp_b = block(RF, RF + ERP, AQUA, x=-4.0, op=0.45)
        erp_l = VGroup(txt(f"equity risk premium {ERP:.2%}", size=24, weight="SEMIBOLD"),
                       txt("extra return demanded for holding shares (Damodaran)", size=19, color=INK2))
        erp_l.arrange(DOWN, buff=0.06, aligned_edge=LEFT).next_to(erp_b, RIGHT, buff=0.35)
        erp_t = tag("F").next_to(erp_l, RIGHT, buff=0.15).align_to(erp_l, UP)
        with self.say("opp3") as d:
            self.at(d * 0.25, GrowFromEdge(erp_b, DOWN), run_time=0.8)
            self.play(FadeIn(erp_l), FadeIn(erp_t), run_time=0.5)
        stack = VGroup(rf_b, rf_l, rf_t, erp_b, erp_l, erp_t)

        # ---------------------------------------------------------- beta as a regression slope
        self.play(FadeOut(stack), FadeOut(oc), run_time=0.5)
        sax = axes([-0.1, 0.1, 0.05], [-0.1, 0.1, 0.05], 4.8, 4.8, y_ticks=[-0.1, 0.1], y_fmt=lambda y: f"{y:+.0%}",
                   x_ticks=[-0.1, 0, 0.1], x_fmt=lambda x: f"{x:+.0%}" if x else "0", grid=False)
        sax.move_to([3.3, -0.7, 0])
        xl = txt("market return, monthly", size=19, color=MUTED).next_to(sax, DOWN, buff=0.5)
        yl = txt("Visa return", size=19, color=MUTED).next_to(sax, LEFT, buff=0.8).rotate(PI / 2)
        rng = np.random.default_rng(7)
        x = rng.normal(0, 0.035, 60).clip(-0.09, 0.09)
        e = rng.normal(0, 0.022, 60)
        e -= x * (x @ e) / (x @ x) + e.mean()          # orthogonal noise: OLS slope is exactly BETA
        y = (BETA * x + e).clip(-0.095, 0.095)
        pts = VGroup(*[Dot(sax.c2p(a, b), radius=0.045, color=INK2) for a, b in zip(x, y)])
        sch = txt("schematic data", size=17, color=MUTED).move_to(sax.c2p(0.095, -0.088), aligned_edge=RIGHT)
        fit = sax.plot(lambda t: BETA * t, x_range=[-0.1, 0.1], color=BLUE, stroke_width=5)
        one = DashedLine(sax.c2p(-0.1, -0.1), sax.c2p(0.1, 0.1), color=MUTED, dash_length=0.08)
        onel = txt("β = 1", size=19, color=MUTED).next_to(sax.c2p(0.08, 0.1), LEFT, buff=0.1)
        b_note = VGroup(txt("beta = slope", size=26, color=BLUE, weight="SEMIBOLD"),
                        txt("> 1 amplifies market moves", size=21, color=INK2),
                        txt("< 1 damps them", size=21, color=INK2)).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        b_note.move_to([-3.6, 1.2, 0])
        with self.say("beta1") as d:
            self.play(Create(sax), FadeIn(sax.extras), FadeIn(xl), FadeIn(yl), run_time=0.7)
            self.play(LaggedStart(*[FadeIn(p, scale=0.5) for p in pts], lag_ratio=0.02), FadeIn(sch), run_time=1.2)
        with self.say("beta2") as d:
            self.play(Create(fit), FadeIn(b_note[0]), run_time=1.0)
            self.at(d * 0.55, Create(one), FadeIn(onel), FadeIn(b_note[1:]), run_time=0.8)
        bv = VGroup(txt(f"Visa: β = {BETA:.2f}", size=34, color=BLUE, weight="BOLD"), tag("F")).arrange(RIGHT, buff=0.15)
        bv.next_to(b_note, DOWN, buff=0.45, aligned_edge=LEFT)
        bvs = txt("5-year, monthly returns", size=19, color=MUTED).next_to(bv, DOWN, buff=0.1, aligned_edge=LEFT)
        with self.say("beta3"):
            self.play(FadeIn(bv), FadeIn(bvs), run_time=0.6)
        self.clear()

        # ---------------------------------------------------------- CAPM
        h = heading("CAPM: the capital asset pricing model")
        eq = tex(r"r", r"=", r"r_f", r"+", r"\beta", r"\times", r"\text{ERP}", size=60)
        eq[2].set_color(BLUE)
        eq[4].set_color(INK)
        eq[6].set_color(AQUA)
        eq.next_to(h, DOWN, buff=0.55).set_x(-2.6)
        with self.say("capm1"):
            self.play(FadeIn(h), run_time=0.4)
            self.play(Write(eq), run_time=1.4)
        num = tex(rf"= {RF * 100:.2f}\% + {BETA:.2f} \times {ERP * 100:.2f}\% = {v.CAPM * 100:.2f}\%", size=44)
        num.next_to(eq, DOWN, buff=0.4, aligned_edge=LEFT)
        k = 0.42
        base_y = -3.3
        b1 = Rectangle(width=1.8, height=RF * 100 * k, fill_color=BLUE, fill_opacity=1, stroke_width=0).move_to([3.0, base_y + RF * 50 * k, 0])
        b2 = Rectangle(width=1.8, height=BETA * ERP * 100 * k, fill_color=AQUA, fill_opacity=1, stroke_width=0)
        b2.next_to(b1, UP, buff=0)
        t1 = txt(f"{RF:.2%}", size=22).move_to(b1)
        t2 = txt(f"+ {BETA * ERP:.2%}", size=22).move_to(b2)
        tot = VGroup(txt(f"{v.CAPM:.2%}", size=30, weight="BOLD"), tag("E")).arrange(RIGHT, buff=0.12).next_to(b2, UP, buff=0.15)
        with self.say("capm2") as d:
            self.play(Write(num), run_time=1.6)
            self.play(GrowFromEdge(b1, DOWN), FadeIn(t1), run_time=0.6)
            self.play(GrowFromEdge(b2, DOWN), FadeIn(t2), run_time=0.6)
            self.play(FadeIn(tot), run_time=0.4)
        up = Rectangle(width=1.8, height=(r - v.CAPM) * 100 * k, fill_color=YELLOW, fill_opacity=1, stroke_width=0).next_to(b2, UP, buff=0)
        final = VGroup(txt(f"→ {r:.1%}", size=40, color=YELLOW, weight="BOLD"), tag("J")).arrange(RIGHT, buff=0.15)
        final.next_to(up, RIGHT, buff=0.3).shift(0.2 * UP)
        why = VGroup(txt("rounded up for single-company", size=22, color=INK2),
                     txt("and regulatory risk", size=22, color=INK2)).arrange(DOWN, buff=0.06, aligned_edge=LEFT)
        why.next_to(num, DOWN, buff=0.5, aligned_edge=LEFT)
        err = VGroup(txt("CAPM: a first-order model, wide error bars", size=24, color=YELLOW)).next_to(why, DOWN, buff=0.4, aligned_edge=LEFT)
        with self.say("capm3") as d:
            self.play(tot.animate.scale(0.8).next_to(b2.get_corner(UL), LEFT, buff=0.2), run_time=0.5)
            self.play(GrowFromEdge(up, DOWN), FadeIn(final), FadeIn(why), run_time=0.8)
            self.at(d * 0.45, FadeIn(err), run_time=0.6)
        self.finish()
