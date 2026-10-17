import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from manim import *  # noqa: E402,F403

import data  # noqa: E402
from style import *  # noqa: E402,F403

US_IN_ACWI = 0.6359     # [MSCI-ACWI] 31 Aug 2026
TAX_FACTOR, TAX_RATE = 1.72, 0.22   # [TAX]: share income x 1.72 taxed at 22%


def year_frac(ts):
    return ts.year + (ts.dayofyear - 1) / 365.25


class Ch13Norway(Chapter):
    KEY = "norway"
    CONCEPTS = ["currency return", "correlation", "ASK", "share income tax", "withholding tax", "position size"]

    def construct(self):
        fx = data.fx_stats()
        spot = float(fx["spot"])
        self.title_card()

        # ---------------------------------------------------------- currency maths
        h = heading("Returns in kroner")
        f1 = tex(r"1 + r_{\text{NOK}} = (1 + r_{\text{USD}})\,(1 + \delta)", size=48).next_to(h, DOWN, buff=0.55).set_x(0)
        dl = txt("δ = change in the dollar's price in kroner", size=22, color=INK2).next_to(f1, DOWN, buff=0.25)
        f2 = tex(r"\ln(1 + r_{\text{NOK}}) = \ln(1 + r_{\text{USD}}) + \ln(1+\delta)", size=42, color=AQUA).next_to(dl, DOWN, buff=0.45)
        with self.say("fx1") as d:
            self.play(FadeIn(h), run_time=0.4)
            self.play(Write(f1), FadeIn(dl), run_time=1.4)
            self.at(d * 0.8, Write(f2), run_time=1.0)
        self.clear()

        # ---------------------------------------------------------- USD/NOK since 2000
        h = heading("US dollar in Norwegian kroner, monthly")
        s = data.usdnok_monthly("2000-01-01")
        xs = [year_frac(t) for t in s.index]
        ax = axes([2000, 2027, 5], [4, 12.5, 2], 10.6, 4.3, y_ticks=[6, 8, 10, 12], y_fmt=lambda y: f"{y:.0f}",
                  x_ticks=[2000, 2005, 2010, 2015, 2020, 2025])
        ax.move_to([0.0, -0.9, 0])
        ln = line_through(ax, xs, list(s.values), color=BLUE, width=3)
        a10 = dashed(ax.c2p(2016.75, fx["avg_10y"]), ax.c2p(2026.8, fx["avg_10y"]), color=AQUA, width=2.5)
        a20 = dashed(ax.c2p(2006.75, fx["avg_20y"]), ax.c2p(2026.8, fx["avg_20y"]), color=VIOLET, width=2.5)
        l10 = txt(f"10-year average {fx['avg_10y']:.2f}", size=18, color=AQUA).next_to(ax.c2p(2016.6, fx["avg_10y"]), LEFT, buff=0.12)
        l20 = txt(f"20-year average {fx['avg_20y']:.2f}", size=18, color=VIOLET).next_to(ax.c2p(2006.9, fx["avg_20y"]), UR, buff=0.06)
        now = VGroup(Dot(ax.c2p(2026.78, spot), radius=0.09, color=YELLOW),
                     txt(f"{spot:.2f}", size=22, color=YELLOW, weight="SEMIBOLD"))
        now[1].next_to(now[0], RIGHT, buff=0.1)
        with self.say("fx2") as d:
            self.play(FadeIn(h), Create(ax), FadeIn(ax.extras), run_time=0.6)
            self.play(Create(ln), run_time=1.6)
            self.play(FadeIn(now), FadeIn(tag("F").next_to(now, UP, buff=0.1)), run_time=0.4)
            self.at(d * 0.45, Create(a10), FadeIn(l10), run_time=0.6)
            self.at(d * 0.72, Create(a20), FadeIn(l20), run_time=0.6)
        dd = data.fx_drawdowns()
        shades = VGroup()
        for _, row in dd.iterrows():
            a, b = year_frac(pd.Timestamp(row["start"])), year_frac(pd.Timestamp(row["end"]))
            r_ = Rectangle(width=max(ax.c2p(b, 4)[0] - ax.c2p(a, 4)[0], 0.12), height=ax.c2p(0, 12.5)[1] - ax.c2p(0, 4)[1],
                           fill_color=ORANGE, fill_opacity=0.25, stroke_width=0)
            r_.move_to([(ax.c2p(a, 4)[0] + ax.c2p(b, 4)[0]) / 2, (ax.c2p(0, 4)[1] + ax.c2p(0, 12.5)[1]) / 2, 0])
            shades.add(r_)
        corr = VGroup(txt(f"shaded: stock-market sell-offs   ·   monthly correlation with the S&P 500: {data.fx_corr()['correlation_spx_vs_usdnok']:.2f}",
                          size=21, color=ORANGE), tag("E")).arrange(RIGHT, buff=0.12)
        corr.next_to(ax, UP, buff=0.15).align_to(ax, LEFT).shift(0.2 * RIGHT)
        with self.say("abs1") as d:
            self.play(FadeIn(shades), run_time=0.8)
            self.at(d * 0.55, FadeIn(corr), run_time=0.6)
        self.clear()

        # ---------------------------------------------------------- the krone as a damper
        h = heading("The krone as a shock absorber")
        dn = data.downturns()
        names = ["2008 – 09", "2020", "2022"]
        ax = axes([0, 3, 1], [-0.6, 0.45, 0.1], 7.6, 4.4, y_ticks=[-0.6, -0.4, -0.2, 0, 0.2, 0.4], y_fmt=lambda y: f"{y:+.0%}" if y else "0%")
        ax.move_to([-2.0, -0.85, 0])
        zero = Line(ax.c2p(0, 0), ax.c2p(3, 0), color=INK2, stroke_width=2)
        groups = VGroup()
        for k, (ep, (_, frow)) in enumerate(zip(dn.index, dd.iterrows())):
            usd = dn.loc[ep, "visa_drawdown"]
            fxc = frow["usdnok_change"]
            nok = (1 + usd) * (1 + fxc) - 1
            bu = bar_at(ax, k + 0.25, 0, usd, 0.5, BLUE)
            bf = bar_at(ax, k + 0.5, 0, fxc, 0.5, YELLOW, 0.8)
            bn = bar_at(ax, k + 0.75, 0, nok, 0.5, AQUA)
            lu = txt(f"{usd:.1%}", size=18, color=BLUE).next_to(bu, DOWN, buff=0.05)
            lf = txt(f"+{fxc:.0%}", size=18, color=YELLOW).next_to(bf, UP, buff=0.05)
            lnk = txt(f"{nok:.0%}", size=18, color=AQUA).next_to(bn, DOWN, buff=0.05)
            nm = txt(names[k], size=19, color=INK2).next_to(ax.c2p(k + 0.5, -0.6), DOWN, buff=0.15)
            groups.add(VGroup(bu, lu, bf, lf, bn, lnk, nm))
        leg = VGroup(*[VGroup(Square(0.22, fill_color=c_, fill_opacity=0.9, stroke_width=0), txt(t_, size=19)).arrange(RIGHT, buff=0.12)
                       for c_, t_ in ((BLUE, "Visa in USD"), (YELLOW, "USD vs NOK"), (AQUA, "Visa in NOK"))])
        leg.arrange(DOWN, buff=0.14, aligned_edge=LEFT).move_to([4.4, 0.9, 0])
        damper = txt("dollar exposure\ndamps the crash", size=22, color=AQUA).next_to(leg, DOWN, buff=0.4, aligned_edge=LEFT)
        with self.say("abs2") as d:
            self.play(FadeIn(h), Create(ax), FadeIn(ax.extras), Create(zero), FadeIn(leg), FadeIn(VGroup(*[g_[6] for g_ in groups])), run_time=0.7)
            for k, g_ in enumerate(groups):
                self.at(d * (0.08 + 0.2 * k), GrowFromEdge(g_[0], UP), FadeIn(g_[1]), GrowFromEdge(g_[2], DOWN), FadeIn(g_[3]), run_time=0.6)
            self.at(d * 0.62, *[AnimationGroup(GrowFromEdge(g_[4], UP), FadeIn(g_[5])) for g_ in groups], run_time=0.8)
            self.play(FadeIn(damper), FadeIn(tag("E").next_to(damper, RIGHT, buff=0.12)), run_time=0.4)
        cost = (fx["avg_20y"] / spot) ** (1 / 10) - 1
        risk = VGroup(txt("long-run risk: the krone recovers", size=21, weight="SEMIBOLD"),
                      tex(rf"\left(\tfrac{{{fx['avg_20y']:.2f}}}{{{spot:.2f}}}\right)^{{1/10}} - 1 \approx {cost * 100:.1f}\%\ \text{{a year}}", size=32, color=ORANGE)
                      ).arrange(DOWN, buff=0.15, aligned_edge=LEFT)
        risk.move_to([2.0, -1.9, 0], aligned_edge=LEFT)
        with self.say("abs3") as d:
            self.play(FadeIn(risk[0]), run_time=0.5)
            self.at(d * 0.35, Write(risk[1]), run_time=1.2)
        self.clear()
        h = heading("Five-year expected return in kroner")
        snk = data.scenarios_nok()
        pw = snk[(snk["scenario"] == "probability-weighted") & (snk["horizon_years"] == 5)].set_index("fx_path")["annualised_return_nok"]
        paths = [("NOK strengthens to 8.50", ORANGE), (f"flat at {spot:.2f}", INK), ("NOK weakens to 10.50", AQUA)]
        cards = VGroup()
        for name, col in paths:
            key = name if name in pw.index else next(i for i in pw.index if i.startswith("flat"))
            cards.add(boxed(VGroup(txt(f"USD/NOK {name.replace('NOK ', '').replace('strengthens to', '→').replace('weakens to', '→')}", size=21, color=INK2),
                                   txt(f"{pw[key]:.1%} a year", size=34, color=col, weight="BOLD")).arrange(DOWN, buff=0.15),
                            color=FAINT, buff=0.28))
        cards.arrange(RIGHT, buff=0.4).next_to(h, DOWN, buff=0.7).set_x(-0.2)
        cl = VGroup(txt("krone strengthens", size=19, color=ORANGE).next_to(cards[0], DOWN, buff=0.15),
                    txt("unchanged", size=19, color=MUTED).next_to(cards[1], DOWN, buff=0.15),
                    txt("krone weakens", size=19, color=AQUA).next_to(cards[2], DOWN, buff=0.15))
        with self.say("abs4") as d:
            self.play(FadeIn(h), FadeIn(cards[1]), FadeIn(cl[1]), run_time=0.6)
            self.at(d * 0.3, FadeIn(cards[0]), FadeIn(cl[0]), run_time=0.6)
            self.at(d * 0.68, FadeIn(cards[2]), FadeIn(cl[2]), FadeIn(tag("E").next_to(cards, RIGHT, buff=0.15)), run_time=0.6)
        us = Rectangle(width=8.0 * US_IN_ACWI, height=0.55, fill_color=BLUE, fill_opacity=0.9, stroke_width=0)
        rest = Rectangle(width=8.0 * (1 - US_IN_ACWI), height=0.55, fill_color=FAINT, fill_opacity=0.9, stroke_width=0)
        acwi = VGroup(us, rest).arrange(RIGHT, buff=0).move_to([0, -2.1, 0])
        al = VGroup(txt(f"US {US_IN_ACWI:.1%}", size=22).move_to(us), txt("rest of world", size=20, color=INK2).move_to(rest))
        at_ = VGroup(txt("Your global index fund (MSCI ACWI) by country, 31 Aug 2026", size=20, color=MUTED), tag("F")).arrange(RIGHT, buff=0.12).next_to(acwi, UP, buff=0.15)
        with self.say("abs5") as d:
            self.play(FadeIn(at_), GrowFromEdge(us, LEFT), FadeIn(rest), FadeIn(al), run_time=0.9)
        self.clear()

        # ---------------------------------------------------------- ASK and tax
        h = heading("Tax: the ASK and share income")
        ask = boxed(VGroup(txt("Aksjesparekonto (ASK)", size=28, weight="SEMIBOLD"),
                           txt("buy and sell without tax on gains until you withdraw them", size=22, color=INK2)).arrange(DOWN, buff=0.12, aligned_edge=LEFT),
                    color=BLUE, buff=0.3)
        ask.next_to(h, DOWN, buff=0.45, aligned_edge=LEFT)
        with self.say("ask1") as d:
            self.play(FadeIn(h), run_time=0.4)
            self.at(d * 0.3, FadeIn(ask, shift=0.1 * UP), run_time=0.7)
        def check(ok, s_):
            mark = txt("✓" if ok else "✗", size=30, color=AQUA if ok else ORANGE, weight="BOLD")
            return VGroup(mark, txt(s_, size=24)).arrange(RIGHT, buff=0.25)
        el = VGroup(check(True, "shares of companies resident in the EEA"), check(True, "equity funds (more than 80% shares)"),
                    check(False, "Visa: a US company"), check(True, "a global index fund")).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        el.next_to(ask, DOWN, buff=0.45, aligned_edge=LEFT).shift(0.3 * RIGHT)
        with self.say("ask2") as d:
            self.play(FadeIn(el[0]), run_time=0.4)
            self.at(d * 0.2, FadeIn(el[1]), run_time=0.4)
            self.at(d * 0.55, FadeIn(el[2]), run_time=0.5)
            self.at(d * 0.78, FadeIn(el[3]), FadeIn(tag("F").next_to(el, RIGHT, buff=0.3).align_to(el, UP)), run_time=0.5)
        self.clear()
        h = heading("Tax on share income in Norway")
        eff = TAX_FACTOR * TAX_RATE
        t1 = tex(rf"{TAX_FACTOR:.2f} \times {TAX_RATE * 100:.0f}\% = {eff * 100:.2f}\%", size=56).move_to([-6.3, 1.95, 0], aligned_edge=LEFT)
        t1l = VGroup(txt("effective rate on gains and dividends, 2025 and 2026", size=21, color=INK2), tag("F")).arrange(RIGHT, buff=0.12).next_to(t1, DOWN, buff=0.2, aligned_edge=LEFT)
        t1n = txt("gains are measured in kroner, so currency moves are taxed too", size=21, color=INK2).next_to(t1l, DOWN, buff=0.15, aligned_edge=LEFT)
        with self.say("tax1") as d:
            self.play(FadeIn(h), Write(t1), run_time=1.2)
            self.play(FadeIn(t1l), run_time=0.4)
            self.at(d * 0.65, FadeIn(t1n), run_time=0.5)
        k = 7.0
        wh = txt("US tax withheld on dividends", size=22, weight="SEMIBOLD").move_to([-6.3, -0.55, 0], aligned_edge=LEFT)
        wrows = VGroup()
        for yy, lab, rate, col in ((-1.15, "with a W-8BEN form", 0.15, AQUA), (-1.75, "without", 0.30, ORANGE)):
            l_ = txt(lab, size=21, color=INK2).move_to([-3.4, yy, 0], aligned_edge=RIGHT)
            b_ = Rectangle(width=rate * k, height=0.4, fill_color=col, fill_opacity=1, stroke_width=0).move_to([-3.2, yy, 0], aligned_edge=LEFT)
            v_ = txt(f"{rate:.0%}", size=22).next_to(b_, RIGHT, buff=0.12)
            wrows.add(VGroup(l_, b_, v_))
        cr = txt("credited against Norwegian tax", size=20, color=AQUA).move_to([-6.3, -2.4, 0], aligned_edge=LEFT)
        with self.say("tax2") as d:
            self.play(FadeIn(wh), FadeIn(wrows[0][0]), GrowFromEdge(wrows[0][1], LEFT), FadeIn(wrows[0][2]), run_time=0.8)
            self.at(d * 0.45, FadeIn(wrows[1][0]), GrowFromEdge(wrows[1][1], LEFT), FadeIn(wrows[1][2]), run_time=0.7)
            self.at(d * 0.72, FadeIn(cr), FadeIn(tag("F").next_to(wh, RIGHT, buff=0.12)), run_time=0.5)
        yr = data.after_tax()
        unc = yr.loc["Visa probability-weighted", "us_withholding_not_credited"]
        sh = boxed(VGroup(txt("shielding deduction (skjermingsfradrag)", size=20, weight="SEMIBOLD"),
                          txt("can absorb Visa's small dividend,", size=18, color=INK2),
                          txt("so the 15% US tax may go uncredited:", size=18, color=INK2),
                          VGroup(txt(f"≈ NOK {round(unc, -2):,.0f} over 10 years on NOK 40,000", size=20, color=YELLOW), tag("E")).arrange(RIGHT, buff=0.12)
                          ).arrange(DOWN, buff=0.08, aligned_edge=LEFT), color=FAINT, buff=0.25)
        sh.move_to([3.5, -1.35, 0])
        with self.say("tax3") as d:
            self.play(FadeIn(sh[0]), FadeIn(sh[1][0]), run_time=0.6)
            self.at(d * 0.3, FadeIn(sh[1][1:3]), run_time=0.5)
            self.at(d * 0.62, FadeIn(sh[1][3]), run_time=0.5)
        self.clear()

        # ---------------------------------------------------------- after-tax comparison
        h = heading("NOK 40,000 for ten years, after tax")
        cases = [("Visa,\nexpected", "Visa probability-weighted", BLUE), ("Visa,\nbase case", "Visa base case", BLUE),
                 ("index fund\nin ASK, 7%", "Global index fund in ASK, 7%/yr", YELLOW), ("index fund\nin ASK, 9.3%", "Global index fund in ASK, 9.3%/yr", YELLOW)]
        ax = axes([0, 4, 1], [0, 90000, 20000], 7.4, 4.0, y_ticks=[0, 20000, 40000, 60000, 80000], y_fmt=lambda y: f"{y / 1000:.0f}k")
        ax.move_to([-2.3, -0.8, 0])
        start = dashed(ax.c2p(0, 40000), ax.c2p(4, 40000), color=MUTED)
        sl = txt("invested: NOK 40k", size=18, color=MUTED).next_to(ax.c2p(4, 40000), RIGHT, buff=0.1)
        bars = VGroup()
        for k, (lab, key, col) in enumerate(cases):
            v_ = yr.loc[key, "after_tax_wealth"]
            b = bar_at(ax, k + 0.5, 0, v_, 1.1, col, 0.9 if k != 1 else 0.55)
            bars.add(VGroup(b, txt(f"{v_ / 1000:.1f}k", size=22, weight="SEMIBOLD").next_to(b, UP, buff=0.06),
                            txt(lab, size=18, color=INK2).next_to(ax.c2p(k + 0.5, 0), DOWN, buff=0.12)))
        with self.say("at1") as d:
            self.play(FadeIn(h), Create(ax), FadeIn(ax.extras), Create(start), FadeIn(sl), run_time=0.6)
            self.play(GrowFromEdge(bars[0][0], DOWN), FadeIn(bars[0][1:]), GrowFromEdge(bars[1][0], DOWN), FadeIn(bars[1][1:]), run_time=0.9)
            self.at(d * 0.6, GrowFromEdge(bars[2][0], DOWN), FadeIn(bars[2][1:]), GrowFromEdge(bars[3][0], DOWN), FadeIn(bars[3][1:]), run_time=0.9)
            self.play(FadeIn(tag("E").next_to(bars[0][1], RIGHT, buff=0.08)), run_time=0.3)
        fl = VGroup(txt("tax barely separates them", size=24, weight="SEMIBOLD"),
                    txt("the ASK's edge: you can switch", size=21, color=INK2),
                    txt("or rebalance without triggering tax", size=21, color=INK2)).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
        fl.move_to([1.8, 0.9, 0], aligned_edge=LEFT)
        with self.say("at2") as d:
            self.play(FadeIn(fl[0]), run_time=0.5)
            self.at(d * 0.4, FadeIn(fl[1:]), FadeIn(tag("J").next_to(fl[0], RIGHT, buff=0.12)), run_time=0.6)
        self.clear()

        # ---------------------------------------------------------- position size
        h = heading("Position size as a share of your portfolio")
        sz = data.sizing()
        ports = sorted(sz["portfolio_nok"].unique())
        amts = sorted(sz["visa_position_nok"].unique())
        cw, ch = 2.0, 0.62
        x0, y0 = -1.6, 1.0
        cells = VGroup()
        for i, pv in enumerate(ports):
            for j, a_ in enumerate(amts):
                w_ = float(sz[(sz["portfolio_nok"] == pv) & (sz["visa_position_nok"] == a_)]["weight"].iloc[0])
                col = AQUA if w_ <= 0.05 else (YELLOW if w_ <= 0.10 else ORANGE)
                r_ = Rectangle(width=cw, height=ch, fill_color=col, fill_opacity=0.35 if w_ <= 0.10 else 0.5, stroke_color=BG, stroke_width=3)
                r_.move_to([x0 + j * cw, y0 - i * ch, 0])
                cells.add(VGroup(r_, txt(f"{w_:.1%}".replace(".0%", "%"), size=22).move_to(r_)))
        rl = VGroup(*[txt(f"NOK {pv / 1e6:g}m" if pv >= 1e6 else f"NOK {pv / 1000:.0f}k", size=21, color=INK2)
                      .move_to([x0 - cw / 2 - 0.25, y0 - i * ch, 0], aligned_edge=RIGHT) for i, pv in enumerate(ports)])
        cl = VGroup(*[txt(f"NOK {a_ / 1000:.0f}k", size=21, color=INK2).move_to([x0 + j * cw, y0 + ch * 0.95, 0]) for j, a_ in enumerate(amts)])
        rt = txt("portfolio", size=19, color=MUTED).next_to(rl, UP, buff=0.3).align_to(rl, RIGHT)
        rule = VGroup(VGroup(Square(0.22, fill_color=AQUA, fill_opacity=0.6, stroke_width=0), txt("≤ 5%: the usual rule of thumb", size=21)).arrange(RIGHT, buff=0.12),
                      VGroup(Square(0.22, fill_color=YELLOW, fill_opacity=0.6, stroke_width=0), txt("≤ 10%: high conviction at most", size=21)).arrange(RIGHT, buff=0.12),
                      VGroup(Square(0.22, fill_color=ORANGE, fill_opacity=0.7, stroke_width=0), txt("a concentrated bet", size=21)).arrange(RIGHT, buff=0.12))
        rule.arrange(DOWN, buff=0.14, aligned_edge=LEFT).next_to(cells, DOWN, buff=0.45).align_to(rl, LEFT)
        with self.say("size") as d:
            self.play(FadeIn(h), FadeIn(rl), FadeIn(cl), FadeIn(rt), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(c_) for c_ in cells], lag_ratio=0.05), run_time=1.2)
            self.at(d * 0.4, FadeIn(rule), FadeIn(tag("J").next_to(rule, RIGHT, buff=0.15)), run_time=0.7)
        self.finish()
