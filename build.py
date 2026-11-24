#!/usr/bin/env python3
"""Builds the tutorial website from ../labs and ../presentations.

Every lab goes online. The slides show the worked solutions, so each deck goes
online only from the day after its tutorial. Run this again after each tutorial.

    python3 build.py           # build only, to check locally
    python3 build.py --push    # build, commit and push (GitHub Pages updates in a minute)
"""
import datetime as dt
import pathlib
import shutil
import subprocess
import sys

SITE = pathlib.Path(__file__).resolve().parent
SRC = SITE.parent

TUTORIALS = [  # number, date of the tutorial, topic
    (10, '2026-11-18', 'Clustering, <i>k</i>-Means and Mixtures of Gaussians'),
    (11, '2026-11-25', 'EM, MM and Factor Analysis'),
    (12, '2026-12-02', 'Principal Component Analysis'),
    (13, '2026-12-09', 'Markov Decision Processes'),
    (14, '2026-12-16', 'Model-Free Reinforcement Learning'),
]

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Machine Learning 2026 · Tutorials</title>
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><rect width='64' height='64' rx='12' fill='%23fff'/><rect x='10' y='14' width='44' height='6' rx='2' fill='%23d6002b'/><rect x='10' y='29' width='44' height='4' rx='2' fill='%231f1f1f'/><rect x='10' y='41' width='30' height='4' rx='2' fill='%231f1f1f'/></svg>">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.css">
<style>
  * { box-sizing: border-box; }
  body {
    margin: 0; background: #fff; color: #1f1f1f;
    font-family: KaTeX_Main, "Latin Modern Roman", "Times New Roman", serif;
    font-size: 20px; line-height: 1.45;
  }
  main { max-width: 860px; margin: 0 auto; padding: 9vh 24px 64px; }
  .rule { width: 2.6em; height: 4px; background: #d6002b; margin-bottom: 1.2em; }
  .sub { color: #666; }
  h1 { font-size: 2em; line-height: 1.2; margin: 0.3em 0 0.4em; }
  table { width: 100%; border-collapse: collapse; margin: 2.2em 0 1.6em; }
  th { text-align: left; font-weight: normal; color: #666; font-size: 0.8em; padding: 0 0.8em 0.4em 0; border-bottom: 1px solid #d6d6d6; }
  td { padding: 0.75em 0.8em 0.75em 0; border-bottom: 1px solid #ececec; vertical-align: baseline; }
  td.n, td.date { color: #666; white-space: nowrap; }
  td.link { white-space: nowrap; }
  a { color: #1d6fa5; text-decoration: none; }
  a:hover { text-decoration: underline; }
  .dl { font-size: 0.8em; margin-left: 0.3em; }
  .later { color: #999; font-size: 0.85em; }
  .note { color: #666; font-size: 0.85em; }
  @media (max-width: 640px) {
    body { font-size: 17px; }
    main { padding: 40px 16px 48px; }
    .date, .dl { display: none; }
  }
</style>
</head>
<body>
<main>
  <div class="rule"></div>
  <div class="sub">Universität Bern · Autumn 2026</div>
  <h1>Machine Learning<br>Tutorials</h1>
  <table>
    <tr><th></th><th class="date">Date</th><th>Topic</th><th>Lab</th><th>Slides</th></tr>
ROWS
  </table>
  <p class="note">The slides appear here after each tutorial. In the slides, → and ← step through, and F switches to full screen.</p>
</main>
</body>
</html>
"""


def build():
    today = dt.date.today()
    rows = []
    for n, date, topic in TUTORIALS:
        day = dt.date.fromisoformat(date)
        lab = SITE / f'labs/tutorial{n}/index.html'
        lab.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SRC / f'labs/tutorial{n}/index.html', lab)

        slides = SITE / f'slides/tutorial{n}'
        if today > day:
            slides.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(SRC / f'presentations/tutorial{n}/index.html', slides / 'index.html')
            deck = (f'<a href="slides/tutorial{n}/">Slides</a>'
                    f'<a class="dl" href="slides/tutorial{n}/index.html" download="ML-2026-Tutorial-{n}-slides.html">(download)</a>')
        else:
            if slides.exists():
                shutil.rmtree(slides)
            deck = f'<span class="later">after {day:%d.%m.}</span>'
        rows.append(f'    <tr><td class="n">{n}</td><td class="date">{day:%d.%m.}</td><td>{topic}</td>'
                    f'<td class="link"><a href="labs/tutorial{n}/">Lab</a></td><td class="link">{deck}</td></tr>')
    (SITE / 'index.html').write_text(PAGE.replace('ROWS', '\n'.join(rows)))
    print('slides online:', [n for n, date, _ in TUTORIALS if today > dt.date.fromisoformat(date)])


def push():
    git = lambda *a: subprocess.run(['git', '-C', str(SITE), *a], check=True, capture_output=True, text=True).stdout
    git('add', '-A')
    if not git('status', '--porcelain').strip():
        print('nothing changed')
        return
    git('commit', '-m', f'Update site ({dt.date.today():%d.%m.%Y})')
    git('push')
    print('pushed')


if __name__ == '__main__':
    build()
    if '--push' in sys.argv:
        push()
