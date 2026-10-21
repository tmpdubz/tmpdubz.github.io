#!/usr/bin/env python3
"""Generate the CV PDF from shared Markdown and bundled fonts, using only Python 3."""
import argparse
from pathlib import Path
import re

from pdf_fonts import TrueTypeFont

ROOT = Path(__file__).resolve().parent.parent
BLUE = (28 / 255, 69 / 255, 135 / 255)
BLACK = (0.06, 0.06, 0.06)
GRAY = (0.40, 0.40, 0.40)
LEFT, WIDTH, TOP, BOTTOM = 54, 504, 722, 48


def clean(text):
    return re.sub(r'\*\*(.*?)\*\*', r'\1', text)


def pdf_string(text):
    data = text.encode('cp1252')
    return b'(' + data.replace(b'\\', b'\\\\').replace(b'(', b'\\(').replace(b')', b'\\)') + b')'


class CV:
    def __init__(self, fonts):
        self.fonts = fonts
        self.pages = [[]]
        self.y = TOP

    def reserve(self, height):
        if self.y - height < BOTTOM:
            self.pages.append([])
            self.y = TOP

    def text(self, text, size=10, font=0, color=BLACK, x=LEFT, width=WIDTH,
             space=5, leading=None, bullet=False):
        """Wrap by actual font metrics, preserving bold spans and bullet indents."""
        leading = leading or size * 1.28
        tokens = []
        pending_space = False
        for i, segment in enumerate(re.split(r'\*\*(.*?)\*\*', text)):
            segment_font = 1 if i % 2 else font
            for token in re.findall(r'\s+|\S+', segment):
                if token.isspace():
                    pending_space = True
                else:
                    tokens.append((token, segment_font, pending_space))
                    pending_space = False
        lines, line, used = [], [], 0
        text_x = x + (18 if bullet else 0)
        available = width - (18 if bullet else 0)
        for word, face, has_space in tokens:
            word_width = self.fonts[face].width(word, size)
            gap = self.fonts[face].width(' ', size) if line and has_space else 0
            if line and used + gap + word_width > available:
                lines.append(line)
                line, used, gap = [], 0, 0
            line.append((word, face, gap))
            used += gap + word_width
        if line:
            lines.append(line)
        self.reserve(len(lines) * leading + space)
        for i, line in enumerate(lines):
            if bullet and i == 0:
                self.pages[-1].append((x + 3, self.y, size * 1.2, 0, color, '\u2022'))
            cursor = text_x
            for word, face, gap in line:
                cursor += gap
                self.pages[-1].append((cursor, self.y, size, face, color, word))
                cursor += self.fonts[face].width(word, size)
            self.y -= leading
        self.y -= space

    def bytes(self, name):
        objects = [b'', b'']

        def add(obj):
            objects.append(obj)
            return len(objects)

        font_ids = [font.embed(add) for font in self.fonts]
        page_ids = []
        for lines in self.pages:
            content = b'\n'.join(
                (f'BT /F{font} {size} Tf {color[0]:.4f} {color[1]:.4f} {color[2]:.4f} rg '
                 f'1 0 0 1 {x:.2f} {y:.2f} Tm ').encode() + pdf_string(text) + b' Tj ET'
                for x, y, size, font, color, text in lines)
            stream_id = add(f'<< /Length {len(content)} >>\nstream\n'.encode() + content + b'\nendstream')
            resources = ' '.join(f'/F{i} {fid} 0 R' for i, fid in enumerate(font_ids))
            page_ids.append(add((f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] '
                                 f'/Resources << /Font << {resources} >> >> /Contents {stream_id} 0 R >>').encode()))
        objects[0] = b'<< /Type /Catalog /Pages 2 0 R >>'
        objects[1] = (f'<< /Type /Pages /Count {len(page_ids)} /Kids ['
                      + ' '.join(f'{i} 0 R' for i in page_ids) + '] >>').encode()
        info_id = add(b'<< /Title ' + pdf_string(name + ' - CV') + b' /Author ' + pdf_string(name) + b' >>')
        output = bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')
        offsets = [0]
        for i, obj in enumerate(objects, 1):
            offsets.append(len(output))
            output.extend(f'{i} 0 obj\n'.encode() + obj + b'\nendobj\n')
        xref = len(output)
        output.extend(f'xref\n0 {len(offsets)}\n0000000000 65535 f \n'.encode())
        for offset in offsets[1:]:
            output.extend(f'{offset:010d} 00000 n \n'.encode())
        output.extend((f'trailer\n<< /Size {len(offsets)} /Root 1 0 R /Info {info_id} 0 R >>\n'
                       f'startxref\n{xref}\n%%EOF\n').encode())
        return output


def render_role(cv, heading, body):
    company, role = heading.split(' / ', 1)
    cv.text(f'**{clean(company)}** / {role}', size=11, space=3)
    for block in re.split(r'\n\s*\n', body.strip()):
        if re.match(r'^[A-Z][a-z]+ \d{4} [–-] ', block):
            date, *notes = block.split(' · ', 1)
            cv.text(date.upper() + (' · ' + notes[0] if notes else ''), size=8.5, color=GRAY, space=8)
        elif block.startswith('**Technologies:'):
            cv.text(block, color=BLUE, space=0)
        elif block.startswith('- '):
            for item in block.splitlines():
                cv.text(item[2:], bullet=True, space=2)
        elif block.startswith('*') and not block.startswith('**') and block.endswith('*'):
            cv.text(block[1:-1], size=9.5, font=2, color=GRAY, space=5)
        else:
            cv.text(' '.join(block.splitlines()), space=6)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'static/Tomasz-Dubiel-CV.pdf')
    args = parser.parse_args()
    source = (ROOT / 'content/resume/index.md').read_text()
    content = re.sub(r'\A---\n.*?\n---\n', '', source, count=1, flags=re.S)
    language = (ROOT / 'config/_default/languages.en.toml').read_text()
    name = re.search(r'^name = "([^"]+)"', language, re.M).group(1)
    email = re.search(r'^email = "([^"]+)"', language, re.M).group(1)
    fonts = [TrueTypeFont(ROOT / f'static/fonts/open-sans/OpenSans-{face}.ttf', f'OpenSans-{face}', face == 'Italic')
             for face in ('Regular', 'Bold', 'Italic')]
    cv = CV(fonts)
    summary, body = content.strip().split('\n## ', 1)
    cv.text(name, size=24, font=1, width=250, leading=24, space=0)
    cv.text('Site Reliability Engineer', size=15, font=1, color=BLUE, width=255, space=12)
    cv.text(email + ' • tdubiel.dev •', size=9, color=BLUE, width=255, space=1)
    cv.text('github.com/tmpdubz • linkedin.com/in/tmpdubz', size=9, color=BLUE, width=255, space=0)
    identity_bottom = cv.y
    cv.y = TOP + 10
    cv.text(summary, size=10.5, color=(.28, .28, .28), x=315, width=243, space=0)
    cv.y = min(identity_bottom, cv.y) - 30
    for section in re.split(r'\n## ', body):
        title, section_body = section.split('\n', 1)
        if title == 'Experience':
            cv.text(title, size=20, font=1, color=BLUE, leading=23, space=3)
            for role_block in section_body.split('\n### ')[1:]:
                heading, role_body = role_block.split('\n', 1)
                # Measure each job first so a job never starts at the bottom of a page.
                probe = CV(fonts)
                probe.y = 10000
                render_role(probe, heading, role_body)
                height = 10000 - probe.y
                cv.reserve(height)
                render_role(cv, heading, role_body)
                cv.y -= 20
        else:
            cv.reserve(85)
            cv.text(title, size=20, font=1, color=BLUE, space=8)
            for block in re.split(r'\n\s*\n', section_body.strip()):
                cv.text(' '.join(block.splitlines()), space=5)
            cv.y -= 18
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(cv.bytes(name))
    print(f'Exported {args.output} ({len(cv.pages)} pages)')


if __name__ == '__main__':
    main()
