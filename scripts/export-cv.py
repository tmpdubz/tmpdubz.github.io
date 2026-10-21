#!/usr/bin/env python3
"""Generate a text-based CV PDF from the resume Markdown, using only Python 3."""
import argparse
from pathlib import Path
import re
import textwrap

ROOT = Path(__file__).resolve().parent.parent


def clean(text):
    return re.sub(r'\*\*(.*?)\*\*', r'\1', text)


def pdf_string(text):
    data = text.encode('cp1252')
    return b'(' + data.replace(b'\\', b'\\\\').replace(b'(', b'\\(').replace(b')', b'\\)') + b')'


class CV:
    def __init__(self):
        self.pages = [[]]
        self.y = 744

    def reserve(self, height):
        if self.y - height < 48:
            self.pages.append([])
            self.y = 744

    def text(self, text, size=10, bold=False, italic=False, indent=0, space=5, reserve=0):
        # Conservative wrapping also leaves room for wide glyphs in Helvetica.
        width = int((508 - indent) / (size * .48))
        lines = textwrap.wrap(text, width=width, break_long_words=False, break_on_hyphens=False) or ['']
        leading = size * 1.2
        self.reserve(len(lines) * leading + reserve + space)
        for line in lines:
            self.reserve(leading)
            # Continuation lines align with the bullet text rather than its marker.
            hanging = 7 if text.startswith('\u2022 ') and line != lines[0] else 0
            self.pages[-1].append((52 + indent + hanging, self.y, size, 3 if italic else 2 if bold else 1, line))
            self.y -= leading
        self.y -= space

    def bytes(self, name):
        objects = [b'', b'']
        objects.extend([
            b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>',
            b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>',
            b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Oblique /Encoding /WinAnsiEncoding >>',
        ])
        page_ids = []
        for number, lines in enumerate(self.pages, 1):
            lines = lines + [(52, 26, 8, 1, 'tdubiel.dev'), (510, 26, 8, 1, str(number))]
            content = b'\n'.join(
                (f'q 0.8 G 0.5 w 52 {y + 16:.2f} m 560 {y + 16:.2f} l S Q\n'.encode()
                 if size == 11 and font == 2 else b'')
                + f'BT /F{font} {size} Tf 1 0 0 1 {x} {y:.2f} Tm '.encode()
                + pdf_string(text) + b' Tj ET' for x, y, size, font, text in lines)
            stream_id = len(objects) + 1
            objects.append(b'<< /Length ' + str(len(content)).encode() + b' >>\nstream\n' + content + b'\nendstream')
            page_id = len(objects) + 1
            page_ids.append(page_id)
            objects.append((f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] '
                            f'/Resources << /Font << /F1 3 0 R /F2 4 0 R /F3 5 0 R >> >> '
                            f'/Contents {stream_id} 0 R >>').encode())
        objects[0] = b'<< /Type /Catalog /Pages 2 0 R >>'
        objects[1] = ('<< /Type /Pages /Count ' + str(len(page_ids)) + ' /Kids ['
                      + ' '.join(f'{i} 0 R' for i in page_ids) + '] >>').encode()
        info_id = len(objects) + 1
        objects.append(b'<< /Title ' + pdf_string(name + ' - CV') + b' /Author ' + pdf_string(name) + b' >>')
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'static/Tomasz-Dubiel-CV.pdf')
    args = parser.parse_args()
    source = (ROOT / 'content/resume/index.md').read_text()
    content = re.sub(r'\A---\n.*?\n---\n', '', source, count=1, flags=re.S)
    language = (ROOT / 'config/_default/languages.en.toml').read_text()
    name = re.search(r'^name = "([^"]+)"', language, re.M).group(1)
    email = re.search(r'^email = "([^"]+)"', language, re.M).group(1)
    cv = CV()
    cv.text(name, size=24, bold=True, space=3)
    cv.text(email + ' | tdubiel.dev | github.com/tmpdubz | linkedin.com/in/tmpdubz', size=8, space=9)
    cv.text('Site Reliability Engineer', size=12, bold=True, space=9)
    for block in re.split(r'\n\s*\n', content.strip()):
        if block.startswith('### '):
            cv.y -= 12
            cv.text(clean(block[4:]), size=11, bold=True, space=4, reserve=150)
        elif block.startswith('## '):
            cv.y -= 7
            cv.text(clean(block[3:]), size=13, bold=True, space=6, reserve=40)
        elif block.startswith('- '):
            for item in block.split('\n'):
                cv.text('\u2022 ' + clean(item[2:]), indent=8, space=6)
        elif block.startswith('*') and not block.startswith('**') and block.endswith('*'):
            cv.text(block[1:-1], italic=True, space=4, reserve=30)
        elif re.match(r'^[A-Z][a-z]+ \d{4} [–-] ', block):
            cv.text(block, size=10, space=9, reserve=30)
        else:
            cv.text(clean(' '.join(block.splitlines())), bold=block.startswith('**Technologies:'), space=6)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(cv.bytes(name))
    print(f'Exported {args.output} ({len(cv.pages)} pages)')


if __name__ == '__main__':
    main()
