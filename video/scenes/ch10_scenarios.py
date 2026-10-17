import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from manim import *  # noqa: E402,F403

import data  # noqa: E402
from style import *  # noqa: E402,F403

SC = {"bear": ORANGE, "base": BLUE, "bull": AQUA}


def ret_color(x):
    if x >= 0.10:
        return AQUA, min(0.3 + (x - 0.10) * 7, 0.95)
    if x >= 0.07:
        return YELLOW, 0.32
    return ORANGE, min(0.25 + (0.07 - x) * 6, 0.9)


class Ch10Scenarios(Chapter):
    KEY = "scenarios"
    CONCEPTS = ["IRR", "net present value", "exit multiple", "scenarios", "expected value", "Jensen's inequality"]

    def construct(self):
        sc = data.scenarios()
        inp = data.scenario_inputs()
        price = data.price()
        paths = data.scenario_paths()
        self.title_card()

        # ---------------------------------------------------------- IRR on a cash-flow timeline
        h = heading("Internal rate of return (IRR)")
        sub = txt("the yearly return your cash flows actually earn", size=24, color=INK2).next_to(h, DOWN, buff=0.3, aligned_edge=LEFT)
        with self.say("irr1") as d:
            self.play(FadeIn(h), run_time=0.5)
            self.at(d * 0.45, FadeIn(sub), run_time=0.6)
        base5 = paths["base"][5]
        x0, dx, y0 = -5.4, 1.75, -0.6
        axis = Arrow([x0 - 0.3, y0, 0], [x0 + 5 * dx + 0.6, y0, 0], buff=0, color=FAINT, stroke_width=3, tip_length=0.2)
        ticks = VGroup(*[VGroup(Line([x0 + k * dx, y0 - 0.08, 0], [x0 + k * dx, y0 + 0.08, 0], color=FAINT),
                                txt(f"year {k}", size=18, color=MUTED).next_to([x0 + k * dx, y0, 0], DOWN, buff=0.2))
                         for k in range(6)])
        pay = Arrow([x0, y0, 0], [x0, y0 - 2.2, 0], buff=0, color=ORANGE, stroke_width=6)
        payl = txt(f"pay ${price:.2f}", size=20, color=ORANGE).next_to(pay, RIGHT, buff=0.15).shift(0.6 * DOWN)
        divs = VGroup(*[Arrow([x0 + k * dx, y0, 0], [x0 + k * dx, y0 + 0.45, 0], buff=0, color=VIOLET, stroke_width=4,
                              max_tip_length_to_length_ratio=0.35) for k in range(1, 6)])
        divl = txt("dividends", size=20, color=VIOLET).next_to(divs[1], UP, buff=0.12)
        sell = Arrow([x0 + 5 * dx, y0 + 0.5, 0], [x0 + 5 * dx, y0 + 3.0, 0], buff=0, color=AQUA, stroke_width=6)
        selll = txt("sell", size=20, color=AQUA).next_to(sell, LEFT, buff=0.15)
        npv = tex(r"0 = -P + \sum_{t=1}^{T} \frac{D_t}{(1+\text{IRR})^t} + \frac{P_T}{(1+\text{IRR})^T}", size=38)
        npv.to_edge(DOWN, buff=0.45).set_x(0.8)
        with self.say("irr2") as d:
            self.play(GrowArrow(axis), FadeIn(ticks), run_time=0.6)
            self.play(GrowArrow(pay), FadeIn(payl), run_time=0.5)
            self.play(LaggedStart(*[GrowArrow(a) for a in divs], lag_ratio=0.2), FadeIn(divl), run_time=0.8)
            self.play(GrowArrow(sell), FadeIn(selll), run_time=0.5)
            self.at(d * 0.45, Write(npv), run_time=1.6)
        self.clear()

        # ---------------------------------------------------------- the model
        h = heading("A simple model for the cash flows")
        m1 = tex(r"\text{EPS}_{2027} = \$" + f"{inp['eps_ntm']:.2f}", r"\;\longrightarrow\;", r"\text{EPS}_T = \text{EPS}_{2027}\,(1+g)^T", size=40)
        m1.next_to(h, DOWN, buff=0.6).set_x(0)
        m1s = txt("analysts' forecast for fiscal 2027", size=19, color=MUTED).next_to(m1[0], DOWN, buff=0.15)
        with self.say("mod1") as d:
            self.play(FadeIn(h), run_time=0.4)
            self.play(Write(m1[0]), FadeIn(m1s), run_time=1.0)
            self.at(d * 0.6, FadeIn(m1[1]), Write(m1[2]), run_time=1.0)
        m2 = tex(r"P_T = \text{EPS}_T \times (P/E)_{\text{exit}}", size=44, color=AQUA)
        m3 = tex(r"D_t = " + f"{inp['payout']:.0%}".replace("%", r"\%") + r" \times \text{EPS}_t", size=40, color=VIOLET)
        VGroup(m2, m3).arrange(DOWN, buff=0.35).next_to(m1, DOWN, buff=0.6)
        levers = VGroup(chip("lever 1: earnings growth g", color=BLUE, size=24), chip("lever 2: exit multiple", color=AQUA, size=24))
        levers.arrange(RIGHT, buff=0.6).to_edge(DOWN, buff=0.6)
        with self.say("mod2") as d:
            self.play(Write(m2), run_time=1.2)
            self.at(d * 0.38, Write(m3), run_time=1.0)
            self.at(d * 0.7, FadeIn(levers, shift=0.1 * UP), run_time=0.7)
        self.clear()

        # ---------------------------------------------------------- three scenarios, five years
        h = heading("Three scenarios, five years ahead")
        ax = axes([0, 5.2, 1], [200, 900, 100], 6.2, 4.4, y_ticks=[200, 400, 600, 800], y_fmt=lambda y: f"${y:.0f}",
                  x_ticks=[0, 1, 2, 3, 4, 5], x_fmt=lambda x: "now" if x == 0 else f"+{x} yr")
        ax.move_to([-2.75, -0.75, 0])
        start = Dot(ax.c2p(0, price), radius=0.08, color=INK)
        sl = txt(f"today ${price:.0f}", size=19).next_to(start, DR, buff=0.08)
        lines, ends, cards = {}, {}, {}
        for name, col in SC.items():
            ex = paths[name][5]["exit_price"]
            curve = ax.plot(lambda t, ex=ex: price * (ex / price) ** (t / 5), x_range=[0, 5], color=col, stroke_width=5)
            lines[name] = curve
            ends[name] = VGroup(Dot(ax.c2p(5, ex), radius=0.08, color=col),
                                txt(f"${ex:.0f}", size=21, color=col, weight="SEMIBOLD").next_to(ax.c2p(5, ex), RIGHT, buff=0.12))
            row = sc[(sc["scenario"] == name) & (sc["horizon_years"] == 5)].iloc[0]
            cards[name] = VGroup(
                VGroup(txt(name.capitalize(), size=26, color=col, weight="BOLD"), txt(f"p = {row['probability']:.0%}", size=22, color=INK2)).arrange(RIGHT, buff=0.3),
                txt(f"EPS +{row['eps_cagr_1_5']:.0%}/yr, exit {row['exit_forward_pe']:.0f}×", size=21, color=INK2),
                txt(f"{row['annualised_return_usd']:+.1%} a year", size=26, color=col, weight="SEMIBOLD"),
            ).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
        VGroup(*[cards[n] for n in ("bull", "base", "bear")]).arrange(DOWN, buff=0.45, aligned_edge=LEFT).move_to([3.9, -0.6, 0])
        note = txt("illustrative paths; the model only fixes the end point", size=16, color=FAINT).next_to(ax, DOWN, buff=0.5)
        with self.say("bear") as d:
            self.play(FadeIn(h), Create(ax), FadeIn(ax.extras), FadeIn(start), FadeIn(sl), FadeIn(note), run_time=0.7)
            self.at(d * 0.55, Create(lines["bear"]), FadeIn(cards["bear"][:2]), run_time=1.4)
            self.play(FadeIn(ends["bear"]), FadeIn(cards["bear"][2]), run_time=0.5)
        for name in ("base", "bull"):
            with self.say(name) as d:
                self.play(FadeIn(cards[name][:2]), run_time=0.5)
                self.at(d * 0.45, Create(lines[name]), run_time=1.2)
                self.play(FadeIn(ends[name]), FadeIn(cards[name][2]), run_time=0.5)
        pb = VGroup()
        for name, w in (("bear", 0.25), ("base", 0.5), ("bull", 0.25)):
            pb.add(Rectangle(width=5.0 * w, height=0.42, fill_color=SC[name], fill_opacity=0.9, stroke_color=BG, stroke_width=3))
        pb.arrange(RIGHT, buff=0).move_to([3.7, -3.25, 0])
        pbl = VGroup(*[txt(t, size=18).move_to(r) for t, r in zip(("25%", "50%", "25%"), pb)])
        pbt = tag("J").next_to(pb, RIGHT, buff=0.15)
        with self.say("prob"):
            self.play(FadeOut(note), FadeIn(pb), FadeIn(pbl), FadeIn(pbt), run_time=0.7)
        self.clear()

        # ---------------------------------------------------------- combining the scenarios
        h = heading("Expected return: weight the ending wealth")
        w5, w10 = paths["probability-weighted"][5]["annualised_return_usd"], paths["probability-weighted"][10]["annualised_return_usd"]
        xs = [-6.0, -3.9, -2.4, -0.6]
        ys = [1.75 - 0.66 * i for i in range(5)]
        table = VGroup()
        hdr = VGroup(*[txt(t, size=22, color=MUTED).move_to([xs[j], ys[0], 0], aligned_edge=LEFT)
                       for j, t in ((1, "p"), (2, "5 years"), (3, "10 years"))])
        table.add(hdr)
        for i, (name, p_) in enumerate((("bear", "25%"), ("base", "50%"), ("bull", "25%")), start=1):
            r5 = paths[name][5]["annualised_return_usd"]
            r10 = paths[name][10]["annualised_return_usd"]
            cells = [txt(name.capitalize(), size=26, color=SC[name], weight="SEMIBOLD"), txt(p_, size=24, color=INK2),
                     txt(f"{r5:+.1%}", size=26), txt(f"{r10:+.1%}", size=26)]
            table.add(VGroup(*[c.move_to([xs[j], ys[i], 0], aligned_edge=LEFT) for j, c in enumerate(cells)]))
        wrow = [(0, txt("Weighted", size=26, weight="BOLD")), (2, txt(f"{w5:.1%}", size=30, color=YELLOW, weight="BOLD")),
                (3, txt(f"{w10:.1%}", size=30, color=YELLOW, weight="BOLD"))]
        table.add(VGroup(*[c.move_to([xs[j], ys[4], 0], aligned_edge=LEFT) for j, c in wrow]))
        rule = Line([xs[0], (ys[3] + ys[4]) / 2, 0], [0.9, (ys[3] + ys[4]) / 2, 0], color=FAINT)
        e5 = tag("E").next_to(table[4][-1], RIGHT, buff=0.15)
        with self.say("ew1") as d:
            self.play(FadeIn(h), FadeIn(table[:4]), run_time=0.8)
            self.at(d * 0.45, Create(rule), FadeIn(table[4]), FadeIn(e5), run_time=0.8)
        # Jensen: average of rates vs rate of the average wealth
        jx = axes([-0.05, 0.2, 0.05], [0.6, 2.2, 0.4], 4.4, 3.4, y_ticks=[1.0, 1.4, 1.8, 2.2], y_fmt=lambda y: f"{y:.1f}×",
                  x_ticks=[0, 0.1, 0.2], x_fmt=lambda x: f"{x:.0%}")
        jx.move_to([4.15, -0.4, 0])
        jc = jx.plot(lambda r: (1 + r) ** 5, x_range=[-0.05, 0.2], color=INK2, stroke_width=3)
        pts = VGroup(*[Dot(jx.c2p(paths[n][5]["annualised_return_usd"], paths[n][5]["wealth_multiple"]), radius=0.07, color=SC[n])
                       for n in ("bear", "base", "bull")])
        mr = data.mean_of_returns(5)
        ew = paths["probability-weighted"][5]["wealth_multiple"]
        avg_pt = Dot(jx.c2p(mr, ew), radius=0.09, color=YELLOW)
        on_curve = Dot(jx.c2p(mr, (1 + mr) ** 5), radius=0.07, color=INK)
        gapl = VGroup(DashedLine(on_curve.get_center(), avg_pt.get_center(), color=YELLOW, dash_length=0.05),
                      DashedLine(avg_pt.get_center(), jx.c2p(w5, ew), color=YELLOW, dash_length=0.05),
                      Dot(jx.c2p(w5, ew), radius=0.07, color=YELLOW))
        jl = tex(r"\mathbb{E}\big[(1+r)^T\big] \ge \big(1+\mathbb{E}[r]\big)^T", size=30, color=YELLOW).next_to(jx, DOWN, buff=0.35)
        jt = txt("wealth after 5 years", size=18, color=MUTED).next_to(jx, UP, buff=0.1)
        jn = VGroup(txt(f"average of the rates {mr:.1%}", size=20, color=INK),
                    txt(f"rate of the average wealth {w5:.1%}", size=20, color=YELLOW)).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
        jn.next_to(jt, UP, buff=0.15)
        with self.say("ew2") as d:
            self.play(Create(jx), FadeIn(jx.extras), Create(jc), FadeIn(jt), run_time=0.8)
            self.play(FadeIn(pts), run_time=0.5)
            self.at(d * 0.35, FadeIn(on_curve), FadeIn(avg_pt), Create(gapl), FadeIn(jn), run_time=0.9)
            self.at(d * 0.6, Write(jl), run_time=1.2)
        self.clear()

        # ---------------------------------------------------------- return grid
        h = heading("Five-year return: earnings growth × exit P/E")
        rg = data.return_grid_5y()
        rows_ = sorted(rg.index, reverse=True)
        cols_ = list(rg.columns)
        cw, ch = 1.15, 0.62
        gx, gy = -3.65, 1.35
        cells, at = VGroup(), {}
        for i, gr in enumerate(rows_):
            for j, pe in enumerate(cols_):
                val = rg.loc[gr, pe]
                col, op = ret_color(val)
                rect = Rectangle(width=cw, height=ch, fill_color=col, fill_opacity=op, stroke_color=BG, stroke_width=3)
                rect.move_to([gx + j * cw, gy - i * ch, 0])
                cells.add(VGroup(rect, txt(f"{val * 100:.1f}", size=20).move_to(rect)))
                at[(gr, pe)] = rect
        rl = VGroup(*[txt(f"{gr:.0%}", size=20, color=INK2).next_to(at[(gr, cols_[0])], LEFT, buff=0.2) for gr in rows_])
        cl = VGroup(*[txt(f"{pe:.0f}×", size=20, color=INK2).next_to(at[(rows_[-1], pe)], DOWN, buff=0.15) for pe in cols_])
        rt = txt("EPS growth\nper year", size=19, color=MUTED).next_to(rl, LEFT, buff=0.2)
        ct = txt("exit P/E", size=19, color=MUTED).next_to(cl, DOWN, buff=0.12)
        leg = VGroup(*[VGroup(Square(0.24, fill_color=c, fill_opacity=0.8, stroke_width=0), txt(t, size=19)).arrange(RIGHT, buff=0.12)
                       for c, t in ((AQUA, "10% or more"), (YELLOW, "7 – 10%, ≈ index"), (ORANGE, "below 7%"))])
        leg.arrange(DOWN, buff=0.14, aligned_edge=LEFT).next_to(cells, RIGHT, buff=0.35).align_to(cells, UP)
        with self.say("grid1") as d:
            self.play(FadeIn(h), FadeIn(rl), FadeIn(cl), FadeIn(rt), FadeIn(ct), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(c) for c in cells], lag_ratio=0.02), FadeIn(leg), run_time=1.6)
        combos = [(0.11, 26.0), (0.13, 24.0), (0.15, 22.0)]
        outl = VGroup(*[SurroundingRectangle(at[c], color=INK, buff=0, stroke_width=4) for c in combos])
        med = VGroup(at[(0.11, 22.0)], at[(0.09, 24.0)])
        medr = DashedVMobject(Rectangle(width=2 * cw, height=2 * ch, color=YELLOW, stroke_width=4), num_dashes=30)
        medr.move_to(VGroup(at[(0.11, 22.0)], at[(0.09, 24.0)]))
        outk = VGroup(Square(0.24, stroke_color=INK, stroke_width=3, fill_opacity=0), txt("needed for 10%", size=19)).arrange(RIGHT, buff=0.12)
        medl = VGroup(DashedVMobject(Square(0.24, color=YELLOW, stroke_width=3), num_dashes=8),
                      txt("median outcome", size=19, color=YELLOW)).arrange(RIGHT, buff=0.12)
        VGroup(outk, medl).arrange(DOWN, buff=0.14, aligned_edge=LEFT).next_to(leg, DOWN, buff=0.35, aligned_edge=LEFT)
        with self.say("grid2") as d:
            for k, o in enumerate(outl):
                self.at(d * (0.12 + 0.12 * k), Create(o), *([FadeIn(outk)] if k == 0 else []), run_time=0.5)
            self.at(d * 0.62, Create(medr), FadeIn(medl), run_time=0.8)
        self.clear()

        # ---------------------------------------------------------- vs the index
        h = heading("Visa vs the index fund, expected return per year")
        ic = data.index_comparison().set_index("horizon_years").loc[10]
        lo_, hi_ = ic["index_expected_return"].min() * 100, ic["index_expected_return"].max() * 100
        rx = NumberLine(x_range=[0, 12, 2], length=11, color=FAINT, include_ticks=True, tick_size=0.06, stroke_width=2).move_to(0.9 * DOWN)
        rt_ = VGroup(*[txt(f"{v}%", size=20, color=MUTED).next_to(rx.n2p(v), DOWN, buff=0.18) for v in range(0, 13, 2)])
        band = Rectangle(width=rx.n2p(hi_)[0] - rx.n2p(lo_)[0], height=0.55, fill_color=YELLOW, fill_opacity=0.3,
                         stroke_color=YELLOW, stroke_width=2).move_to((rx.n2p(lo_) + rx.n2p(hi_)) / 2 + 0.3 * UP)
        bl1 = txt(f"market-implied {hi_:.1f}%", size=20, color=YELLOW).next_to(band.get_corner(UR), UR, buff=0.08)
        bl2 = txt(f"conservative {lo_:.0f}%", size=20, color=YELLOW).next_to(band.get_corner(UL), UL, buff=0.08)
        bt = txt("global index fund", size=24, color=YELLOW, weight="SEMIBOLD").next_to(band, UP, buff=0.75)
        with self.say("idx1") as d:
            self.play(FadeIn(h), Create(rx), FadeIn(rt_), run_time=0.6)
            self.play(FadeIn(band), FadeIn(bt), FadeIn(bl1), run_time=0.8)
            self.at(d * 0.62, FadeIn(bl2), run_time=0.5)
        v5_, v10_ = w5 * 100, w10 * 100
        vb = Rectangle(width=rx.n2p(v5_)[0] - rx.n2p(v10_)[0], height=0.55, fill_color=BLUE, fill_opacity=1, stroke_width=0)
        vb.move_to((rx.n2p(v5_) + rx.n2p(v10_)) / 2 + 0.3 * UP)
        vl = VGroup(txt(f"Visa {v10_:.1f} – {v5_:.1f}%", size=24, color=BLUE, weight="SEMIBOLD"), tag("E")).arrange(RIGHT, buff=0.12)
        vl.next_to(rx, DOWN, buff=0.8).set_x(rx.n2p((v5_ + v10_) / 2)[0])
        vline = Line(vb.get_bottom(), vl.get_top(), color=BLUE, stroke_width=2)
        capm = data._valuation().CAPM * 100
        ct_ = VGroup(Line(rx.n2p(capm) + 0.6 * UP, rx.n2p(capm) + 0.05 * DOWN, color=VIOLET, stroke_width=4),
                     txt(f"CAPM {capm:.1f}%", size=19, color=VIOLET))
        ct_[1].next_to(ct_[0], UP, buff=0.06)
        verdict = VGroup(txt("priced fairly", size=26, color=INK), tag("J")).arrange(RIGHT, buff=0.12).next_to(vl, DOWN, buff=0.35)
        with self.say("idx2") as d:
            self.play(FadeIn(vb), Create(vline), FadeIn(vl), run_time=0.8)
            self.at(d * 0.4, FadeIn(ct_), run_time=0.6)
            self.at(d * 0.72, FadeIn(verdict), run_time=0.5)
        self.clear()

        # ---------------------------------------------------------- the price you pay
        h = heading("Expected 10-year return vs the price you pay")
        prices = np.linspace(260, 460, 41)
        rets = data.price_return_curve(prices, 10)
        ax = axes([250, 470, 50], [0.06, 0.14, 0.02], 9.0, 4.4, y_ticks=[0.06, 0.08, 0.10, 0.12, 0.14], y_fmt=lambda y: f"{y:.0%}",
                  x_ticks=[250, 300, 350, 400, 450], x_fmt=lambda x: f"${x:.0f}")
        ax.move_to([-0.9, -0.85, 0])
        curve = line_through(ax, list(prices), rets, color=AQUA, width=5)
        xl = txt("purchase price", size=19, color=MUTED).next_to(ax, DOWN, buff=0.45)
        with self.say("bb1") as d:
            self.play(FadeIn(h), Create(ax), FadeIn(ax.extras), FadeIn(xl), run_time=0.7)
            self.play(Create(curve), run_time=1.6)
        bbp = data.buy_below().set_index(["target_expected_return", "horizon_years"]).loc[(0.10, 10)]
        now_r = data.price_return_curve([price], 10)[0]
        def mark(x, y, color, label, side):
            g = VGroup(dashed(ax.c2p(x, 0.06), ax.c2p(x, y), color=color), dashed(ax.c2p(250, y), ax.c2p(x, y), color=color),
                       Dot(ax.c2p(x, y), radius=0.09, color=color))
            l = txt(label, size=21, color=color, weight="SEMIBOLD").next_to(ax.c2p(x, y), side, buff=0.15)
            return VGroup(g, l)
        m_now = mark(price, now_r, ORANGE, f"today ${price:.0f}: {now_r:.1%}", UR)
        m_bb = mark(bbp["buy_below_price"], 0.10, AQUA, f"${bbp['buy_below_price']:.0f}: 10%  ({bbp['implied_forward_pe_fy2027e']:.0f}× FY2027E)", UR)
        sep25 = data.history().loc["2025", "price"]
        m_sep = VGroup(Line(ax.c2p(sep25, 0.06), ax.c2p(sep25, 0.065), color=INK2, stroke_width=4),
                       txt(f"Sep 2025: ${sep25:.0f}", size=19, color=INK2).next_to(ax.c2p(sep25, 0.065), UP, buff=0.08))
        with self.say("bb2") as d:
            self.play(FadeIn(m_now), run_time=0.6)
            self.at(d * 0.15, FadeIn(m_bb), run_time=0.8)
            self.play(FadeIn(tag("E").next_to(m_bb[1], RIGHT, buff=0.12)), run_time=0.3)
            self.at(d * 0.7, FadeIn(m_sep), run_time=0.6)
        self.finish()
