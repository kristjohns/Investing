"""Look and feel shared by every chapter: palette, type, small building blocks, and the
Chapter base class that ties animations to the narration clips.

Timing model: `with self.say(key) as d:` starts that narration line, runs whatever is
animated inside the block, then waits until the clip (plus a short pause) is over.
The start time of every line is written to build/timeline/<chapter>.json, which
build.py uses to lay the audio and subtitles under the rendered video.
"""
import json
from contextlib import contextmanager
from pathlib import Path

import numpy as np
from manim import (DOWN, LEFT, ORIGIN, RIGHT, UP, Axes, Create, DashedLine, FadeIn, FadeOut, Line,
                   MarkupText, MathTex, Rectangle, RoundedRectangle, Scene, Text, VGroup, config)

from narration import chapters

HERE = Path(__file__).resolve().parent
BUILD = HERE / "build"
TIMELINE = BUILD / "timeline"

# ---------------------------------------------------------------- palette (dark theme)
BG = "#1a1a19"
INK = "#f0efec"
INK2 = "#c3c2b7"
MUTED = "#898781"
FAINT = "#5a5954"
GRID = "#2e2e2b"
PANEL = "#232321"
BLUE = "#3987e5"
ORANGE = "#d95926"
AQUA = "#199e70"
YELLOW = "#c98500"
MAGENTA = "#d55181"
VIOLET = "#9085e9"
RED = "#e66767"
GREEN = "#2fa84f"
TAG_COLORS = {"F": "#256abf", "E": "#199e70", "J": "#c98500"}
TAG_NAMES = {"F": "Fact", "E": "Estimate", "J": "Judgment"}

FONT = "Inter"
config.background_color = BG

# frame: 14.22 x 8 units; content sits between y = -3.5 and the heading at y = 3.0
LEFT_X = -6.55
TOP_Y = 3.05


# ---------------------------------------------------------------- text helpers
def txt(s, size=28, color=INK, weight="NORMAL", **kw):
    return Text(s, font=FONT, font_size=size, color=color, weight=weight, **kw)


def mtxt(s, size=28, color=INK, **kw):
    """Pango markup, e.g. '<span foreground="#3987e5">$40.0bn</span>'."""
    return MarkupText(s, font=FONT, font_size=size, color=color, **kw)


def hl(s, color=BLUE, bold=True):
    w = ' font_weight="bold"' if bold else ""
    return f'<span foreground="{color}"{w}>{s}</span>'


def tex(*parts, size=44, color=INK, **kw):
    return MathTex(*parts, font_size=size, color=color, **kw)


def heading(s, size=40):
    h = txt(s, size=size, weight="SEMIBOLD")
    h.move_to([LEFT_X, TOP_Y, 0], aligned_edge=LEFT)
    return h


def tag(kind, scale=1.0):
    """Coloured F / E / J badge as in the report."""
    box = RoundedRectangle(corner_radius=0.07, width=0.36 * scale, height=0.36 * scale,
                           fill_color=TAG_COLORS[kind], fill_opacity=1, stroke_width=0)
    letter = txt(kind, size=int(20 * scale), weight="BOLD").move_to(box)
    return VGroup(box, letter)


def tagged(mob, kind, buff=0.15, direction=RIGHT):
    t = tag(kind).next_to(mob, direction, buff=buff)
    return VGroup(mob, t)


def panel(width, height, color=PANEL, stroke=None, radius=0.12):
    return RoundedRectangle(corner_radius=radius, width=width, height=height, fill_color=color,
                            fill_opacity=1, stroke_color=stroke or color, stroke_width=2 if stroke else 0)


def boxed(mob, color=BLUE, buff=0.25, fill=PANEL, radius=0.12, stroke_width=2):
    r = RoundedRectangle(corner_radius=radius, width=mob.width + 2 * buff, height=mob.height + 2 * buff,
                         fill_color=fill, fill_opacity=1, stroke_color=color, stroke_width=stroke_width)
    r.move_to(mob)
    return VGroup(r, mob)


def chip(s, color=BLUE, size=22):
    t = txt(s, size=size, color=INK)
    r = RoundedRectangle(corner_radius=0.18, width=t.width + 0.4, height=t.height + 0.28,
                         fill_color=color, fill_opacity=0.18, stroke_color=color, stroke_width=1.5)
    r.move_to(t)
    return VGroup(r, t)


def stat(value, label, color=BLUE, vsize=54, lsize=22, kind=None):
    v = txt(value, size=vsize, color=color, weight="BOLD")
    l = txt(label, size=lsize, color=INK2)
    g = VGroup(v, l).arrange(DOWN, buff=0.14)
    if kind:
        g.add(tag(kind).next_to(v, RIGHT, buff=0.15))
    return g


def bullets(items, size=28, color=INK, dot_color=BLUE, buff=0.32, width=None):
    rows = []
    for it in items:
        t = it if not isinstance(it, str) else txt(it, size=size, color=color)
        if width and t.width > width:
            t.scale_to_fit_width(width)
        d = RoundedRectangle(corner_radius=0.04, width=0.13, height=0.13, fill_color=dot_color,
                             fill_opacity=1, stroke_width=0)
        d.next_to(t, LEFT, buff=0.22).align_to(t, UP).shift(0.11 * DOWN)
        rows.append(VGroup(d, t))
    return VGroup(*rows).arrange(DOWN, aligned_edge=LEFT, buff=buff)


def ordinal(n):
    n = int(n)
    suf = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suf}"


# ---------------------------------------------------------------- charts
def fmt_pct(x, d=1):
    return f"{x * 100:.{d}f}%"


class ChartAxes(Axes):
    """Axes whose tick labels and gridlines (`extras`, kept separate so they can fade in
    on their own) follow every move of the axes."""

    def shift(self, *vectors):
        super().shift(*vectors)
        if getattr(self, "extras", None) is not None:
            self.extras.shift(*vectors)
        return self


def axes(x_range, y_range, x_length, y_length, y_ticks=None, y_fmt=str, x_ticks=None, x_fmt=str,
         grid=True, label_size=18):
    """Plain axes with Inter tick labels and faint horizontal gridlines."""
    ax = ChartAxes(x_range=x_range, y_range=y_range, x_length=x_length, y_length=y_length, tips=False,
                   axis_config={"color": FAINT, "stroke_width": 2, "include_ticks": False})
    extras = VGroup()
    # Manim draws the y-axis through x = 0 when 0 is inside the x-range; put the labels there too
    x_at = 0 if x_range[0] < 0 < x_range[1] else x_range[0]
    for y in (y_ticks or []):
        p = ax.c2p(x_at, y)
        if grid and y != y_range[0]:
            extras.add(Line(ax.c2p(x_range[0], y), ax.c2p(x_range[1], y), color=GRID, stroke_width=1.5))
        extras.add(txt(y_fmt(y), size=label_size, color=MUTED).next_to(p, LEFT, buff=0.12))
    for x in (x_ticks or []):
        p = ax.c2p(x, y_range[0])
        extras.add(txt(x_fmt(x), size=label_size, color=MUTED).next_to(p, DOWN, buff=0.12))
    ax.extras = extras
    return ax


def line_through(ax, xs, ys, color=BLUE, width=4):
    pts = [ax.c2p(x, y) for x, y in zip(xs, ys)]
    from manim import VMobject
    m = VMobject(stroke_color=color, stroke_width=width)
    m.set_points_as_corners(pts)
    return m


def bar_at(ax, x, y0, y1, width, color, opacity=1.0):
    """A bar between y0 and y1 at x (data coordinates); width in scene units."""
    lo, hi = ax.c2p(x, min(y0, y1)), ax.c2p(x, max(y0, y1))
    h = max(hi[1] - lo[1], 1e-3)
    r = Rectangle(width=width, height=h, fill_color=color, fill_opacity=opacity, stroke_width=0)
    r.move_to([lo[0], lo[1] + h / 2, 0])
    return r


def dashed(a, b, color=MUTED, width=2, dash=0.08):
    return DashedLine(a, b, color=color, stroke_width=width, dash_length=dash)


# ---------------------------------------------------------------- base scene
_CHAPTERS = {k: (i, title, lines) for i, k, title, lines in chapters()}


class Chapter(Scene):
    KEY = ""
    CONCEPTS: list[str] = []
    PAD = 0.32         # pause after each narration line

    def setup(self):
        self.num, self.title_text, lines = _CHAPTERS[self.KEY]
        self.expected = [k for k, _ in lines]
        self.durations = json.loads((BUILD / "durations.json").read_text())
        self.timeline = []
        self.tag_mob = None

    # -- narration sync
    @contextmanager
    def say(self, key, pad=None):
        i = len(self.timeline)
        assert i < len(self.expected) and self.expected[i] == key, \
            f"{self.KEY}: expected line {self.expected[i] if i < len(self.expected) else None!r}, got {key!r}"
        d = self.durations[f"{self.KEY}/{key}"]["duration"]
        start = self.renderer.time
        self.timeline.append({"key": key, "start": start, "duration": d})
        yield d
        rest = d + (self.PAD if pad is None else pad) - (self.renderer.time - start)
        if rest > 1 / config.frame_rate:
            self.wait(rest)

    def at(self, t, *anims, run_time=0.6):
        """Play `anims` starting t seconds after the current narration line began."""
        target = self.timeline[-1]["start"] + t
        now = self.renderer.time
        if target - now > 1 / config.frame_rate:
            self.wait(target - now)
        if anims:
            self.play(*anims, run_time=run_time)

    def gap(self, t=0.4):
        self.wait(t)

    # -- furniture
    def chapter_tag(self):
        label = "Introduction" if self.num == 0 else f"{self.num:02d}  {self.title_text}"
        t = txt(label, size=19, color=MUTED).to_corner(LEFT + UP, buff=0.32)
        dots = VGroup(*[RoundedRectangle(corner_radius=0.03, width=0.22, height=0.06, stroke_width=0,
                                         fill_color=BLUE if j == self.num else FAINT,
                                         fill_opacity=1 if j <= self.num else 0.6)
                        for j in range(len(_CHAPTERS))]).arrange(RIGHT, buff=0.06)
        dots.to_corner(RIGHT + UP, buff=0.36)
        return VGroup(t, dots)

    def title_card(self):
        """Chapter opener, played over the 'title' narration line."""
        num = txt(f"{self.num:02d}", size=120, color=FAINT, weight="BOLD")
        title = txt(self.title_text, size=58, weight="BOLD")
        if title.width > 11.6:
            title.scale_to_fit_width(11.6)
        bar = Rectangle(width=1.6, height=0.08, fill_color=BLUE, fill_opacity=1, stroke_width=0)
        group = VGroup(num, title, bar).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        if self.CONCEPTS:
            c = VGroup(*[chip(x, color=VIOLET, size=22) for x in self.CONCEPTS]).arrange(RIGHT, buff=0.18)
            if c.width > 12.4:
                c.scale_to_fit_width(12.4)
            lab = txt("Concepts in this chapter", size=20, color=MUTED)
            cg = VGroup(lab, c).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
            group = VGroup(group, cg).arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        group.move_to(ORIGIN).to_edge(LEFT, buff=1.2)
        self.tag_mob = self.chapter_tag()
        with self.say("title") as d:
            self.play(FadeIn(num, shift=0.2 * UP), FadeIn(title, shift=0.2 * UP), Create(bar), run_time=0.8)
            if self.CONCEPTS:
                self.play(FadeIn(group[1], shift=0.1 * UP), run_time=0.6)
        self.wait(0.5)
        self.play(FadeOut(group), FadeIn(self.tag_mob), run_time=0.6)

    def clear(self, run_time=0.5, keep=()):
        mobs = [m for m in self.mobjects if m is not self.tag_mob and m not in keep]
        if mobs:
            self.play(*[FadeOut(m) for m in mobs], run_time=run_time)

    def finish(self):
        assert [x["key"] for x in self.timeline] == self.expected, \
            f"{self.KEY}: unused lines {self.expected[len(self.timeline):]}"
        self.wait(0.4)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.6)
        self.wait(0.2)
        out = TIMELINE / f"{config.pixel_height}p{int(config.frame_rate)}"
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{self.KEY}.json").write_text(json.dumps(
            {"chapter": self.KEY, "index": self.num, "title": self.title_text,
             "fps": config.frame_rate, "duration": self.renderer.time, "lines": self.timeline}, indent=1))
