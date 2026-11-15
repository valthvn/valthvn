#!/usr/bin/env python3
"""Session 006: the profile as a painting, after the portfolio (Starry Night Over the Rhône)."""
import datetime as dt
import html
import json
import math
import random
import textwrap
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'assets/session'
# Set to the deployed portfolio address to make the painting a link; None leaves it unlinked.
PORTFOLIO_URL = None
PROJECTS = [
    {'repo': 'GoodByeFirewall', 'name': 'GoodByeFirewall', 'place': 'The bridge', 'lang': 'JavaScript',
     'text': 'Fork of GoodByeDPI: gets past deep packet inspection and network restrictions.'},
    {'repo': 'Mint', 'name': 'Mint', 'place': 'The reflection', 'lang': 'C#',
     'text': 'Lightweight Windows tray app: watches the CPU and cools it in one click through power plans.'},
    {'repo': 'trouve-ton-theatre-nantes', 'name': 'Trouve ton théâtre Nantes', 'place': 'The lights of Arles', 'lang': 'JavaScript',
     'text': 'Plays in and around Nantes: programme, map of venues and posters.'},
    {'repo': 'SkyHands', 'name': 'SkyHands', 'place': 'The strollers', 'lang': 'Java',
     'text': 'Hypixel Skyblock mod to customise first-person hands and combat animations.'},
    {'repo': 'dsh-local-voice', 'name': 'dsh-local-voice', 'place': 'The boat', 'lang': 'JavaScript',
     'text': 'Local, offline, multi-model voice input for DeepSeek Harness.'},
    {'repo': 'animated-terminal-profile', 'name': 'animated-terminal-profile', 'place': 'The Great Bear', 'lang': 'Python',
     'text': 'Terminal-style animated GitHub profile README generator.'},
]

INK, PAPER, MUTED, OCHRE = '#1b2440', '#fbf9f4', '#4a5068', '#b9731a'
EDGE, CHIP_INK = '#d8d2c4', '#10224f'
# On GitHub's dark theme a cream label glares against the black page: the labels become night-blue
# panels with a gold fillet, like the project panels inside the portfolio's painting.
DARK = {PAPER: '#0d1c47', EDGE: '#c79a3e', INK: '#f6d66b', MUTED: '#d3dbe8', OCHRE: '#8fd0c4'}
THEMED = ['tableau'] + [f'cartel-{i:02d}' for i in range(1, 7)]
SERIF = "Georgia, 'Times New Roman', serif"
# The Great Bear, as placed in the portfolio: x from -1 to 1, y from 0 (horizon) to 1, size.
STARS = [(-0.62, 0.62, 1.0), (-0.4, 0.8, 1.1), (-0.17, 0.77, 1.0), (0.05, 0.65, 1.15), (0.1, 0.44, 1.0),
         (0.42, 0.5, 1.2), (0.45, 0.74, 1.05), (-0.86, 0.86, 0.8), (-0.76, 0.3, 0.7), (0.76, 0.9, 0.8),
         (0.82, 0.33, 0.75), (-0.22, 0.36, 0.6), (0.28, 0.93, 0.7), (-0.5, 0.4, 0.6)]
STYLE = ('<style>@keyframes tw{0%,100%{opacity:1}50%{opacity:.4}}'
         '@keyframes sh{0%,100%{opacity:.95;transform:translateX(0)}50%{opacity:.55;transform:translateX(1.6px)}}'
         '.tw{animation:tw 3.4s ease-in-out infinite}.sh{animation:sh 2.8s ease-in-out infinite}'
         '@media (prefers-reduced-motion:reduce){.tw,.sh{animation:none}}</style>')


def n(value):
    """Short number formatting keeps the generated files small."""
    return f'{value:.1f}'.rstrip('0').rstrip('.')


def mix(a, b, t):
    ca, cb = (int(a[i:i+2], 16) for i in (1, 3, 5)), (int(b[i:i+2], 16) for i in (1, 3, 5))
    return '#' + ''.join(f'{max(0, min(255, round(x + (y - x) * t))):02x}' for x, y in zip(ca, cb))


def text(x, y, value, size=14, fill=INK, weight=400, style='normal', anchor='start', extra=''):
    return (f'<text x="{n(x)}" y="{n(y)}" font-family="{SERIF}" font-size="{size}" font-weight="{weight}" '
            f'font-style="{style}" text-anchor="{anchor}" fill="{fill}"{extra}>{html.escape(str(value))}</text>')


def svg(w, h, title, description, body):
    result = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
              f'role="img" aria-labelledby="title desc"><title id="title">{html.escape(title)}</title>'
              f'<desc id="desc">{html.escape(description)}</desc>{STYLE}{body}</svg>\n')
    ET.fromstring(result)
    return result


def normalize_days(data):
    """A 365-day window ending at the last actual date, not the machine clock."""
    raw = data['days']
    if not raw:
        raise ValueError('Contribution data must contain days')
    lookup = {}
    for row in raw:
        date = dt.date.fromisoformat(row['date'])
        count = row['count']
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            raise ValueError('Contribution counts must be nonnegative integers')
        if date in lookup:
            raise ValueError('Duplicate contribution dates')
        lookup[date] = count
    end = max(lookup)
    start = end - dt.timedelta(days=364)
    # Missing dates within the observed window are errors, never fake zeroes.
    return [{'date': start + dt.timedelta(days=i), 'count': lookup[start + dt.timedelta(days=i)]}
            for i in range(365)]


# ---------------------------------------------------------------- painting

def strokes(rng, x0, y0, x1, y1, step, length, colour, sway=0.0, width=5):
    """Rows of short brush strokes; `colour(tx, ty, rng)` picks each one, `sway` bends the rows."""
    out = [f'<g fill="none" stroke-linecap="round" stroke-width="{width}">']
    y = y0 + step/2
    while y < y1:
        x = x0 - rng.uniform(0, length[1])
        while x < x1:
            l = rng.uniform(*length)
            ang = math.radians(sway * math.sin(x/70 + y/38) + rng.uniform(-5, 5))
            yy = y + sway * 0.35 * math.sin(x/55 + y/30)
            out.append(f'<path d="M{n(x)} {n(yy)}l{n(l*math.cos(ang))} {n(l*math.sin(ang))}" '
                       f'stroke="{colour((x - x0)/(x1 - x0), (y - y0)/(y1 - y0), rng)}"/>')
            x += l + rng.uniform(2, 5)
        y += step
    out.append('</g>')
    return ''.join(out)


def sky_colour(tx, ty, rng):
    base = mix('#0a2257', '#2f8091', ty ** 1.4)
    r = rng.random()
    if r < 0.16:
        return mix(base, '#3aa0a2', 0.6)
    if r < 0.3:
        return mix(base, '#050f3a', 0.6)
    return mix(base, '#ffffff' if rng.random() < 0.5 else '#000000', rng.uniform(0, 0.16))


def water_colour(tx, ty, rng):
    base = mix('#16528c', '#0b2a66', ty)
    r = rng.random()
    if r < 0.14:
        return mix(base, '#3a9ba6', 0.55)
    if r < 0.34:
        return mix(base, '#040c34', 0.6)
    return mix(base, '#ffffff' if rng.random() < 0.5 else '#000000', rng.uniform(0, 0.14))


def bank_colour(tx, ty, rng):
    return mix(mix('#0d1a22', '#2b2a17', rng.random()), '#000000', rng.uniform(0, 0.25))


def star(x, y, size, index, rng):
    r = 7.5 * size
    rays = ''.join(
        f'<path d="M{n(x + math.cos(a)*r*0.42)} {n(y + math.sin(a)*r*0.42)}L{n(x + math.cos(a)*r*rng.uniform(0.85, 1.15))} '
        f'{n(y + math.sin(a)*r*rng.uniform(0.85, 1.15))}" stroke="{"#bfe6c4" if i % 2 else "#f6f3c0"}"/>'
        for i, a in enumerate(k * math.tau / 10 + rng.uniform(-0.12, 0.12) for k in range(10)))
    return (f'<g class="tw" style="animation-delay:{n(-index*0.47)}s" fill="none" stroke-linecap="round" stroke-width="{n(1.7*size)}">'
            f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r*1.75)}" stroke="#4fa8aa" stroke-opacity=".4" stroke-dasharray="6 5" stroke-width="{n(2.4*size)}"/>'
            f'{rays}<circle cx="{n(x)}" cy="{n(y)}" r="{n(r*0.36)}" fill="#fffbe0" stroke="none"/></g>')


def lamp(x, y, r, index, rng):
    rays = ''.join(f'<path d="M{n(x + math.cos(a)*r*1.3)} {n(y + math.sin(a)*r*1.3)}L{n(x + math.cos(a)*r*2.5)} {n(y + math.sin(a)*r*2.5)}"/>'
                   for a in (k * math.tau / 8 + 0.2 for k in range(8)))
    return (f'<g class="tw" style="animation-delay:{n(-index*0.31)}s"><g stroke="#f0a020" stroke-width="{n(max(0.8, r*0.45))}" '
            f'stroke-linecap="round" fill="none">{rays}</g><circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="#ffd866"/></g>')


def reflection(x, y, length, width, index, rng):
    """A broken column of gold strokes falling from a light towards the viewer."""
    out = [f'<g class="sh" style="animation-delay:{n(-index*0.37)}s" fill="none" stroke-linecap="round">']
    k, yy = 0, y
    while yy < y + length:
        fade = 1 - (yy - y)/length
        w = width * (0.7 + 0.9 * (yy - y)/length) * rng.uniform(0.6, 1.1)
        out.append(f'<path d="M{n(x - w/2 + rng.uniform(-1.5, 1.5))} {n(yy)}h{n(w)}" stroke="{"#ffd866" if k % 3 == 0 else "#f0a020"}" '
                   f'stroke-width="{n(1.4 + 1.6*fade)}" stroke-opacity="{n(0.35 + 0.65*fade)}"/>')
        yy += rng.uniform(3.4, 5.2)
        k += 1
    out.append('</g>')
    return ''.join(out)


def skyline(rng, w, base, tall):
    points, x = [f'0 {n(base)}'], 0
    while x < w:
        hgt = rng.uniform(0.35, 1.0) * tall * (2.1 if rng.random() < 0.05 else 1)
        bw = rng.uniform(7, 19)
        points += [f'{n(x)} {n(base - hgt)}', f'{n(min(w, x + bw))} {n(base - hgt)}']
        x += bw
    points.append(f'{n(w)} {n(base)}')
    return f'<polygon points="{" ".join(points)}" fill="#081637"/>'


def night(w, h, seed, clip_id, decor=True, star_scale=None):
    """The painted scene, in local coordinates: static brushwork (filtered), then the living lights."""
    rng = random.Random(seed)
    hz = h * 0.46
    static = [f'<rect width="{w}" height="{n(hz)}" fill="#12386f"/><rect y="{n(hz)}" width="{w}" height="{n(h - hz)}" fill="#0f3a7a"/>',
              strokes(rng, 0, 0, w, hz, 7, (11, 24), sky_colour, sway=11),
              strokes(rng, 0, hz, w, h, 6.2, (13, 30), water_colour, sway=1.5, width=4.4),
              skyline(rng, w, hz + 1, h * 0.035)]
    # Lit windows of the far town.
    static.append(''.join(f'<rect x="{n(rng.uniform(0, w))}" y="{n(hz - rng.uniform(2, h*0.022))}" width="1.6" height="1.6" fill="#f0b040"/>'
                          for _ in range(int(w/14))))
    # The near bank, with the two moored boats and the strollers.
    bank = f'M{n(w*0.4)} {h}C{n(w*0.5)} {n(h*0.9)} {n(w*0.62)} {n(h*0.87)} {n(w*0.74)} {n(h*0.855)}S{n(w*0.95)} {n(h*0.83)} {w} {n(h*0.83)}V{h}Z'
    static.append(f'<clipPath id="{clip_id}-bank"><path d="{bank}"/></clipPath><path d="{bank}" fill="#0e1b22"/>'
                  f'<g clip-path="url(#{clip_id}-bank)">{strokes(rng, w*0.4, h*0.82, w, h, 5.5, (9, 20), bank_colour, sway=3, width=4)}</g>')
    for bx, by, s in ((w*0.2, h*0.865, 1.0), (w*0.31, h*0.93, 1.15)) if decor else ():
        l = w * 0.085 * s
        static.append(f'<path d="M{n(bx - l)} {n(by)}q{n(l)} {n(-l*0.16)} {n(2*l)} {n(-l*0.05)}q{n(-l*0.9)} {n(l*0.3)} {n(-2*l)} {n(l*0.05)}z" '
                      f'fill="#070d1c" stroke="#4a3618" stroke-width="1.6"/>')
    cx, cy, u = w * 0.8, h * 0.848, h / 412
    static.append(f'<g transform="translate({n(cx)} {n(cy)}) scale({n(u)})">'
                  '<path d="M-7-22h8l3 24h-13z" fill="#0b1640"/><circle cx="-3" cy="-25.5" r="3" fill="#a9824f"/>'
                  '<path d="M-8.5-27.6h11" stroke="#c9a23c" stroke-width="2" stroke-linecap="round"/>'
                  '<path d="M6-19h5l5 21h-14z" fill="#1c6a62"/><path d="M5.5-19h6l1 7h-8z" fill="#9a4a1c"/>'
                  '<circle cx="8.5" cy="-22.5" r="2.8" fill="#a9824f"/></g>')
    live = []
    lamps = [w * (0.06 + 0.88 * i / 9) + rng.uniform(-w*0.02, w*0.02) for i in range(10)]
    for i, lx in enumerate(lamps if decor else ()):
        live.append(reflection(lx, hz + 4, h * rng.uniform(0.2, 0.3), w * 0.02, i, rng))
        live.append(lamp(lx, hz - 2, 2.2 + rng.uniform(0, 1), i, rng))
    for i, (sx, sy, size) in enumerate(STARS):
        live.append(star(w/2 + sx * w * 0.47, hz * (0.97 - sy * 0.9), size * (star_scale or w / 560), i, rng))
    return (f'<filter id="{clip_id}-brush" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".035" '
            f'numOctaves="2" seed="3"/><feDisplacementMap in="SourceGraphic" scale="5"/></filter>'
            f'<clipPath id="{clip_id}"><rect width="{w}" height="{h}"/></clipPath>'
            f'<g clip-path="url(#{clip_id})"><g filter="url(#{clip_id}-brush)">{"".join(static)}</g>{"".join(live)}</g>'), lamps, hz


# ---------------------------------------------------------------- gilded frame

def frame(x, y, w, h, th=46):
    """A baroque gilded frame: carved outer band, smooth hollow, beaded liner."""
    out = ['<linearGradient id="gold" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#8a6420"/><stop offset=".25" stop-color="#f3d57a"/>'
           '<stop offset=".5" stop-color="#c79a3e"/><stop offset=".75" stop-color="#fbe8a0"/><stop offset="1" stop-color="#9a6f22"/></linearGradient>',
           f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#gold)"/>',
           f'<rect x="{x + 2.5}" y="{y + 2.5}" width="{w - 5}" height="{h - 5}" fill="none" stroke="#6b4a14" stroke-width="1.2"/>',
           f'<rect x="{x + 13}" y="{y + 13}" width="{w - 26}" height="{h - 26}" fill="none" stroke="#7a5416" stroke-opacity=".55" stroke-width="20"/>']
    motif = ('<path d="M-15 1c4-10 11-10 15 0s11 10 15 0" fill="none" stroke="#fbe8a0" stroke-width="2.6" stroke-linecap="round"/>'
             '<path d="M-15 1c4-10 11-10 15 0s11 10 15 0" fill="none" stroke="#5e400f" stroke-width=".8" transform="translate(0 2.2)"/>'
             '<ellipse cx="-8" cy="-5.5" rx="5.5" ry="2.3" fill="#f3d57a" transform="rotate(-32 -8 -5.5)"/>'
             '<ellipse cx="8" cy="6.5" rx="5.5" ry="2.3" fill="#f3d57a" transform="rotate(-32 8 6.5)"/>'
             '<ellipse cx="-2" cy="7" rx="3.6" ry="1.6" fill="#e2bd5c" transform="rotate(28 -2 7)"/>'
             '<ellipse cx="2" cy="-6" rx="3.6" ry="1.6" fill="#e2bd5c" transform="rotate(28 2 -6)"/>'
             '<circle r="2.4" cy="1" fill="#fff3c0"/>')
    def run(length):
        count = max(1, round((length - 2*th + 20) / 31))
        gap = (length - 2*th + 20) / count
        return [th - 10 + gap * (i + 0.5) for i in range(count)]
    for d in run(w):
        out.append(f'<g transform="translate({n(x + d)} {n(y + 13)})">{motif}</g><g transform="translate({n(x + d)} {n(y + h - 13)}) scale(1 -1)">{motif}</g>')
    for d in run(h):
        out.append(f'<g transform="translate({n(x + 13)} {n(y + d)}) rotate(-90)">{motif}</g>'
                   f'<g transform="translate({n(x + w - 13)} {n(y + d)}) rotate(90)">{motif}</g>')
    for cx, cy in ((x + 13, y + 13), (x + w - 13, y + 13), (x + 13, y + h - 13), (x + w - 13, y + h - 13)):
        petals = ''.join(f'<ellipse cx="{n(cx + math.cos(a)*6)}" cy="{n(cy + math.sin(a)*6)}" rx="4.6" ry="2.2" fill="#f3d57a" '
                         f'transform="rotate({n(math.degrees(a))} {n(cx + math.cos(a)*6)} {n(cy + math.sin(a)*6)})"/>' for a in (k*math.tau/8 for k in range(8)))
        out.append(f'<circle cx="{cx}" cy="{cy}" r="11.5" fill="#8a6420"/>{petals}<circle cx="{cx}" cy="{cy}" r="3" fill="#fff3c0"/>')
    # Cord fillets either side of the carved band, then the hollow: nested gold lines read as a concave slope.
    for inset, colour, sw in ((24.5, '#fbe8a0', 1.6), (26.5, '#6b4a14', 1.2), (29, '#b08a36', 3.4), (32.2, '#d9b257', 3.2),
                              (35.2, '#f3d57a', 3), (37.8, '#c79a3e', 2.4), (39.6, '#6b4a14', 1)):
        out.append(f'<rect x="{x + inset}" y="{y + inset}" width="{w - 2*inset}" height="{h - 2*inset}" fill="none" stroke="{colour}" stroke-width="{sw}"/>')
    # Beaded liner against the canvas.
    bi = th - 3.2
    out.append(f'<rect x="{x + bi}" y="{y + bi}" width="{w - 2*bi}" height="{h - 2*bi}" fill="none" stroke="#fbe8a0" stroke-width="2.6" '
               f'stroke-dasharray="0.1 5.2" stroke-linecap="round"/>')
    out.append(f'<rect x="{x + th - 0.6}" y="{y + th - 0.6}" width="{w - 2*th + 1.2}" height="{h - 2*th + 1.2}" fill="none" stroke="#3d2a08" stroke-width="1.2"/>')
    # Mitred corners.
    for (ax, ay), (bx, by) in (((x, y), (x + th, y + th)), ((x + w, y), (x + w - th, y + th)),
                               ((x, y + h), (x + th, y + h - th)), ((x + w, y + h), (x + w - th, y + h - th))):
        out.append(f'<path d="M{ax} {ay}L{bx} {by}" stroke="#5e400f" stroke-opacity=".5" stroke-width=".8"/>')
    return ''.join(out)


def label(x, y, w, h):
    return (f'<rect x="{x + 2}" y="{y + 3}" width="{w}" height="{h}" fill="#000000" fill-opacity=".16"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{PAPER}" stroke="{EDGE}"/>')


def hero():
    fx, fy, fw, fh, th = 20, 14, 650, 512, 46
    scene, _, _ = night(fw - 2*th, fh - 2*th, 1888, 'canvas')
    body = (f'<rect x="{fx + 5}" y="{fy + 9}" width="{fw}" height="{fh}" fill="#000000" fill-opacity=".18"/>'
            f'{frame(fx, fy, fw, fh, th)}<g transform="translate({fx + th} {fy + th})">{scene}</g>'
            + label(706, 330, 234, 168)
            + text(724, 372, 'valthvn', 32, weight=600)
            + text(724, 398, 'Portfolio, 2026', 18, style='italic')
            + text(724, 430, 'after Vincent van Gogh,', 13.5, MUTED)
            + text(724, 448, 'Starry Night Over the Rhône, 1888', 13.5, MUTED, style='italic')
            + text(724, 472, 'Vibe coder: web apps, tools and APIs.', 12.5, MUTED)
            + text(724, 488, 'Build. Learn. Iterate.', 12.5, OCHRE, style='italic'))
    return svg(960, 540, 'valthvn, a portfolio inside a painting',
               'A gilded baroque frame holds an animated night scene after Van Gogh: the Great Bear twinkles over the Rhône, '
               'the lights of Arles shimmer on the water, two strollers and two boats rest on the bank. A museum label reads: '
               'valthvn, Portfolio, 2026. Vibe coder: web apps, tools and APIs. Build. Learn. Iterate.', body)


def cartel(index, project):
    """A museum label: text only, on its own paper surface."""
    w, h, x = 470, 148, 26
    lines = textwrap.wrap(project['text'], 62)[:3]
    chip = 22 + len(project['lang']) * 7.4
    body = (label(4, 4, w - 10, h - 12)
            + text(x, 34, f'N° {index} · {project["place"].upper()}', 11, OCHRE, extra=' letter-spacing="1.6"')
            + text(x, 62, project['name'], 23, weight=600, style='italic')
            + ''.join(text(x, 84 + i * 17, line, 13.5, MUTED) for i, line in enumerate(lines))
            + f'<ellipse cx="{n(x + chip/2)}" cy="{h - 25}" rx="{n(chip/2)}" ry="10" fill="#e0a12c" transform="rotate(-2 {n(x + chip/2)} {h - 25})"/>'
            + text(x + chip/2, h - 20.8, project['lang'], 12, CHIP_INK, weight=600, anchor='middle')
            + text(w - 22, h - 20.8, 'open the repository →', 12.5, MUTED, style='italic', anchor='end'))
    return svg(w, h, f'{project["name"]}, museum label',
               f'Museum label number {index}, {project["place"]}: {project["name"]}. {project["text"]} Written in {project["lang"]}.', body)


def activity(data):
    """The lights of Arles: one light per day; its reflection is as long as that day's contributions."""
    days = normalize_days(data)
    window = days[-90:]
    w, h = 960, 300
    scene, _, hz = night(w, h, 90, 'river', decor=False, star_scale=0.8)
    peak = max(1, max(d['count'] for d in window))
    rng = random.Random(365)
    live, ticks = [], []
    for i, day in enumerate(window):
        x = 35 + i * 10
        if day['date'].day == 1 or i == 0:
            ticks.append(text(x, h - 44, day['date'].strftime('%b').upper(), 10, '#c9dcc9', extra=' letter-spacing="1.2"'))
        if not day['count']:
            continue
        share = day['count'] / peak
        live.append(f'<g data-day="{day["date"].isoformat()}" data-count="{day["count"]}">'
                    + reflection(x, hz + 4, 12 + 108 * share ** 0.6, 6.5, i, rng)
                    + lamp(x, hz - 2, 1.5 + 2.3 * math.sqrt(share), i, rng) + '</g>')
    year, recent = sum(d['count'] for d in days), sum(d['count'] for d in window)
    halo = ' stroke="#07122e" stroke-width="3.5" stroke-linejoin="round" paint-order="stroke"'
    body = (f'<clipPath id="panel"><rect width="{w}" height="{h}" rx="5"/></clipPath><g clip-path="url(#panel)">{scene}'
            # A darker band of water in the foreground carries the reading of the picture.
            f'<rect y="{h - 34}" width="{w}" height="34" fill="#07122e" fill-opacity=".82"/>{"".join(live)}{"".join(ticks)}</g>'
            + text(22, 34, 'The lights of Arles', 22, '#f6d66b', 600, 'italic', extra=halo)
            + text(22, 54, '90 days of contributions', 13, '#f3e7c0', style='italic', extra=halo)
            + text(22, h - 12, f'{year} contributions in 365 days · {recent} in the last 90 · each light is a day, '
                               f'its reflection that day’s contributions', 13, '#f3e7c0')
            + text(w - 22, h - 12, f'as of {window[-1]["date"].isoformat()}', 13, '#c9dcc9', style='italic', anchor='end'))
    return svg(w, h, 'The lights of Arles: 90 days of GitHub contributions',
               f'A painted night river. Along the far shore, one light per day with at least one contribution over the last 90 observed '
               f'days; each reflection is as long as that day’s contribution count. {year} contributions over 365 days, {recent} over the '
               f'last 90, as of {window[-1]["date"].isoformat()}.', body)


# ---------------------------------------------------------------- README

def readme():
    def image(name, alt, width='960'):
        img = f'<img src="./assets/session/{name}.svg" width="{width}" alt="{html.escape(alt)}">'
        if name not in THEMED:
            return img
        return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/session/{name}-dark.svg">'
                f'{img}</picture>')
    painting = image('tableau', 'valthvn. A gilded frame holds an animated night scene after Van Gogh’s Starry Night Over the Rhône. '
                                'Museum label: valthvn, Portfolio, 2026. Vibe coder: web apps, tools and APIs. Build. Learn. Iterate.')
    if PORTFOLIO_URL:
        painting = f'<a href="{PORTFOLIO_URL}">{painting}</a>'
    rows = []
    for i in range(0, len(PROJECTS), 2):
        rows.append(' '.join(f'<a href="https://github.com/valthvn/{p["repo"]}">'
                             + image(f'cartel-{i + j + 1:02d}', f'Open the {p["name"]} repository', '49%') + '</a>'
                             for j, p in enumerate(PROJECTS[i:i + 2])) + '<br>')
    return '<!-- VALTHVN / SESSION 006 -->\n\n' + painting + '\n\n' + '\n'.join(rows) + '''

<details>
<summary><em>The studio</em> — stack</summary>

```json
{
  "languages": ["Python", "TypeScript", "JavaScript"],
  "frontend": ["React", "Next.js", "Tailwind CSS"],
  "backend": ["FastAPI", "Node.js", "Express"],
  "tools": ["Docker", "Git", "Linux", "GitHub Actions"]
}
```

</details>

<br>

''' + image('activity', 'The lights of Arles: a painted night river where each light on the far shore is one of the last 90 days, '
                        'and each reflection is as long as that day’s real GitHub contribution count. Refreshed daily.') + '''

<details>
<summary><em>Visitor’s guide</em></summary>

**The painting**: the profile is one room of a museum; the picture is the portfolio.
**The labels**: each project hangs under an element of the scene; click a label to open its repository.
**The lights of Arles**: real public contributions, one light per day, refreshed daily.

</details>
'''


def main():
    data = json.loads((ROOT/'data/contributions.json').read_text(encoding='utf-8'))
    OUT.mkdir(parents=True, exist_ok=True)
    assets = {'tableau': hero(), 'activity': activity(data)}
    assets.update((f'cartel-{i:02d}', cartel(i, p)) for i, p in enumerate(PROJECTS, 1))
    for name in THEMED:
        body = assets[name]
        for light, dark in DARK.items():
            body = body.replace(light, dark)
        assets[f'{name}-dark'] = body
    for stale in OUT.glob('*.svg'):
        if stale.stem not in assets:
            stale.unlink()
    for name, body in assets.items():
        (OUT/f'{name}.svg').write_text(body, encoding='utf-8')
    (ROOT/'README.md').write_text(readme(), encoding='utf-8')
    print('Rendered SESSION 006: the painting, six museum labels and the lights of Arles.')


if __name__ == '__main__':
    main()
