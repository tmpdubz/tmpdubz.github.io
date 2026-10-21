"""Read metrics and embed bundled TrueType fonts without runtime dependencies."""
import struct
import zlib


class TrueTypeFont:
    def __init__(self, path, name, italic=False):
        self.data = path.read_bytes()
        self.name = name
        self.italic = italic
        count = self.u16(4)
        self.tables = {}
        for i in range(count):
            tag, _, offset, length = struct.unpack_from('>4sIII', self.data, 12 + i * 16)
            self.tables[tag.decode()] = (offset, length)
        head = self.tables['head'][0]
        self.units = self.u16(head + 18)
        self.bbox = [self.scale(x) for x in struct.unpack_from('>hhhh', self.data, head + 36)]
        hhea = self.tables['hhea'][0]
        self.ascent = self.scale(self.i16(hhea + 4))
        self.descent = self.scale(self.i16(hhea + 6))
        metric_count = self.u16(hhea + 34)
        metrics = self.tables['hmtx'][0]
        advances = [self.u16(metrics + i * 4) for i in range(metric_count)]
        cmap = self.tables['cmap'][0]
        offsets = []
        for i in range(self.u16(cmap + 2)):
            platform, encoding, offset = struct.unpack_from('>HHI', self.data, cmap + 4 + i * 8)
            if platform in (0, 3) and self.u16(cmap + offset) == 4:
                offsets.append((platform == 3 and encoding == 1, cmap + offset))
        if not offsets:
            raise ValueError(f'{path}: no supported Unicode character map')
        subtable = max(offsets)[1]
        segments = self.u16(subtable + 6) // 2
        ends = subtable + 14
        starts = ends + segments * 2 + 2
        deltas = starts + segments * 2
        ranges = deltas + segments * 2
        self.widths = {}
        for byte in range(256):
            try:
                code = ord(bytes([byte]).decode('cp1252'))
            except UnicodeDecodeError:
                self.widths[byte] = 0
                continue
            glyph = 0
            for i in range(segments):
                if self.u16(starts + i * 2) <= code <= self.u16(ends + i * 2):
                    delta = self.i16(deltas + i * 2)
                    offset = self.u16(ranges + i * 2)
                    if offset:
                        glyph = self.u16(ranges + i * 2 + offset + 2 * (code - self.u16(starts + i * 2)))
                        if glyph:
                            glyph = (glyph + delta) & 0xffff
                    else:
                        glyph = (code + delta) & 0xffff
                    break
            self.widths[byte] = self.scale(advances[min(glyph, metric_count - 1)])

    def u16(self, offset):
        return struct.unpack_from('>H', self.data, offset)[0]

    def i16(self, offset):
        return struct.unpack_from('>h', self.data, offset)[0]

    def scale(self, value):
        return round(value * 1000 / self.units)

    def width(self, text, size):
        return sum(self.widths[c] for c in text.encode('cp1252')) * size / 1000

    def embed(self, add):
        compressed = zlib.compress(self.data)
        file_id = add(f'<< /Length {len(compressed)} /Length1 {len(self.data)} /Filter /FlateDecode >>\nstream\n'.encode() + compressed + b'\nendstream')
        descriptor = add((f'<< /Type /FontDescriptor /FontName /{self.name} /Flags {96 if self.italic else 32} '
                          f'/FontBBox [{" ".join(map(str, self.bbox))}] /ItalicAngle {-12 if self.italic else 0} '
                          f'/Ascent {self.ascent} /Descent {self.descent} /CapHeight {self.ascent} '
                          f'/StemV 80 /FontFile2 {file_id} 0 R >>').encode())
        mapping = []
        for byte in range(32, 256):
            try:
                mapping.append(f'<{byte:02X}> <{ord(bytes([byte]).decode("cp1252")):04X}>')
            except UnicodeDecodeError:
                pass
        cmap = ('/CIDInit /ProcSet findresource begin\n12 dict begin\nbegincmap\n'
                '/CIDSystemInfo << /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def\n'
                '/CMapName /WinAnsiUnicode def\n/CMapType 2 def\n'
                '1 begincodespacerange\n<00> <FF>\nendcodespacerange\n')
        for i in range(0, len(mapping), 100):
            group = mapping[i:i + 100]
            cmap += f'{len(group)} beginbfchar\n' + '\n'.join(group) + '\nendbfchar\n'
        cmap += 'endcmap\nCMapName currentdict /CMap defineresource pop\nend\nend'
        encoded = cmap.encode()
        unicode_id = add(f'<< /Length {len(encoded)} >>\nstream\n'.encode() + encoded + b'\nendstream')
        widths = ' '.join(str(self.widths[i]) for i in range(32, 256))
        return add((f'<< /Type /Font /Subtype /TrueType /BaseFont /{self.name} /Encoding /WinAnsiEncoding '
                    f'/FirstChar 32 /LastChar 255 /Widths [{widths}] '
                    f'/FontDescriptor {descriptor} 0 R /ToUnicode {unicode_id} 0 R >>').encode())
