import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from manim import *  # noqa: E402,F403

import data  # noqa: E402
from style import *  # noqa: E402,F403


def node(title, sub, color, w=3.1, h=1.15):
    box = RoundedRectangle(corner_radius=0.14, width=w, height=h, fill_color=PANEL, fill_opacity=1,
                           stroke_color=color, stroke_width=2.5)
    t = txt(title, size=28, weight="SEMIBOLD")
    s = txt(sub, size=19, color=INK2)
    VGroup(t, s).arrange(DOWN, buff=0.08).move_to(box)
    return VGroup(box, t, s)


class Ch01Business(Chapter):
    KEY = "business"
    CONCEPTS = ["four-party network", "interchange", "gross vs net revenue", "contra revenue", "take rate"]

    def construct(self):
        f = data.fin()
        self.title_card()

        # ---------------------------------------------------------- four-party diagram
        holder = node("Cardholder", "you", BLUE).move_to([-4.6, 1.45, 0])
        merchant = node("Merchant", "the shop", AQUA).move_to([4.6, 1.45, 0])
        issuer = node("Issuer", "your bank", ORANGE).move_to([-4.6, -1.55, 0])
        acquirer = node("Acquirer", "merchant's bank", YELLOW).move_to([4.6, -1.55, 0])
        visanet = node("VisaNet", "Visa's network", VIOLET, w=2.6).move_to([0, -1.55, 0])
        parts = [holder, merchant, acquirer, issuer]
        for p in parts:
            p.set_opacity(0.25)
        with self.say("four"):
            self.play(LaggedStart(*[FadeIn(p) for p in parts], lag_ratio=0.25), run_time=1.2)
        tap = Arrow(holder.get_right(), merchant.get_left(), buff=0.15, color=INK2, stroke_width=3)
        tap_lab = txt("taps card", size=20, color=INK2).next_to(tap, UP, buff=0.1)
        with self.say("parties") as d:
            for k, p in enumerate(parts):
                self.at(k * d / 4.3, p.animate.set_opacity(1), run_time=0.45)
                if k == 1:
                    self.play(GrowArrow(tap), FadeIn(tap_lab), run_time=0.4)
        a2v = Arrow(acquirer.get_left(), visanet.get_right(), buff=0.12, color=VIOLET, stroke_width=3)
        v2i = Arrow(visanet.get_left(), issuer.get_right(), buff=0.12, color=VIOLET, stroke_width=3)
        m2a = Arrow(merchant.get_bottom(), acquirer.get_top(), buff=0.12, color=INK2, stroke_width=3)
        msg = Dot(radius=0.09, color=INK).move_to(merchant.get_bottom())
        steps = VGroup(txt("1  authorise", size=22, color=INK2), txt("2  clear", size=22, color=INK2),
                       txt("3  settle", size=22, color=INK2)).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        steps.next_to(visanet, DOWN, buff=0.35)
        with self.say("visanet") as d:
            self.play(FadeIn(visanet, scale=0.9), run_time=0.6)
            self.play(GrowArrow(m2a), GrowArrow(a2v), GrowArrow(v2i), run_time=0.8)
            path = VMobject().set_points_as_corners([merchant.get_bottom(), acquirer.get_top(), acquirer.get_left(),
                                                     visanet.get_right(), visanet.get_left(), issuer.get_right()])
            self.add(msg)
            self.play(MoveAlongPath(msg, path), run_time=2.0, rate_func=linear)
            self.play(FadeOut(msg), LaggedStart(*[FadeIn(s, shift=0.1 * RIGHT) for s in steps], lag_ratio=0.6), run_time=1.6)
        # fees
        inter = CurvedArrow(merchant.get_corner(DL) + 0.1 * UP, issuer.get_corner(UR) + 0.1 * DOWN, angle=-0.35,
                            color=ORANGE, stroke_width=4)
        inter_lab = mtxt(hl("interchange fee", ORANGE) + " → your bank", size=22).move_to([-0.9, 0.8, 0])
        with self.say("interchange"):
            self.play(Create(inter), run_time=1.0)
            self.play(FadeIn(inter_lab), run_time=0.5)
        fee1 = Arrow(issuer.get_bottom() + 0.6 * RIGHT, visanet.get_bottom() + 0.5 * LEFT, buff=0.1, color=BLUE,
                     stroke_width=3, path_arc=0.6)
        fee2 = Arrow(acquirer.get_bottom() + 0.6 * LEFT, visanet.get_bottom() + 0.5 * RIGHT, buff=0.1, color=BLUE,
                     stroke_width=3, path_arc=-0.6)
        fee_lab = txt("Visa's fees, from both banks", size=22, color=BLUE)
        inc_lab = txt("minus client incentives paid back", size=22, color=YELLOW)
        VGroup(fee_lab, inc_lab).arrange(DOWN, buff=0.1).move_to([0, -3.35, 0])
        with self.say("fees") as d:
            self.play(FadeOut(steps), run_time=0.3)
            self.play(Create(fee1), Create(fee2), FadeIn(fee_lab), run_time=1.0)
            self.at(d * 0.55, FadeIn(inc_lab), run_time=0.5)
        self.clear()

        # ---------------------------------------------------------- revenue waterfall
        y = f.loc[2025]
        lines = [("Service", y["service_rev"], BLUE), ("Data\nprocessing", y["data_processing_rev"], BLUE),
                 ("International", y["intl_transaction_rev"], BLUE), ("Other", y["other_rev"], BLUE)]
        gross, inc, net = y["gross_revenue"], y["client_incentives"], y["net_revenue"]
        h = heading("Visa's revenue, fiscal 2025")
        ax = axes([0, 7.6, 1], [0, 60, 10], 11.6, 4.6, y_ticks=[0, 20, 40, 60], y_fmt=lambda v: f"${v}bn")
        ax.move_to([0.5, -0.65, 0])
        bars, labs, vals = VGroup(), VGroup(), VGroup()
        base = 0.0
        for k, (name, v, c) in enumerate(lines):
            b = bar_at(ax, k + 0.6, base / 1000, (base + v) / 1000, 1.05, c, 0.85)
            bars.add(b)
            vals.add(txt(f"{v / 1000:.1f}", size=22).next_to(b, UP, buff=0.08))
            labs.add(txt(name, size=19, color=INK2).next_to(ax.c2p(k + 0.6, 0), DOWN, buff=0.15))
            base += v
        g_bar = bar_at(ax, 4.6, 0, gross / 1000, 1.05, INK2, 0.9)
        g_val = txt(f"{gross / 1000:.1f}", size=24, weight="SEMIBOLD").next_to(g_bar, UP, buff=0.08)
        g_lab = txt("Gross", size=19, color=INK2).next_to(ax.c2p(4.6, 0), DOWN, buff=0.15)
        i_bar = bar_at(ax, 5.6, net / 1000, gross / 1000, 1.05, ORANGE, 0.9)
        i_val = txt(f"−{inc / 1000:.1f}", size=22, color=ORANGE).next_to(i_bar, UP, buff=0.08)
        i_lab = txt("Client\nincentives", size=19, color=INK2).next_to(ax.c2p(5.6, 0), DOWN, buff=0.15)
        n_bar = bar_at(ax, 6.6, 0, net / 1000, 1.05, BLUE, 1)
        n_val = txt(f"{net / 1000:.1f}", size=26, color=BLUE, weight="BOLD").next_to(n_bar, UP, buff=0.08)
        n_lab = txt("Net", size=19, color=INK2).next_to(ax.c2p(6.6, 0), DOWN, buff=0.15)
        with self.say("gross") as d:
            self.play(FadeIn(h), Create(ax), FadeIn(ax.extras), run_time=0.7)
            self.play(LaggedStart(*[AnimationGroup(GrowFromEdge(b, DOWN), FadeIn(v), FadeIn(l))
                                    for b, v, l in zip(bars, vals, labs)], lag_ratio=0.45), run_time=2.0)
            self.play(GrowFromEdge(g_bar, DOWN), FadeIn(g_val), FadeIn(g_lab), run_time=0.7)
        drv1 = txt("× volume", size=19, color=AQUA).next_to(vals[0], UP, buff=0.12)
        drv2 = txt("× transactions", size=19, color=AQUA).next_to(vals[1], UP, buff=0.12)
        with self.say("lines1") as d:
            self.play(bars[0].animate.set_fill(AQUA, 1), FadeIn(drv1), run_time=0.5)
            self.at(d * 0.45, bars[1].animate.set_fill(AQUA, 1), FadeIn(drv2), run_time=0.5)
        drv3 = txt("cross-border, FX", size=19, color=AQUA).next_to(vals[2], UP, buff=0.12)
        drv4 = txt("licensing,\nservices", size=18, color=AQUA).next_to(vals[3], UP, buff=0.12)
        with self.say("lines2") as d:
            self.play(bars[:2].animate.set_fill(BLUE, 0.85), FadeOut(drv1), FadeOut(drv2),
                      bars[2].animate.set_fill(AQUA, 1), FadeIn(drv3), run_time=0.6)
            self.at(d * 0.68, bars[2].animate.set_fill(BLUE, 0.85), FadeOut(drv3),
                    bars[3].animate.set_fill(AQUA, 1), FadeIn(drv4), run_time=0.5)
        note = VGroup(txt(f"{inc / gross:.1%} of gross", size=20, color=ORANGE)).next_to(i_val, UP, buff=0.1)
        with self.say("net") as d:
            self.play(bars[3].animate.set_fill(BLUE, 0.85), FadeOut(drv4), run_time=0.3)
            self.play(GrowFromEdge(i_bar, UP), FadeIn(i_val), FadeIn(i_lab), FadeIn(note), run_time=0.9)
            self.at(d * 0.62, GrowFromEdge(n_bar, DOWN), FadeIn(n_val), FadeIn(n_lab), run_time=0.8)
            self.play(FadeIn(tag("F").next_to(n_val, RIGHT, buff=0.12)), run_time=0.3)
        self.clear()

        # ---------------------------------------------------------- traffic x toll
        h = heading("Traffic × toll")
        eq = tex(r"\text{Revenue} \;\approx\; \underbrace{Q}_{\text{transactions}} \times \underbrace{p}_{\text{toll per transaction}}", size=46)
        eq.next_to(h, DOWN, buff=0.6).set_x(0)
        with self.say("toll1"):
            self.play(FadeIn(h), run_time=0.4)
            self.play(Write(eq), run_time=1.6)
        tx = f.loc[2025, "processed_transactions"]
        rpt = f.loc[2025, "revenue_per_transaction_usd"] * 100
        calc = VGroup(tex(rf"Q = {tx:.1f}\ \text{{bn}}", size=40),
                      tex(rf"p = \frac{{\$40.0\ \text{{bn}}}}{{{tx:.1f}\ \text{{bn}}}} \approx {rpt:.1f}\ \text{{cents}}", size=40))
        calc.arrange(RIGHT, buff=1.2).next_to(eq, DOWN, buff=0.55)
        calc_t = tag("E").next_to(calc, RIGHT, buff=0.2)
        with self.say("toll2"):
            self.play(FadeIn(calc[0]), run_time=0.6)
            self.play(FadeIn(calc[1]), FadeIn(calc_t), run_time=0.8)
        # two small charts: transactions and toll
        yrs = list(range(2016, 2026))
        q = [f.loc[y_, "processed_transactions"] for y_ in yrs]
        p = [f.loc[y_, "revenue_per_transaction_usd"] * 100 for y_ in yrs]
        ax1 = axes([2015.4, 2025.6, 1], [0, 300, 100], 5.4, 2.4, y_ticks=[0, 100, 200, 300], y_fmt=str)
        ax2 = axes([2015.4, 2025.6, 1], [0, 20, 5], 5.4, 2.4, y_ticks=[0, 10, 20], y_fmt=lambda v: f"{v}¢")
        ax1.move_to([-3.3, -2.1, 0])
        ax2.move_to([3.9, -2.1, 0])
        bars1 = VGroup(*[bar_at(ax1, y_, 0, v, 0.36, BLUE) for y_, v in zip(yrs, q)])
        line2 = line_through(ax2, yrs, p, color=AQUA, width=5)
        t1 = txt("Transactions, bn", size=20, color=INK2).next_to(ax1, UP, buff=0.12)
        t2 = txt("Net revenue per transaction", size=20, color=INK2).next_to(ax2, UP, buff=0.12)
        e1 = VGroup(txt("2016", size=17, color=MUTED).next_to(ax1.c2p(2016, 0), DOWN, buff=0.1),
                    txt("2025", size=17, color=MUTED).next_to(ax1.c2p(2025, 0), DOWN, buff=0.1))
        e2 = VGroup(txt("2016", size=17, color=MUTED).next_to(ax2.c2p(2016, 0), DOWN, buff=0.1),
                    txt("2025", size=17, color=MUTED).next_to(ax2.c2p(2025, 0), DOWN, buff=0.1))
        v1 = VGroup(txt(f"{q[0]:.0f}", size=18).next_to(bars1[0], UP, buff=0.05),
                    txt(f"{q[-1]:.0f}", size=18).next_to(bars1[-1], UP, buff=0.05))
        v2 = VGroup(txt(f"{p[0]:.1f}¢", size=18, color=AQUA).next_to(ax2.c2p(2016, p[0]), UP, buff=0.08).shift(0.3 * RIGHT),
                    txt(f"{p[-1]:.1f}¢", size=18, color=AQUA).next_to(ax2.c2p(2025, p[-1]), UP, buff=0.08))
        with self.say("toll3") as d:
            self.play(VGroup(eq, calc, calc_t).animate.scale(0.75).next_to(h, DOWN, buff=0.35).set_x(0), run_time=0.6)
            self.play(Create(ax1), FadeIn(ax1.extras), FadeIn(t1), FadeIn(e1),
                      Create(ax2), FadeIn(ax2.extras), FadeIn(t2), FadeIn(e2), run_time=0.7)
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars1], lag_ratio=0.15), FadeIn(v1), run_time=1.6)
            self.play(Create(line2), FadeIn(v2), run_time=1.4)
        self.clear()

        # ---------------------------------------------------------- not a lender
        h = heading("A network, not a lender")
        colA = VGroup(txt("Your bank (issuer)", size=30, color=ORANGE, weight="SEMIBOLD"),
                      bullets(["lends the money", "sets the interest rate", "takes the credit losses"], size=26,
                              dot_color=ORANGE)).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        colB = VGroup(txt("Visa", size=30, color=BLUE, weight="SEMIBOLD"),
                      bullets(["no loan book", "no credit losses", "earns on spending, not interest"], size=26,
                              dot_color=BLUE)).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        cols = VGroup(colA, colB).arrange(RIGHT, buff=1.6, aligned_edge=UP).next_to(h, DOWN, buff=0.6).set_x(0)
        colB[1].align_to(colA[1], UP)
        with self.say("lender") as d:
            self.play(FadeIn(h), run_time=0.4)
            self.play(FadeIn(colA, shift=0.1 * RIGHT), run_time=0.8)
            self.at(d * 0.62, FadeIn(colB, shift=0.1 * RIGHT), run_time=0.8)
        card = VGroup(txt("Settlement guarantee, fiscal 2025", size=26, weight="SEMIBOLD"),
                      VGroup(stat("$153.4bn", "peak daily exposure", ORANGE, vsize=40, lsize=20),
                             stat("$8.8bn", "collateral held", AQUA, vsize=40, lsize=20),
                             stat("minimal", "historical losses (Visa)", INK, vsize=40, lsize=20)).arrange(RIGHT, buff=0.9))
        card.arrange(DOWN, buff=0.35)
        card = boxed(card, color=FAINT, buff=0.3)
        card.add(tag("F").next_to(card, UR, buff=-0.45))
        card.to_edge(DOWN, buff=0.45)
        with self.say("settle"):
            self.play(FadeIn(card, shift=0.15 * UP), run_time=0.8)
        self.finish()
