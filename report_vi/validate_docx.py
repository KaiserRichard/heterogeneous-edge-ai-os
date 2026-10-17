#!/usr/bin/env python3
"""Structural, content and reproducibility checks; no claim of rendered pagination."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from xml.dom import minidom
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
OUT = ROOT / 'BaoCao_HDH_Nhom3Stars.docx'
subprocess.run([sys.executable, str(ROOT / 'build_docx.py')], check=True)
first = OUT.read_bytes()
subprocess.run([sys.executable, str(ROOT / 'build_docx.py')], check=True)
assert OUT.read_bytes() == first, 'Build is not reproducible'
with zipfile.ZipFile(OUT) as z:
    assert z.testzip() is None
    for name in z.namelist():
        if name.endswith(('.xml', '.rels')):
            minidom.parseString(z.read(name))
    xml = z.read('word/document.xml').decode()
    text = ''.join(ET.fromstring(xml).itertext())
    forbidden = r'results/|release/|slides/|docs/|\.md\b|\.csv\b|\.tex\b|\.onnx\b|FLAGGED|INVALID|MEASURED|\bSIM\b|PLANNED|conductor|provenance|bản trình bày|v2 validity rule|Phụ lục|Nguồn:|<!--|2026-10-\d|\d{8}T\d{6}Z'
    assert not re.search(forbidden, xml, re.I), 'Internal material remains'
    document = ET.fromstring(z.read('word/document.xml'))
    styles = ET.fromstring(z.read('word/styles.xml'))
    settings = ET.fromstring(z.read('word/settings.xml'))
    w = '{'+NS['w']+'}'
    assert settings.find('w:updateFields', NS).get(w+'val') == 'true'
    assert 'TOC \\o "1-2"' in z.read('word/document.xml').decode()
    assert all(styles.find(f"w:style[@w:styleId='{name}']", NS) is not None
               for name in ('Heading1','Heading2','Heading3','Caption'))
    sections = document.findall('.//w:sectPr', NS)
    assert len(sections) == 2
    assert sections[0].find('w:footerReference', NS) is None
    assert sections[1].find('w:footerReference', NS) is not None
    for sec in sections:
        assert sec.find('w:pgSz', NS).attrib == {w+'w':'11906', w+'h':'16838'}
        margins = sec.find('w:pgMar', NS)
        assert [margins.get(w+k) for k in ('top','bottom','left','right')] == ['1417','1134','1701','1134']
    assert len(document.findall('.//w:tbl', NS)) == 8
    assert len([n for n in z.namelist() if n.startswith('word/media/')]) == 3
    assert len(document.findall('.//w:br[@w:type="page"]', NS)) == 2
    assert not document.findall('.//w:pageBreakBefore', NS)
    assert not styles.findall('.//w:pageBreakBefore', NS)
    for table in document.findall('.//w:tbl', NS):
        assert not table.findall('.//w:keepNext', NS)
    table_style = styles.find("w:style[@w:styleId='TableText']", NS)
    assert table_style.find('.//w:keepNext', NS) is None
    wp = '{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}'
    for extent in document.iter(wp+'extent'):
        assert int(extent.get('cx')) <= 4320000
        assert int(extent.get('cy')) <= 2880000
    default = styles.find('w:docDefaults/w:pPrDefault/w:pPr', NS)
    assert default.find('w:ind', NS).get(w+'firstLine') == '567'
    assert default.find('w:spacing', NS).get(w+'after') == '120'
    assert default.find('w:spacing', NS).get(w+'line') == '312'
    for name in ('Caption', 'TableCaption'):
        st = styles.find(f"w:style[@w:styleId='{name}']", NS)
        assert st.find('w:rPr/w:sz', NS).get(w+'val') == '24'
        assert st.find('w:rPr/w:i', NS) is not None
    assert len(re.findall(r'CHƯƠNG [1-8]\.', text)) == 16  # headings and cached TOC
    heading = styles.find("w:style[@w:styleId='Heading1']", NS)
    assert heading.find('.//w:keepNext', NS) is not None
    # All internal document relationship targets must exist.
    rels = ET.fromstring(z.read('word/_rels/document.xml.rels'))
    for rel in rels:
        assert 'word/'+rel.get('Target') in z.namelist()
content = (ROOT/'content.md').read_text()
body = content.split('# CHƯƠNG 1. GIỚI THIỆU',1)[1].split('# TÀI LIỆU THAM KHẢO',1)[0]
body = re.sub(r'<!--.*?-->', '', body)
words = len(body.split())
assert 5400 <= words <= 6400, words
assert content.count('<!-- PAGE -->') == 3
assert '<!-- PAGE -->' not in content.split('# CHƯƠNG 1. GIỚI THIỆU', 1)[1]
assert len(re.findall(r'^Bảng \d+\.',content,re.M)) == 7
assert len(re.findall(r'^!\[Hình \d+\.\d+\.',content,re.M)) == 3
for ref in range(1,9):
    assert f'[{ref}]' in body
report = {
    'clean_submission_text': 'PASS', 'zip_crc': 'PASS', 'all_xml_and_relationships_parse': 'PASS',
    'continuous_flow_figure_limits_table_pagination': 'PASS',
    'relationship_targets': 'PASS', 'reproducible_build': 'PASS',
    'a4_margins_styles_toc_cover_footer': 'PASS',
    'body_whitespace_words_including_tables': words,
    'forced_front_matter_breaks': 3, 'target_word_pages': '16–19', 'report_tables': 7, 'cover_members_table': 1, 'figures': 3,
    'rendered_page_count': None,
    'rendering_limit': 'Word pagination requires rendering; continuous flow targets 16–19 pages, not a verified page count.',
    'docx_sha256': hashlib.sha256(first).hexdigest()
}
(ROOT/'validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
print(json.dumps(report, ensure_ascii=False, indent=2))
