import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from manim import *  # noqa: E402,F403

import data  # noqa: E402
from style import *  # noqa: E402,F403

BESSEMBINDER = (1092, 26000, 0.043)  # [BESSEMBINDER]: 1,092 of ~26,000 US stocks (4.3% as published), 1926-2016
SPIVA_20Y = 0.9289                  # [SPIVA]: US large-cap active funds lagging the S&P 500, 20 years to end-2025
ACWI_WEIGHT = 0.0057                # [MSCI]: Visa ~0.57% of MSCI ACWI (30 Jun 2026)


class Ch12Diversification(Chapter):
    KEY = "diversification"
    CONCEPTS = ["systematic vs specific risk", "1/N variance", "skewness", "base rates"]

    def construct(self):
        self.title_card()

        # ---------------------------------------------------------- variance decomposition
        h = heading("What happens to risk when you combine stocks")
        with self.say("var1"):
            self.play(FadeIn(h), run_time=0.5)
        f1 = tex(r"\sigma_i^2", r"=", r"\beta_i^2\,\sigma_m^2", r"+", r"\sigma_\varepsilon^2", size=54)
        f1[2].set_color(AQUA)
        f1[4].set_color(ORANGE)
        f1.next_to(h, DOWN, buff=0.6).set_x(-2.5)
        l1 = txt("market risk", size=22, color=AQUA).next_to(f1[2], DOWN, buff=0.25).align_to(f1[2], RIGHT)
        l2 = txt("company-specific", size=22, color=ORANGE).next_to(f1[4], DOWN, buff=0.25).align_to(f1[4], LEFT)
        with self.say("var2") as d:
            self.play(Write(f1), run_time=1.2)
            self.at(d * 0.3, FadeIn(l1), run_time=0.5)
            self.at(d * 0.65, FadeIn(l2), run_time=0.5)
        f2 = tex(r"\sigma_p^2(N)", r"=", r"\beta^2\sigma_m^2", r"+", r"\frac{\sigma_\varepsilon^2}{N}", size=50)
        f2[2].set_color(AQUA)
        f2[4].set_color(ORANGE)
        f2.next_to(f1, DOWN, buff=1.0, aligned_edge=LEFT)
        ax = axes([0, 3, 1], [0, 0.4, 0.1], 4.8, 3.4, y_ticks=[0, 0.2, 0.4], y_fmt=lambda y: f"{y:.0%}",
                  x_ticks=[0, 1, 2, 3], x_fmt=lambda x: f"{10 ** x:,.0f}")
        ax.move_to([4.0, -1.1, 0])
        sm, se = 0.16, 0.30          # schematic: market and specific volatility
        curve = ax.plot(lambda x: math.sqrt(sm ** 2 + se ** 2 / 10 ** x), x_range=[0, 3, 0.01], color=BLUE, stroke_width=5)
        floor = dashed(ax.c2p(0, sm), ax.c2p(3, sm), color=AQUA, width=3)
        fl = txt("market risk stays", size=19, color=AQUA).next_to(ax.c2p(3, sm), UP, buff=0.16).shift(0.9 * LEFT)
        xl = txt("number of stocks N (log scale)", size=18, color=MUTED).next_to(ax, DOWN, buff=0.45)
        yl = txt("portfolio volatility, schematic", size=18, color=MUTED).next_to(ax, UP, buff=0.12)
        avg = txt("like averaging N noisy\nmeasurements", size=21, color=INK2).next_to(f2, DOWN, buff=0.35, aligned_edge=LEFT)
        with self.say("var3") as d:
            self.play(Write(f2), run_time=1.2)
            self.play(Create(ax), FadeIn(ax.extras), FadeIn(xl), FadeIn(yl), run_time=0.6)
            self.play(Create(curve), Create(floor), FadeIn(fl), run_time=1.4)
            self.at(d * 0.7, FadeIn(avg), run_time=0.6)
        one = VGroup(Dot(ax.c2p(0, math.sqrt(sm ** 2 + se ** 2)), radius=0.1, color=ORANGE),
                     txt("one stock", size=20, color=ORANGE))
        one[1].next_to(one[0], RIGHT, buff=0.15)
        idx = VGroup(Dot(ax.c2p(3, math.sqrt(sm ** 2 + se ** 2 / 1000)), radius=0.1, color=AQUA),
                     txt("index: thousands", size=20, color=AQUA))
        idx[1].next_to(idx[0], DOWN, buff=0.15).shift(0.9 * LEFT)
        with self.say("var4") as d:
            self.play(FadeIn(idx), run_time=0.6)
            self.at(d * 0.6, FadeIn(one), run_time=0.6)
        self.clear()

        # ---------------------------------------------------------- what the market pays for
        h = heading("The market pays only for market risk")
        w = 9.0
        b1 = Rectangle(width=w * 0.35, height=0.9, fill_color=AQUA, fill_opacity=0.9, stroke_width=0)
        b2 = Rectangle(width=w * 0.65, height=0.9, fill_color=ORANGE, fill_opacity=0.9, stroke_width=0)
        bar = VGroup(b1, b2).arrange(RIGHT, buff=0).move_to([0, 0.6, 0])
        t1 = txt("market risk: paid", size=24).move_to(b1)
        t2 = txt("company-specific risk: not paid", size=24).move_to(b2)
        cap = txt("a single stock's risk, schematic split", size=19, color=MUTED).next_to(bar, UP, buff=0.15)
        rule = VGroup(txt("hold one stock only if its expected return is clearly higher", size=26, weight="SEMIBOLD"),
                      mtxt("Visa " + hl("≈ 8.5%", BLUE) + " vs index " + hl("7 – 9.3%", YELLOW) + "  →  not clearly higher", size=26)).arrange(DOWN, buff=0.25)
        rule.next_to(bar, DOWN, buff=0.8)
        with self.say("pay") as d:
            self.play(FadeIn(h), FadeIn(cap), GrowFromEdge(b1, LEFT), FadeIn(t1), run_time=0.8)
            self.at(d * 0.22, GrowFromEdge(b2, LEFT), FadeIn(t2), run_time=0.8)
            self.at(d * 0.6, FadeIn(rule[0]), run_time=0.6)
            self.at(d * 0.82, FadeIn(rule[1]), FadeIn(tag("J").next_to(rule[1], RIGHT, buff=0.12)), run_time=0.6)
        self.clear()

        # ---------------------------------------------------------- base rates
        h = heading("Base rates: most stocks don't beat Treasury bills")
        n_win, n_all, share = BESSEMBINDER
        cols, rows = 50, 20
        k_on = round(share * cols * rows)
        dots = VGroup(*[Dot(radius=0.045, color=FAINT) for _ in range(cols * rows)]).arrange_in_grid(rows=rows, cols=cols, buff=0.075)
        dots.move_to([-2.6, -0.8, 0])
        rng = np.random.default_rng(3)
        on = set(rng.choice(cols * rows, size=k_on, replace=False))
        hi = [dots[i] for i in sorted(on)]
        lab = VGroup(txt(f"{share:.1%} of US stocks", size=30, color=YELLOW, weight="BOLD"),
                     txt(f"({n_win:,} of ~{n_all:,}, 1926 – 2016)", size=20, color=INK2),
                     txt("created all the wealth\nabove Treasury bills", size=24, color=INK)).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        lab.move_to([4.2, -0.4, 0])
        with self.say("skew1") as d:
            self.play(FadeIn(h), FadeIn(dots, lag_ratio=0.001), run_time=1.0)
            self.at(d * 0.5, *[dd.animate.set_color(YELLOW).scale(1.4) for dd in hi], FadeIn(lab),
                    FadeIn(tag("F").next_to(lab[0], RIGHT, buff=0.12)), run_time=1.0)
        self.clear()
        h = heading("Single-stock returns are skewed")
        ax = axes([0, 6, 1], [0, 0.8, 0.1], 7.2, 3.8, y_ticks=[], x_ticks=[0, 1, 2, 3, 4, 5, 6], x_fmt=lambda x: f"{x}×", grid=False)
        ax.move_to([-2.0, -0.9, 0])
        mu, sg = 0.0, 0.8              # schematic lognormal wealth multiple
        pdf = lambda x: math.exp(-(math.log(x) - mu) ** 2 / (2 * sg ** 2)) / (x * sg * math.sqrt(2 * math.pi))
        dist = ax.plot(pdf, x_range=[0.02, 6, 0.01], color=BLUE, stroke_width=5)
        area = ax.get_area(dist, x_range=[0.02, 6], color=BLUE, opacity=0.2)
        med, mean = math.exp(mu), math.exp(mu + sg ** 2 / 2)
        ml = VGroup(dashed(ax.c2p(med, 0), ax.c2p(med, 0.78), color=INK2), txt("typical stock (median)", size=19, color=INK2))
        ml[1].next_to(ax.c2p(med, 0.78), RIGHT, buff=0.1)
        al = VGroup(dashed(ax.c2p(mean, 0), ax.c2p(mean, 0.62), color=YELLOW), txt("average, pulled up\nby a few winners", size=19, color=YELLOW))
        al[1].next_to(ax.c2p(mean, 0.62), RIGHT, buff=0.1)
        xl = txt("wealth multiple after many years, schematic", size=18, color=MUTED).next_to(ax, DOWN, buff=0.45)
        with self.say("skew2") as d:
            self.play(FadeIn(h), Create(ax), FadeIn(ax.extras), FadeIn(xl), run_time=0.5)
            self.play(Create(dist), FadeIn(area), run_time=1.2)
            self.at(d * 0.35, Create(al[0]), FadeIn(al[1]), run_time=0.6)
            self.at(d * 0.65, Create(ml[0]), FadeIn(ml[1]), run_time=0.6)
        sp = VGroup()
        sb1 = Rectangle(width=5.0 * SPIVA_20Y, height=0.55, fill_color=ORANGE, fill_opacity=0.9, stroke_width=0)
        sb2 = Rectangle(width=5.0 * (1 - SPIVA_20Y), height=0.55, fill_color=AQUA, fill_opacity=0.9, stroke_width=0)
        sbar = VGroup(sb1, sb2).arrange(RIGHT, buff=0).move_to([3.45, 0.9, 0])
        st = VGroup(txt(f"{SPIVA_20Y:.0%} of US large-cap active funds", size=21, color=ORANGE),
                    txt("trailed the S&P 500 over 20 years", size=21, color=INK2)).arrange(DOWN, buff=0.06, aligned_edge=LEFT)
        st.next_to(sbar, DOWN, buff=0.15).align_to(sbar, LEFT)
        with self.say("skew3") as d:
            self.play(GrowFromEdge(sb1, LEFT), FadeIn(sb2), FadeIn(st), FadeIn(tag("F").next_to(sbar, RIGHT, buff=0.12)), run_time=0.9)
        self.clear()

        # ---------------------------------------------------------- Visa has been a winner, and you own it already
        h = heading("Visa has won, and you already own some")
        r = data.returns_usd_nok()
        visa_tr = r.loc["Visa total return (dividends not reinvested)", "cagr_usd"]
        spx = r.loc["S&P 500 price only (monthly avg, Sep 2015 - Sep 2026)", "cagr_usd"]
        k = 18.0
        rb1 = Rectangle(width=visa_tr * k, height=0.6, fill_color=BLUE, fill_opacity=1, stroke_width=0)
        rb2 = Rectangle(width=spx * k, height=0.6, fill_color=YELLOW, fill_opacity=0.9, stroke_width=0)
        rows_ = VGroup(VGroup(txt("Visa, with dividends", size=22, color=INK2), rb1, txt(f"{visa_tr:.1%}/yr", size=24, weight="SEMIBOLD")),
                       VGroup(txt("S&P 500, price only", size=22, color=INK2), rb2, txt(f"{spx:.1%}/yr", size=24, weight="SEMIBOLD")))
        for row in rows_:
            row[0].move_to([-3.0, 0, 0], aligned_edge=RIGHT)
            row[1].move_to([-2.8, 0, 0], aligned_edge=LEFT)
            row[2].next_to(row[1], RIGHT, buff=0.15)
        rows_[0].shift(1.6 * UP)
        rows_[1].shift(0.8 * UP)
        cap = VGroup(txt("USD, Sep 2015 – Sep 2026", size=19, color=MUTED), tag("E")).arrange(RIGHT, buff=0.12).next_to(rows_, UP, buff=0.2).align_to(rows_[1][1], LEFT)
        with self.say("win1") as d:
            self.play(FadeIn(h), FadeIn(cap), run_time=0.4)
            self.play(FadeIn(rows_[0][0]), GrowFromEdge(rb1, LEFT), FadeIn(rows_[0][2]), run_time=0.8)
            self.at(d * 0.4, FadeIn(rows_[1][0]), GrowFromEdge(rb2, LEFT), FadeIn(rows_[1][2]), run_time=0.8)
        pos, port = 40_000, 500_000
        w_after = pos / port + ACWI_WEIGHT * (port - pos) / port
        k2 = 40.0
        e1 = Rectangle(width=max(ACWI_WEIGHT * k2, 0.06), height=0.6, fill_color=AQUA, fill_opacity=1, stroke_width=0)
        e2 = Rectangle(width=w_after * k2, height=0.6, fill_color=ORANGE, fill_opacity=1, stroke_width=0)
        ex = VGroup(VGroup(txt("Visa in the index fund", size=22, color=INK2), e1, txt(f"{ACWI_WEIGHT:.2%}", size=24, weight="SEMIBOLD")),
                    VGroup(txt("+ NOK 40,000 in Visa\n(NOK 500,000 portfolio)", size=22, color=INK2), e2, txt(f"{w_after:.1%}", size=24, weight="SEMIBOLD")))
        for row, yy in zip(ex, (-1.0, -2.1)):
            row[0].move_to([-3.0, yy, 0], aligned_edge=RIGHT)
            row[1].move_to([-2.8, yy, 0], aligned_edge=LEFT)
            row[2].next_to(row[1], RIGHT, buff=0.15)
        excap = txt("your exposure to Visa", size=19, color=MUTED).next_to(ex[0], UP, buff=0.25).align_to(ex[0][1], LEFT)
        with self.say("win2") as d:
            self.play(FadeIn(excap), FadeIn(ex[0]), run_time=0.7)
            self.at(d * 0.55, FadeIn(ex[1][0]), GrowFromEdge(e2, LEFT), FadeIn(ex[1][2]), run_time=0.9)
        self.finish()
