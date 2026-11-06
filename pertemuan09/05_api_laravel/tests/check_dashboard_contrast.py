"""Check the actual light/dark CSS tokens used by text, controls, and graphs."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
css = (ROOT / 'backend/public/dashboard.css').read_text(encoding='utf-8')


def luminance(hex_value):
    value = hex_value.lstrip('#')
    if len(value) == 3:
        value = ''.join(c * 2 for c in value)
    values = [int(value[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [v / 12.92 if v <= 0.04045 else ((v + .055) / 1.055) ** 2.4 for v in values]
    return sum(v * factor for v, factor in zip(linear, (.2126, .7152, .0722)))


pairs = [('ink', 'page', 4.5), ('ink', 'surface', 4.5), ('title', 'page', 4.5),
         ('title', 'surface', 4.5), ('muted', 'page', 4.5), ('muted', 'surface', 4.5),
         ('warn', 'warn-bg', 4.5), ('button-ink', 'title', 4.5),
         ('border', 'surface', 3), ('focus', 'surface', 3), ('focus', 'page', 3)]
results = []
for selector, body in re.findall(r'(:root(?:\[data-theme="dark"\])?)\{([^}]+)\}', css):
    tokens = dict(re.findall(r'--([a-z-]+):\s*(#[a-fA-F0-9]+)', body))
    theme = 'dark' if 'dark' in selector else 'light'
    for foreground, background, minimum in pairs:
        a, b = sorted((luminance(tokens[foreground]), luminance(tokens[background])))
        ratio = (b + .05) / (a + .05)
        assert ratio >= minimum, (theme, foreground, background, ratio)
        results.append(dict(theme=theme, foreground=foreground, background=background,
                            ratio=round(ratio, 2), minimum=minimum, status='PASS'))
assert len(results) == 22
report = dict(status='PASS', method='sRGB relative luminance; CSS tokens from dashboard.css',
              results=results, limits=['Not a full accessibility conformance audit.',
              'Decorative table/grid separator color is excluded; graph lines use title, not separator color.'])
(ROOT / 'bukti/dashboard_contrast.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(dict(status='PASS', pairs=len(results),
                     lowest_text_ratio=min(row['ratio'] for row in results if row['minimum'] == 4.5)), indent=2))
