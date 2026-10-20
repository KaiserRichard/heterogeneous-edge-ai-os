#!/usr/bin/env python3
"""Build the Vietnamese report offline using only Python's standard library.

Subset: #/##/### headings, paragraphs, - bullets, **bold**, *italic*, pipe
 tables, ![caption](relative-image), <!-- PAGE -->, <!-- COVER -->,
 <!-- ABSTRACT --> and <!-- TOC -->. Parts use the Heading 1 page-break property.
"""
from pathlib import Path
import re
import struct
import zipfile
from xml.sax.saxutils import escape
from xml.dom import minidom

ROOT = Path(__file__).resolve().parent
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
NS = f'xmlns:w="{W}" xmlns:r="{R}"'

def run(text, bold=False, italic=False):
    props = ('<w:b/>' if bold else '') + ('<w:i/>' if italic else '')
    return f'<w:r><w:rPr>{props}</w:rPr><w:t xml:space="preserve">{escape(text)}</w:t></w:r>'

def inline(text):
    return ''.join(run(t[2:-2], bold=True) if t.startswith('**') else
                   run(t[1:-1], italic=True) if t.startswith('*') else run(t)
                   for t in re.split(r'(\*\*.*?\*\*|\*[^*]+\*)', text) if t)

def para(text='', style=None, center=False, extra=''):
    p = (f'<w:pStyle w:val="{style}"/>' if style else '')
    p += '<w:jc w:val="center"/>' if center else ''
    return f'<w:p><w:pPr>{p}{extra}</w:pPr>{inline(text)}</w:p>'

def dimensions(data):
    if data.startswith(b'\x89PNG'):
        return struct.unpack('>II', data[16:24])
    i = 2
    while i < len(data):
        if data[i] != 255:
            i += 1
            continue
        marker = data[i+1]
        i += 2
        if marker in (0xD8, 0xD9):
            continue
        n = int.from_bytes(data[i:i+2], 'big')
        if marker in (0xC0, 0xC1, 0xC2):
            h, w = struct.unpack('>HH', data[i+3:i+7])
            return w, h
        i += n
    raise ValueError('Unsupported image')

# A4; top/bottom/left/right = 2.5/2/3/2 cm, rounded to twips.
SECTION = '<w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1417" w:bottom="1134" w:left="1701" w:right="1134" w:header="567" w:footer="567" w:gutter="0"/>'

PPR_ORDER = ['pStyle','keepNext','keepLines','pageBreakBefore','framePr','widowControl','numPr','suppressLineNumbers','pBdr','shd','tabs','suppressAutoHyphens','kinsoku','wordWrap','overflowPunct','topLinePunct','autoSpaceDE','autoSpaceDN','bidi','adjustRightInd','snapToGrid','spacing','ind','contextualSpacing','mirrorIndents','suppressOverlap','jc','textDirection','textAlignment','textboxTightWrap','outlineLvl','divId','cnfStyle','rPr','sectPr','pPrChange']
RPR_ORDER = ['rStyle','rFonts','b','bCs','i','iCs','caps','smallCaps','strike','dstrike','outline','shadow','emboss','imprint','noProof','snapToGrid','vanish','webHidden','color','spacing','w','kern','position','sz','szCs','highlight','u','effect','bdr','shd','fitText','vertAlign','rtl','cs','em','lang','eastAsianLayout','specVanish','oMath']

TBLPR_ORDER = ['tblStyle','tblpPr','tblOverlap','bidiVisual','tblStyleRowBandSize','tblStyleColBandSize','tblW','jc','tblCellSpacing','tblInd','tblBorders','shd','tblLayout','tblCellMar','tblLook']

def schema_order(xml):
    """Word rejects pPr/rPr children out of schema order, so sort them before writing."""
    if '<w:' not in xml:
        return xml
    dom = minidom.parseString(xml)
    for tag, order in (('w:pPr', PPR_ORDER), ('w:rPr', RPR_ORDER), ('w:tblPr', TBLPR_ORDER)):
        for node in dom.getElementsByTagName(tag):
            kids = [c for c in node.childNodes if c.nodeType == 1]
            for c in kids:
                node.removeChild(c)
            kids.sort(key=lambda c: order.index(c.tagName[2:]) if c.tagName[2:] in order else len(order))
            for c in kids:
                node.appendChild(c)
    return dom.documentElement.toxml() if not xml.startswith('<?xml') else dom.toxml()

def build():
    # Keep additive rerun tables synchronized with the retained comparison.
    import runpy
    runpy.run_path(str(ROOT.parent / "tools/rerun/build_documents.py"))["refresh"]()
    lines = (ROOT / 'content.md').read_text().splitlines()
    body, media, rels = [], {}, []
    i = 0
    glossary = False
    cover = False
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line:
            continue
        if line == '<!-- COVER -->':
            cover = True
            continue
        if line == '<!-- PAGE -->':
            if cover:
                border = '<w:pgBorders w:offsetFrom="page">' + ''.join(f'<w:{side} w:val="double" w:sz="6" w:space="24" w:color="000000"/>' for side in ('top', 'left', 'bottom', 'right')) + '</w:pgBorders>'
                section = '<w:sectPr><w:type w:val="nextPage"/>' + SECTION + border + '</w:sectPr>'
                body[-1] = body[-1].replace('</w:pPr>', section + '</w:pPr>', 1)
                cover = False
            continue
        if line == '<!-- TOC -->':
            body.append(para('MỤC LỤC', 'FrontHeading', extra='<w:pageBreakBefore/>'))
            body.append('<w:p><w:r><w:fldChar w:fldCharType="begin" w:dirty="true"/></w:r><w:r><w:instrText xml:space="preserve"> TOC \\o "1-2" \\h \\z \\u </w:instrText></w:r><w:r><w:fldChar w:fldCharType="separate"/></w:r></w:p>')
            # Cached entries remain readable before Word updates the field.
            for entry in lines:
                if entry.startswith(('# ', '## ')):
                    body.append(para(entry.lstrip('# ').strip(), 'TOC1'))
            body[-1] = body[-1].replace('</w:p>', '<w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>')
            continue
        if line == '<!-- GLOSSARY -->':
            glossary = True
            body.append(para('DANH MỤC THUẬT NGỮ VÀ TỪ VIẾT TẮT', 'FrontHeading', extra='<w:pageBreakBefore/>'))
            continue
        if line == '<!-- ABSTRACT -->':
            body.append(para('TÓM TẮT', 'FrontHeading'))
            continue
        if line.startswith('<!--'):
            continue
        m = re.fullmatch(r'!\[(.*?)\]\((.*?)\)', line)
        if m:
            caption, path = m.groups()
            data = (ROOT / path).read_bytes()
            w, h = dimensions(data)
            logo = cover
            scale = 1080000 / w if logo else min(5760000 / w, 3600000 / h)  # Logo 3 cm; figures 16 × 10 cm
            cx, cy = int(w * scale), int(h * scale)
            index = len(media) + 1
            name = f'image{index}{Path(path).suffix.lower()}'
            rid = f'rIdImage{index}'
            media[name] = data
            rels.append(f'<Relationship Id="{rid}" Type="{R}/image" Target="media/{name}"/>')
            body.append(f'''<w:p><w:pPr><w:jc w:val="center"/><w:ind w:firstLine="0"/><w:keepNext/></w:pPr><w:r><w:drawing><wp:inline xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/><wp:docPr id="{index}" name="Hình {index}" descr="{escape(caption, {'"': '&quot;'})}"/><a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:nvPicPr><pic:cNvPr id="{index}" name="{name}"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>''')
            if not logo:
                body.append(para(caption, 'Caption', center=True))
            continue
        if line.startswith('|'):
            rows = [line]
            while i < len(lines) and lines[i].strip().startswith('|'):
                rows.append(lines[i].strip()); i += 1
            rows = [r for r in rows if not re.fullmatch(r'[| :\-]+', r)]
            n = len(rows[0].strip('|').split('|'))
            widths = [2268, 3175, 3628] if glossary and n == 3 else [9071 // n] * n
            tbl = '<w:tbl><w:tblPr><w:tblW w:w="9071" w:type="dxa"/><w:tblLayout w:type="fixed"/><w:tblBorders>'
            tbl += ''.join(f'<w:{side} w:val="single" w:sz="4" w:color="808080"/>' for side in ('top','left','bottom','right','insideH','insideV'))
            tbl += '</w:tblBorders><w:tblCellMar><w:top w:w="60" w:type="dxa"/><w:left w:w="115" w:type="dxa"/><w:bottom w:w="60" w:type="dxa"/><w:right w:w="115" w:type="dxa"/></w:tblCellMar></w:tblPr><w:tblGrid>'
            tbl += ''.join(f'<w:gridCol w:w="{width}"/>' for width in widths) + '</w:tblGrid>'
            for idx, row in enumerate(rows):
                tbl += '<w:tr><w:trPr><w:cantSplit/>' + ('<w:tblHeader/>' if idx == 0 else '') + '</w:trPr>'
                for width, cell in zip(widths, row.strip('|').split('|')):
                    tbl += f'<w:tc><w:tcPr><w:tcW w:w="{width}" w:type="dxa"/>' + ('<w:shd w:fill="E8EEF4"/><w:vAlign w:val="center"/>' if idx == 0 else '') + '</w:tcPr>' + para(('**'+cell.strip()+'**') if idx == 0 else cell.strip(), 'CoverTable' if cover else 'GlossaryText' if glossary else 'TableText') + '</w:tc>'
                tbl += '</w:tr>'
            body.append(tbl + '</w:tbl>'); continue
        m = re.match(r'^(#{1,3}) (.*)', line)
        if m:
            glossary = False
            body.append(para(m[2], 'Heading'+str(len(m[1])))); continue
        if line.startswith('- '):
            body.append(para(line[2:], extra='<w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr>')); continue
        style = ('CoverTitle' if 'NỀN TẢNG THỰC THI' in line else 'CoverDate' if line.startswith('Hà Nội,') else 'Cover') if cover else 'TableCaption' if re.match(r'^Bảng \d+\.', line) else 'Source' if line.startswith('Nguồn:') else None
        extra = ''
        if cover:
            style = ('CoverUniversity' if 'ĐẠI HỌC BÁCH KHOA' in line else
                     'CoverReport' if 'BÁO CÁO BÀI TẬP LỚN' in line else
                     'CoverCourse' if 'HỌC PHẦN:' in line else style)
            if style == 'CoverUniversity':
                extra = '<w:pBdr><w:bottom w:val="single" w:sz="6" w:space="8"/></w:pBdr><w:ind w:left="2400" w:right="2400" w:firstLine="0"/>'
        body.append(para(line, style, center=cover, extra=extra))
    body.append('<w:sectPr><w:footerReference w:type="default" r:id="rIdFooter"/>'+SECTION+'<w:pgNumType w:start="1"/></w:sectPr>')
    document = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document {NS}><w:body>'+''.join(body)+'</w:body></w:document>'
    styles = f'''<w:styles {NS}><w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="Times New Roman" w:cs="Times New Roman"/><w:sz w:val="26"/><w:szCs w:val="26"/><w:lang w:val="vi-VN"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="80" w:line="288" w:lineRule="auto"/><w:jc w:val="both"/><w:ind w:firstLine="567"/><w:widowControl/></w:pPr></w:pPrDefault></w:docDefaults><w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>'''
    for level in (1,2,3):
        styles += f'<w:style w:type="paragraph" w:styleId="Heading{level}"><w:name w:val="heading {level}"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:pPr>{"<w:pageBreakBefore/>" if level == 1 else ""}<w:keepNext/><w:keepLines/><w:spacing w:before="160" w:after="100"/><w:ind w:firstLine="0"/><w:outlineLvl w:val="{level-1}"/><w:jc w:val="left"/></w:pPr><w:rPr><w:b/>{"<w:i/>" if level == 3 else ""}<w:sz w:val="{28 if level==1 else 26}"/></w:rPr></w:style>'
    for name, size, align in [('Caption',24,'center'),('TableCaption',24,'center'),('GlossaryText',22,'left'),('TableText',22,'left'),('CoverTable',26,'center'),('Cover',28,'center'),('CoverTitle',40,'center'),('CoverUniversity',28,'center'),('CoverReport',32,'center'),('CoverCourse',28,'center'),('CoverDate',28,'center'),('FrontHeading',28,'center'),('TOC1',26,'left')]:
        before = 1100 if name == 'CoverDate' else 160 if name.startswith('Cover') else 0
        keep = '<w:keepNext/>' if name in ('TableCaption', 'FrontHeading') else ''
        styles += f'<w:style w:type="paragraph" w:styleId="{name}"><w:name w:val="{name}"/><w:basedOn w:val="Normal"/><w:pPr><w:ind w:firstLine="0"/><w:spacing w:before="{before}" w:after="{40 if name == "GlossaryText" else 120}" w:line="{240 if name == "GlossaryText" else 312}" w:lineRule="auto"/><w:jc w:val="{align}"/>{keep}</w:pPr><w:rPr><w:sz w:val="{size}"/>'+('<w:b/>' if name in ('FrontHeading', 'CoverUniversity', 'CoverReport', 'CoverCourse', 'CoverTitle') else '')+('<w:i/>' if name in ('Caption','TableCaption') else '')+('<w:color w:val="1F5FA8"/>' if name == 'CoverTitle' else '')+'</w:rPr></w:style>'
    styles += '</w:styles>'
    footer = f'<w:ftr {NS}><w:p><w:pPr><w:ind w:firstLine="0"/><w:jc w:val="center"/></w:pPr><w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText> PAGE </w:instrText></w:r><w:r><w:fldChar w:fldCharType="separate"/></w:r>{run("1")}<w:r><w:fldChar w:fldCharType="end"/></w:r></w:p></w:ftr>'
    relationships = f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rIdStyles" Type="{R}/styles" Target="styles.xml"/><Relationship Id="rIdSettings" Type="{R}/settings" Target="settings.xml"/><Relationship Id="rIdNumbering" Type="{R}/numbering" Target="numbering.xml"/><Relationship Id="rIdFooter" Type="{R}/footer" Target="footer1.xml"/>'+''.join(rels)+'</Relationships>'
    files = {'word/document.xml': document, 'word/styles.xml': styles, 'word/footer1.xml': footer,
             'word/settings.xml': f'<w:settings {NS}><w:updateFields w:val="true"/></w:settings>',
             'word/numbering.xml': f'<w:numbering {NS}><w:abstractNum w:abstractNumId="0"><w:multiLevelType w:val="singleLevel"/><w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="•"/><w:lvlJc w:val="left"/><w:pPr><w:tabs><w:tab w:val="num" w:pos="360"/></w:tabs><w:ind w:left="360" w:hanging="240"/></w:pPr></w:lvl></w:abstractNum><w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num></w:numbering>',
             'word/_rels/document.xml.rels': relationships,
             '_rels/.rels': f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="{R}/officeDocument" Target="word/document.xml"/></Relationships>'}
    types = '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Default Extension="jpg" ContentType="image/jpeg"/><Default Extension="png" ContentType="image/png"/>'
    for part, kind in [('document','document.main'),('styles','styles'),('settings','settings'),('numbering','numbering'),('footer1','footer')]:
        types += f'<Override PartName="/word/{part}.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.{kind}+xml"/>'
    files['[Content_Types].xml'] = types+'</Types>'
    target = ROOT / 'BaoCao_HDH_Nhom3Stars.docx'
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in files.items():
            data = schema_order(data)
            info = zipfile.ZipInfo(name, (2026,10,17,0,0,0)); info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data.encode('utf-8'))
        for name, data in media.items():
            info = zipfile.ZipInfo('word/media/'+name, (2026,10,17,0,0,0)); info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    print(target)
    print(f'Sections: 2; report figures: {len(media) - 1}; cover logo: 1')

if __name__ == '__main__':
    build()
