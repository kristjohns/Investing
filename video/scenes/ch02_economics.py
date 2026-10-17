import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from manim import *  # noqa: E402,F403

import data  # noqa: E402
from style import *  # noqa: E402,F403


class Ch02Economics(Chapter):
    KEY = "economics"
    CONCEPTS = ["network effect", "operating leverage", "operating margin", "GAAP vs non-GAAP", "ROIC",
                "cost of capital"]

    def construct(self):
        f = data.fin()
        self.title_card()

        # ---------------------------------------------------------- two-sided network
        h = heading("A two-sided network")
        left = VGroup(*[Dot(radius=0.1, color=BLUE) for _ in range(6)]).arrange(DOWN, buff=0.4).move_to([-5.7, -0.5, 0])
        right = VGroup(*[Dot(radius=0.1, color=AQUA) for _ in range(6)]).arrange(DOWN, buff=0.4).move_to([-3.1, -0.5, 0])
        edges = VGroup(*[Line(a_.get_center(), b_.get_center(), stroke_width=1.2, color=FAINT) for a_ in left for b_ in right])
        la = txt("Cardholders", size=24, color=BLUE).next_to(left, UP, buff=0.3)
        ra = txt("Merchants", size=24, color=AQUA).next_to(right, UP, buff=0.3)
        with self.say("net1"):
            self.play(FadeIn(h), FadeIn(la), FadeIn(ra), run_time=0.5)
            self.play(LaggedStart(*[FadeIn(d_, scale=0.5) for d_ in [*left, *right]], lag_ratio=0.08), run_time=1.0)
            self.play(Create(edges, lag_ratio=0.02), run_time=1.4)
        # positive feedback loop, drawn like a block diagram
        n1 = boxed(txt("more cardholders", size=22, color=BLUE), color=BLUE, buff=0.2).move_to([0.45, -0.5, 0])
        n2 = boxed(txt("more merchants", size=22, color=AQUA), color=AQUA, buff=0.2).move_to([5.3, -0.5, 0])
        top = CurvedArrow(n1.get_top() + 0.05 * UP, n2.get_top() + 0.05 * UP, angle=-1.2, color=INK2, stroke_width=3)
        bot = CurvedArrow(n2.get_bottom() + 0.05 * DOWN, n1.get_bottom() + 0.05 * DOWN, angle=-1.2, color=INK2, stroke_width=3)
        tl_ = txt("want acceptance", size=19, color=INK2).next_to(top, UP, buff=0.08)
        bl_ = txt("accept the cards people carry", size=19, color=INK2).next_to(bot, DOWN, buff=0.08)
        plus = txt("+", size=40, color=YELLOW, weight="BOLD")
        pf = VGroup(txt("positive", size=18, color=YELLOW), txt("feedback", size=18, color=YELLOW)).arrange(DOWN, buff=0.06)
        VGroup(plus, pf).arrange(DOWN, buff=0.1).move_to([(n1.get_right()[0] + n2.get_left()[0]) / 2, -0.5, 0])
        newcomer = txt("a newcomer must win both sides at once", size=21, color=MUTED).move_to([2.85, -3.2, 0])
        with self.say("net2") as d:
            self.play(FadeIn(n1), FadeIn(n2), run_time=0.5)
            self.play(Create(top), FadeIn(tl_), run_time=0.8)
            self.play(Create(bot), FadeIn(bl_), FadeIn(plus), FadeIn(pf), run_time=0.8)
            self.at(d * 0.72, FadeIn(newcomer), run_time=0.6)
        loop = VGroup(n1, n2, top, bot, tl_, bl_, plus, pf, newcomer)
        big = stat("40.8%", "of all card purchase transactions in the world, 2025", BLUE, vsize=72, lsize=24, kind="F")
        big.move_to([0, -0.4, 0])
        with self.say("net3") as d:
            self.at(d * 0.45, FadeOut(VGroup(left, right, edges, la, ra, loop)), FadeIn(big, scale=0.95),
                    run_time=0.8)
        self.clear()

        # ---------------------------------------------------------- operating leverage
        h = heading("Operating leverage")
        y = f.loc[2025]
        costs = VGroup(*[VGroup(txt(n, size=24, color=INK2), txt(v, size=24, weight="SEMIBOLD")).arrange(RIGHT, buff=0.3)
                         for n, v in (("People", f"${y['personnel'] / 1000:.1f}bn"),
                                      ("Marketing", f"${y['marketing'] / 1000:.1f}bn"),
                                      ("Network and processing", f"${y['network_processing'] / 1000:.1f}bn"))])
        costs.arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        ct = txt("Biggest costs, fiscal 2025", size=22, color=MUTED)
        cg = VGroup(ct, costs).arrange(DOWN, buff=0.25, aligned_edge=LEFT).next_to(h, DOWN, buff=0.5, aligned_edge=LEFT)
        with self.say("ol1"):
            self.play(FadeIn(h), run_time=0.4)
            self.play(FadeIn(cg, shift=0.1 * RIGHT), run_time=0.8)
        eqs = VGroup(tex(r"\text{cost} = F + vQ \qquad \text{revenue} = pQ", size=38),
                     tex(r"m(Q) = 1 - \frac{v}{p} - \frac{F}{p\,Q}", size=46)).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        eqs.next_to(h, DOWN, buff=0.55).to_edge(RIGHT, buff=0.7)
        with self.say("ol2") as d:
            self.play(FadeIn(eqs[0]), run_time=0.7)
            self.at(d * 0.45, Write(eqs[1]), run_time=1.4)
        ax = axes([0, 10, 1], [0, 1, 0.25], 6.2, 2.6, y_ticks=[0, 1], y_fmt=lambda v: f"{v:.0%}")
        ax.move_to([2.6, -2.15, 0])
        curve = ax.plot(lambda q: max(0.9 - 1.0 / q, 0), x_range=[1.12, 10, 0.02], color=BLUE, stroke_width=5)
        ceil = dashed(ax.c2p(0, 0.9), ax.c2p(10, 0.9), color=AQUA)
        ceil_l = tex(r"1 - v/p", size=30, color=AQUA).next_to(ax.c2p(10, 0.9), UP, buff=0.08).shift(0.6 * LEFT)
        xl = txt("transactions Q", size=18, color=MUTED).next_to(ax.c2p(10, 0), DOWN, buff=0.12).shift(0.7 * LEFT)
        sch = txt("schematic", size=17, color=FAINT).next_to(ax, LEFT, buff=0.2).shift(0.9 * DOWN)
        fact = VGroup(txt(f"Network and processing: {y['network_processing'] / y['net_revenue']:.1%} of revenue", size=22),
                      tag("F")).arrange(RIGHT, buff=0.15).next_to(cg, DOWN, buff=0.7, aligned_edge=LEFT)
        with self.say("ol3") as d:
            self.play(Create(ax), FadeIn(ax.extras), FadeIn(xl), FadeIn(sch), run_time=0.5)
            self.play(Create(curve), run_time=1.6)
            self.play(Create(ceil), FadeIn(ceil_l), run_time=0.6)
            self.at(d * 0.62, FadeIn(fact), run_time=0.6)
        self.clear()

        # ---------------------------------------------------------- operating margin
        h = heading("Operating margin")
        de = tex(r"\text{operating margin} = \frac{\text{operating profit}}{\text{revenue}}", size=44).next_to(h, DOWN, buff=0.5).set_x(0)
        with self.say("om1"):
            self.play(FadeIn(h), run_time=0.4)
            self.play(Write(de), run_time=1.2)
        ax = axes([0, 2, 1], [0, 0.8, 0.2], 4.2, 3.0, y_ticks=[0, 0.2, 0.4, 0.6, 0.8], y_fmt=lambda v: f"{v:.0%}")
        ax.move_to([-3.2, -1.6, 0])
        gm, nm = f.loc[2025, "op_margin"], f.loc[2025, "nongaap_op_margin"]
        b1 = bar_at(ax, 0.55, 0, gm, 1.1, BLUE)
        b2 = bar_at(ax, 1.45, 0, nm, 1.1, VIOLET)
        v1 = txt(fmt_pct(gm), size=24, weight="SEMIBOLD").next_to(b1, UP, buff=0.08)
        v2 = txt(fmt_pct(nm), size=24, weight="SEMIBOLD").next_to(b2, UP, buff=0.08)
        l1 = txt("GAAP", size=20, color=INK2).next_to(ax.c2p(0.55, 0), DOWN, buff=0.12)
        l2 = txt("non-GAAP", size=20, color=INK2).next_to(ax.c2p(1.45, 0), DOWN, buff=0.12)
        prov = txt(f"FY2025 includes a ${f.loc[2025, 'litigation_provision'] / 1000:.1f}bn lawsuit provision", size=20, color=MUTED)
        prov.next_to(ax, UP, buff=0.25).align_to(ax, LEFT)
        with self.say("om2") as d:
            self.play(Create(ax), FadeIn(ax.extras), run_time=0.5)
            self.play(GrowFromEdge(b1, DOWN), FadeIn(v1), FadeIn(l1), FadeIn(prov), run_time=0.8)
            self.at(d * 0.6, GrowFromEdge(b2, DOWN), FadeIn(v2), FadeIn(l2), run_time=0.8)
            self.play(FadeIn(tag("F").next_to(v2, RIGHT, buff=0.1)), run_time=0.3)
        ax2 = axes([2022.5, 2025.5, 1], [0.6, 0.75, 0.05], 4.6, 2.6, y_ticks=[0.6, 0.65, 0.7, 0.75],
                   y_fmt=lambda v: f"{v:.0%}", x_ticks=[2023, 2024, 2025], x_fmt=lambda v: f"FY{v}")
        ax2.move_to([3.6, -1.75, 0])
        ys = [f.loc[y_, "nongaap_op_margin"] for y_ in (2023, 2024, 2025)]
        ln = line_through(ax2, [2023, 2024, 2025], ys, color=VIOLET, width=5)
        dots = VGroup(*[Dot(ax2.c2p(x, v), radius=0.08, color=VIOLET) for x, v in zip((2023, 2024, 2025), ys)])
        labs = VGroup(*[txt(fmt_pct(v), size=20).next_to(dd, UP, buff=0.12) for dd, v in zip(dots, ys)])
        t2 = txt("non-GAAP margin: flat", size=22, color=INK2).next_to(ax2, UP, buff=0.25)
        with self.say("om3"):
            self.play(Create(ax2), FadeIn(ax2.extras), FadeIn(t2), run_time=0.5)
            self.play(Create(ln), FadeIn(dots), FadeIn(labs), run_time=1.0)
        self.clear()

        # ---------------------------------------------------------- ROIC
        h = heading("Return on invested capital (ROIC)")
        machine = VGroup(
            boxed(txt("the business", size=26), color=BLUE, buff=0.35),
        )
        cin = Arrow(LEFT * 2.8, ORIGIN, buff=0, color=INK2, stroke_width=4)
        cout = Arrow(ORIGIN, RIGHT * 2.8, buff=0, color=AQUA, stroke_width=4)
        cin.next_to(machine, LEFT, buff=0.1)
        cout.next_to(machine, RIGHT, buff=0.1)
        lin = txt("capital in", size=22, color=INK2).next_to(cin, UP, buff=0.22)
        lout = txt("after-tax profit out", size=22, color=AQUA).next_to(cout, UP, buff=0.22)
        mach = VGroup(machine, cin, cout, lin, lout).next_to(h, DOWN, buff=0.7).set_x(-1.0)
        f1 = tex(r"\text{ROIC} = \frac{\text{NOPAT}}{\text{invested capital}}, \quad \text{NOPAT} = \text{EBIT}\,(1 - t)", size=36)
        f1.next_to(mach, DOWN, buff=0.45).set_x(0)
        with self.say("roic1") as d:
            self.play(FadeIn(h), run_time=0.4)
            self.play(FadeIn(machine), GrowArrow(cin), FadeIn(lin), run_time=0.7)
            self.play(GrowArrow(cout), FadeIn(lout), run_time=0.7)
            self.at(d * 0.55, Write(f1), run_time=1.4)
        f2 = mtxt("value is created when " + hl("ROIC", AQUA) + " &gt; " + hl("cost of capital ≈ 8.5%", YELLOW), size=28)
        f2.next_to(f1, DOWN, buff=0.4)
        with self.say("roic2") as d:
            self.at(d * 0.55, FadeIn(f2, shift=0.1 * UP), run_time=0.7)
        self.play(FadeOut(VGroup(mach, f1)), f2.animate.next_to(h, DOWN, buff=0.35, aligned_edge=LEFT), run_time=0.6)
        ax = axes([2014.5, 2025.5, 1], [0, 0.5, 0.1], 9.0, 3.9, y_ticks=[0, 0.1, 0.2, 0.3, 0.4, 0.5],
                  y_fmt=lambda v: f"{v:.0%}", x_ticks=[2015, 2017, 2019, 2021, 2023, 2025])
        ax.move_to([-0.9, -1.2, 0])
        yrs = list(range(2015, 2026))
        rg = [f.loc[y_, "roic_gross"] for y_ in yrs]
        yn = list(range(2020, 2026))
        rn = [f.loc[y_, "roic_net"] for y_ in yn]
        lg = line_through(ax, yrs, rg, color=BLUE, width=5)
        lnet = line_through(ax, yn, rn, color=AQUA, width=5)
        coc = dashed(ax.c2p(2014.5, 0.085), ax.c2p(2025.5, 0.085), color=YELLOW, width=2.5)
        cl = txt("cost of capital 8.5%", size=19, color=YELLOW).next_to(ax.c2p(2014.6, 0.085), UP, buff=0.06, aligned_edge=LEFT)
        el = VGroup(txt(f"{rg[-1]:.0%} on all capital", size=20, color=BLUE).next_to(ax.c2p(2025, rg[-1]), RIGHT, buff=0.12),
                    txt(f"{rn[-1]:.0%} net of cash", size=20, color=AQUA).next_to(ax.c2p(2025, rn[-1]), RIGHT, buff=0.12))
        sl = txt(f"{rg[0]:.0%}", size=20, color=BLUE).next_to(ax.c2p(2015, rg[0]), UP, buff=0.12)
        with self.say("roic3") as d:
            self.play(Create(ax), FadeIn(ax.extras), Create(coc), FadeIn(cl), run_time=0.7)
            self.play(Create(lg), FadeIn(sl), run_time=1.5)
            self.play(FadeIn(el[0]), run_time=0.3)
            self.at(d * 0.7, Create(lnet), FadeIn(el[1]), run_time=1.0)
            self.play(FadeIn(tag("E").next_to(el, RIGHT, buff=0.1)), run_time=0.3)
        self.clear()

        # ---------------------------------------------------------- negative tangible capital
        h = heading("Almost no tangible capital")
        gi = (f.loc[2025, "goodwill"] + f.loc[2025, "intangibles_net"]) / 1000
        ic = f.loc[2025, "invested_capital_net"] / 1000
        ax = axes([0, 2, 1], [0, 50, 10], 4.6, 3.6, y_ticks=[0, 25, 50], y_fmt=lambda v: f"${v}bn")
        ax.move_to([-3.0, -1.0, 0])
        b1 = bar_at(ax, 0.55, 0, gi, 1.2, VIOLET)
        b2 = bar_at(ax, 1.45, 0, ic, 1.2, BLUE)
        v1 = txt(f"${gi:.1f}bn", size=22, weight="SEMIBOLD").next_to(b1, UP, buff=0.08)
        v2 = txt(f"${ic:.1f}bn", size=22, weight="SEMIBOLD").next_to(b2, UP, buff=0.08)
        l1 = txt("goodwill +\nintangibles", size=19, color=INK2).next_to(ax.c2p(0.55, 0), DOWN, buff=0.12)
        l2 = txt("net invested\ncapital", size=19, color=INK2).next_to(ax.c2p(1.45, 0), DOWN, buff=0.12)
        concl = mtxt("tangible capital " + hl("&lt; 0", ORANGE), size=30).move_to([3.4, 0.4, 0])
        with self.say("tang1") as d:
            self.play(FadeIn(h), Create(ax), FadeIn(ax.extras), run_time=0.5)
            self.play(GrowFromEdge(b1, DOWN), FadeIn(v1), FadeIn(l1), run_time=0.8)
            self.at(d * 0.5, GrowFromEdge(b2, DOWN), FadeIn(v2), FadeIn(l2), run_time=0.8)
            self.at(d * 0.82, FadeIn(concl), FadeIn(tag("E").next_to(concl, RIGHT, buff=0.12)), run_time=0.5)
        cap = stat(fmt_pct(f.loc[2025, "capex_pct_rev"]), "capital expenditure / revenue, FY2025", AQUA, vsize=56, lsize=22, kind="F")
        cap.next_to(concl, DOWN, buff=0.7)
        arrow = txt("→ nearly all cash can be paid out", size=24, color=INK2).next_to(cap, DOWN, buff=0.4)
        with self.say("tang2") as d:
            self.play(FadeIn(cap, shift=0.1 * UP), run_time=0.7)
            self.at(d * 0.5, FadeIn(arrow), run_time=0.6)
        self.finish()
