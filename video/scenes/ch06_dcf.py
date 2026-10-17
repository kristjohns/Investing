import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from manim import *  # noqa: E402,F403

import data  # noqa: E402
from style import *  # noqa: E402,F403


class Ch06Dcf(Chapter):
    KEY = "dcf"
    CONCEPTS = ["DCF", "explicit forecast", "terminal value", "Gordon growth", "enterprise value", "net debt"]

    def construct(self):
        v = data._valuation()
        s = data.dcf_summary()
        dy = data.dcf_years()
        r, g, m = v.BASE["discount_rate"], v.BASE["terminal_growth"], v.BASE["fcf_margin"]
        yrs = list(dy.index)
        self.title_card()

        # ---------------------------------------------------------- the formula
        h = heading("Discounted cash flow (DCF)")
        f1 = tex(r"V = \sum_{t=1}^{\infty} \frac{\text{FCF}_t}{(1+r)^t}", size=56).next_to(h, DOWN, buff=0.6).set_x(0)
        with self.say("def1") as d:
            self.play(FadeIn(h), run_time=0.4)
            self.at(d * 0.4, Write(f1), run_time=1.6)
        f2 = tex(r"V = \underbrace{\sum_{t=1}^{10} \frac{\text{FCF}_t}{(1+r)^t}}_{\text{explicit forecast}}",
                 r"+", r"\underbrace{\frac{TV}{(1+r)^{10}}}_{\text{terminal value}}", size=48)
        f2[0].set_color(BLUE)
        f2[2].set_color(VIOLET)
        f2.next_to(h, DOWN, buff=0.6).set_x(0)
        with self.say("def2"):
            self.play(TransformMatchingShapes(f1, f2), run_time=1.4)
        self.clear()

        # ---------------------------------------------------------- inputs: revenue and FCF
        h = heading("Ten-year forecast, USD bn")
        rev0 = v.REV_FY26E / 1000
        ax = axes([2025.4, 2036.6, 1], [0, 110, 20], 11.4, 4.4, y_ticks=[0, 20, 40, 60, 80, 100], y_fmt=lambda y: f"{y}",
                  x_ticks=[2026, 2028, 2030, 2032, 2034, 2036], x_fmt=lambda x: "FY2026E" if x == 2026 else f"FY{x}")
        ax.move_to([0.3, -1.05, 0])
        rb0 = bar_at(ax, 2026, 0, rev0, 0.62, FAINT)
        rl0 = txt(f"{rev0:.1f}", size=18, color=INK2).next_to(rb0, UP, buff=0.06)
        rbars = VGroup(*[bar_at(ax, y, 0, dy.loc[y, "net_revenue"] / 1000, 0.62, BLUE, 0.45) for y in yrs])
        glabs = VGroup(*[txt(f"{dy.loc[y, 'revenue_growth']:.0%}" if dy.loc[y, 'revenue_growth'] * 100 % 1 < 1e-9
                             else f"{dy.loc[y, 'revenue_growth']:.1%}", size=16, color=AQUA).next_to(b, UP, buff=0.06)
                         for y, b in zip(yrs, rbars)])
        leg = VGroup(VGroup(Square(0.2, fill_color=BLUE, fill_opacity=0.6, stroke_width=0), txt("revenue", size=20)).arrange(RIGHT, buff=0.1),
                     txt("10% = growth that year", size=20, color=AQUA)).arrange(RIGHT, buff=0.5)
        leg.next_to(ax, UP, buff=0.3).align_to(ax, LEFT).shift(0.8 * RIGHT)
        with self.say("in1") as d:
            self.play(FadeIn(h), Create(ax), FadeIn(ax.extras), run_time=0.6)
            self.play(GrowFromEdge(rb0, DOWN), FadeIn(rl0), run_time=0.6)
            self.at(d * 0.3, LaggedStart(*[GrowFromEdge(b, DOWN) for b in rbars[:5]], lag_ratio=0.2),
                    FadeIn(glabs[:5]), FadeIn(leg), run_time=1.4)
            self.at(d * 0.68, LaggedStart(*[GrowFromEdge(b, DOWN) for b in rbars[5:]], lag_ratio=0.2), FadeIn(glabs[5:]), run_time=1.4)
        fbars = VGroup(*[bar_at(ax, y, 0, dy.loc[y, "fcf_after_sbc"] / 1000, 0.62, AQUA) for y in yrs])
        fl = VGroup(txt(f"{dy.loc[yrs[0], 'fcf_after_sbc'] / 1000:.1f}", size=18, weight="SEMIBOLD").move_to(fbars[0]),
                    txt(f"{dy.loc[yrs[-1], 'fcf_after_sbc'] / 1000:.1f}", size=18, weight="SEMIBOLD").move_to(fbars[-1]))
        fleg = VGroup(txt(f"free cash flow = {m:.1%} of revenue", size=20, color=AQUA), tag("E")).arrange(RIGHT, buff=0.12)
        fleg.next_to(leg, RIGHT, buff=0.6)
        with self.say("in2") as d:
            self.play(FadeOut(glabs), FadeIn(fleg), run_time=0.4)
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in fbars], lag_ratio=0.1), run_time=1.4)
            self.play(FadeIn(fl), run_time=0.4)
        # ---------------------------------------------------------- discounting
        pvf = tex(r"PV_t = \frac{\text{FCF}_t}{(1+r)^{\,t-1/2}}", size=40).move_to([-3.2, 1.75, 0])
        pvn = txt(f"r = {r:.1%}, mid-year", size=20, color=MUTED).next_to(pvf, RIGHT, buff=0.4)
        with self.say("pv1") as d:
            self.play(FadeOut(VGroup(rbars, rb0, rl0, leg, fleg)), run_time=0.6)
            self.play(Write(pvf), FadeIn(pvn), run_time=1.2)
        pvbars = VGroup(*[bar_at(ax, y, 0, dy.loc[y, "pv_fcf"] / 1000, 0.62, BLUE) for y in yrs])
        ghost = fbars.copy().set_fill(AQUA, 0.18)
        pl = txt(f"{dy.loc[yrs[-1], 'pv_fcf'] / 1000:.1f}", size=18, weight="SEMIBOLD", color=INK).next_to(pvbars[-1], UP, buff=0.06)
        tot = VGroup(txt(f"sum of PVs: ${s['pv_explicit'] / 1000:.1f}bn", size=28, color=BLUE, weight="SEMIBOLD"), tag("E")).arrange(RIGHT, buff=0.12)
        tot.move_to([3.2, 0.7, 0])
        with self.say("pv2") as d:
            self.add(ghost)
            self.play(FadeOut(fl), *[Transform(fb, pb) for fb, pb in zip(fbars, pvbars)], run_time=2.0)
            self.play(FadeIn(pl), run_time=0.4)
            self.at(d * 0.68, FadeIn(tot), run_time=0.6)
        self.clear()

        # ---------------------------------------------------------- terminal value as a geometric series
        h = heading("Terminal value: a geometric series")
        q = (1 + g) / (1 + r)
        n = 14
        tail = VGroup()
        for k in range(n):
            hgt = 2.6 * q ** k
            b = Rectangle(width=0.34, height=hgt, fill_color=VIOLET, fill_opacity=1 - 0.045 * k, stroke_width=0)
            b.move_to([-6.1 + 0.42 * k, -3.2 + hgt / 2, 0])
            tail.add(b)
        tl = txt(f"after 2036: grows {g:.0%} a year forever,\neach year discounted once more", size=21, color=INK2)
        tl.next_to(tail, UP, buff=0.3).align_to(tail, LEFT)
        dots = txt("…", size=40, color=VIOLET).next_to(tail, RIGHT, buff=0.2)
        with self.say("tv1") as d:
            self.play(FadeIn(h), run_time=0.4)
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in tail], lag_ratio=0.15), FadeIn(dots), run_time=2.0)
            self.play(FadeIn(tl), run_time=0.5)
        s1 = tex(r"TV = \sum_{k=1}^{\infty} \text{FCF}_N \left(\frac{1+g}{1+r}\right)^{k}", size=42).move_to([3.7, 1.55, 0])
        s1b = tex(r"\text{ratio } q = \frac{1+g}{1+r}", "=" + f"{q:.4f}", size=32, color=VIOLET).next_to(s1, DOWN, buff=0.3)
        with self.say("tv2") as d:
            self.play(Write(s1), run_time=1.6)
            self.at(d * 0.62, FadeIn(s1b), run_time=0.6)
        s2 = tex(r"TV = \frac{\text{FCF}_N\,(1+g)}{r-g}", r"\quad (r > g)", size=44, color=AQUA).next_to(s1b, DOWN, buff=0.35)
        warn = txt("r ≤ g: the series diverges", size=22, color=ORANGE).next_to(s2, DOWN, buff=0.25)
        with self.say("tv3") as d:
            self.play(Write(s2), run_time=1.4)
            self.at(d * 0.68, FadeIn(warn), run_time=0.5)
        fc = dy.loc[yrs[-1], "fcf_after_sbc"] / 1000
        num = tex(rf"\frac{{{fc:.1f} \times {1 + g:.2f}}}{{{r:.3f} - {g:.2f}}} = \${f"{s['terminal_value'] / 1000:,.0f}".replace(",", "{{,}}")}\text{{bn in 2036}}", size=38)
        pvt = VGroup(txt(f"worth ${s['pv_terminal'] / 1000:.1f}bn today", size=28, color=VIOLET, weight="SEMIBOLD"), tag("E")).arrange(RIGHT, buff=0.12)
        with self.say("tv4") as d:
            self.play(FadeOut(VGroup(s1, s1b, warn)), s2.animate.move_to([3.7, 1.55, 0]), run_time=0.6)
            num.next_to(s2, DOWN, buff=0.5)
            pvt.next_to(num, DOWN, buff=0.35)
            self.play(Write(num), run_time=1.6)
            self.at(d * 0.72, FadeIn(pvt), run_time=0.6)
        self.clear()

        # ---------------------------------------------------------- from enterprise value to a share price
        h = heading("From cash flows to a value per share")
        ev = (s["pv_explicit"] + s["pv_terminal"]) / 1000
        rows_ = [("ten forecast years", f"${s['pv_explicit'] / 1000:.1f}bn", BLUE, "NORMAL"),
                 ("terminal value", f"${s['pv_terminal'] / 1000:.1f}bn", VIOLET, "NORMAL"),
                 ("enterprise value", f"${ev:.1f}bn", INK, "SEMIBOLD"),
                 ("minus net debt", f"−${s['net_debt'] / 1000:.1f}bn", ORANGE, "NORMAL"),
                 ("equity value", f"${s['equity_value'] / 1000:.1f}bn", INK, "SEMIBOLD"),
                 (f"÷ {v.SHARES:,.0f}m shares", f"${s['value_per_share']:.0f}", AQUA, "BOLD")]
        lx, rx_, y_top = -6.0, -0.9, 1.9
        tab = VGroup()
        for i, (name, val, c_, w_) in enumerate(rows_):
            yy = y_top - 0.62 * i
            lab = txt(name, size=26, color=INK2 if w_ == "BOLD" else c_, weight="NORMAL" if w_ == "BOLD" else w_)
            num_ = txt(val, size=34 if w_ == "BOLD" else 26, color=c_, weight=w_)
            lab.move_to([lx, yy, 0], aligned_edge=LEFT)
            num_.move_to([rx_, yy, 0], aligned_edge=RIGHT)
            tab.add(VGroup(lab, num_))
        rule1 = Line([lx, y_top - 0.62 * 1.5, 0], [rx_, y_top - 0.62 * 1.5, 0], color=FAINT)
        rule2 = Line([lx, y_top - 0.62 * 3.5, 0], [rx_, y_top - 0.62 * 3.5, 0], color=FAINT)
        with self.say("sum1") as d:
            self.play(FadeIn(h), FadeIn(tab[0]), FadeIn(tab[1]), run_time=0.6)
            self.play(Create(rule1), FadeIn(tab[2]), run_time=0.6)
            self.at(d * 0.4, FadeIn(tab[3]), Create(rule2), FadeIn(tab[4]), run_time=0.7)
            self.at(d * 0.7, FadeIn(tab[5]), run_time=0.7)
        cmp_ = VGroup(txt(f"vs price ${data.price():.2f}:", size=26, color=INK2),
                      txt(f"{s['upside']:+.0%}", size=40, color=AQUA, weight="BOLD"), tag("E")).arrange(RIGHT, buff=0.2)
        cmp_.move_to([4.2, 1.2, 0])
        fair = txt("≈ fairly priced", size=26, color=INK).next_to(cmp_, DOWN, buff=0.25)
        with self.say("sum2") as d:
            self.play(FadeIn(cmp_), run_time=0.6)
            self.at(d * 0.5, FadeIn(fair), run_time=0.5)
        share = s["terminal_share_of_value"]
        w = 5.4
        b1 = Rectangle(width=w * (1 - share), height=0.7, fill_color=BLUE, fill_opacity=1, stroke_width=0)
        b2 = Rectangle(width=w * share, height=0.7, fill_color=VIOLET, fill_opacity=1, stroke_width=0)
        split = VGroup(b1, b2).arrange(RIGHT, buff=0).move_to([3.6, -1.6, 0])
        t1 = txt(f"{1 - share:.0%}", size=24).move_to(b1)
        t2 = txt(f"{share:.0%}", size=28, weight="BOLD").move_to(b2)
        cap = VGroup(txt("2027 – 36", size=19, color=BLUE).next_to(b1, DOWN, buff=0.1),
                     txt("after 2036", size=19, color=VIOLET).next_to(b2, DOWN, buff=0.1))
        st = txt("share of the value", size=20, color=MUTED).next_to(split, UP, buff=0.15)
        with self.say("sum3") as d:
            self.play(FadeIn(st), GrowFromEdge(b1, LEFT), FadeIn(t1), run_time=0.6)
            self.play(GrowFromEdge(b2, LEFT), FadeIn(t2), FadeIn(cap), run_time=0.7)
            self.at(d * 0.55, Circumscribe(VGroup(b2, t2), color=YELLOW), run_time=1.0)
        self.finish()
