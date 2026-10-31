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
from build_docx import OUTPUT_NAME, PPR_ORDER, RPR_ORDER
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
OUT = ROOT / OUTPUT_NAME
subprocess.run([sys.executable, str(ROOT / 'build_docx.py')], check=True)
first = OUT.read_bytes()
subprocess.run([sys.executable, str(ROOT / 'build_docx.py')], check=True)
assert OUT.read_bytes() == first, 'Build is not reproducible'
with zipfile.ZipFile(OUT) as z:
    assert z.testzip() is None
    for name in z.namelist():
        if name.endswith(('.xml', '.rels')):
            minidom.parseString(z.read(name))
    property_nodes = 0
    for name in z.namelist():
        if not name.endswith('.xml'):
            continue
        root = ET.fromstring(z.read(name))
        for tag, order in (('pPr', PPR_ORDER), ('rPr', RPR_ORDER)):
            for node in root.iter('{'+NS['w']+'}'+tag):
                children = [child.tag.split('}')[-1] for child in node]
                assert all(child in order for child in children), (name, tag, children)
                indices = [order.index(child) for child in children]
                assert indices == sorted(indices), (name, tag, children)
                assert len(children) == len(set(children)), (name, tag, children)
                property_nodes += 1
    xml = z.read('word/document.xml').decode()
    text = ''.join(ET.fromstring(xml).itertext())
    forbidden = r'results/|release/|slides/|docs/|\.md\b|\.csv\b|\.tex\b|\.onnx\b|FLAGGED|INVALID|MEASURED|\bSIM\b|PLANNED|conductor|provenance|bản trình bày|v2 validity rule|Phụ lục|Nguồn:|<!--|2026-10-\d|\d{8}T\d{6}Z'
    assert not re.search(forbidden, xml, re.I), 'Internal material remains'
    document = ET.fromstring(z.read('word/document.xml'))
    styles = ET.fromstring(z.read('word/styles.xml'))
    settings = ET.fromstring(z.read('word/settings.xml'))
    w = '{'+NS['w']+'}'
    assert settings.find('w:updateFields', NS).get(w+'val') == 'true'
    assert 'TOC \\o "1-2"' in ''.join(document.itertext())
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
    assert len(document.findall('.//w:tbl', NS)) == 10
    assert len([n for n in z.namelist() if n.startswith('word/media/')]) == 5
    assert not document.findall('.//w:br[@w:type="page"]', NS)
    assert len(document.findall('.//w:pageBreakBefore', NS)) == 2
    assert len(styles.findall('.//w:pageBreakBefore', NS)) == 1
    for table in document.findall('.//w:tbl', NS):
        assert not table.findall('.//w:keepNext', NS)
    for style_id in ('GlossaryText', 'TableText'):
        st = styles.find(f"w:style[@w:styleId='{style_id}']", NS)
        assert st.find('w:rPr/w:sz', NS).get(w+'val') == '22'
    # The cached TOC must match the source headings even before field refresh.
    cached = [ ''.join(p.itertext()) for p in document.findall('.//w:p', NS)
               if p.find("w:pPr/w:pStyle[@w:val='TOC1']", NS) is not None ]
    source_headings = [line.lstrip('# ').strip() for line in (ROOT/'content.md').read_text().splitlines()
                       if line.startswith(('# ', '## '))]
    assert cached == source_headings
    table_style = styles.find("w:style[@w:styleId='TableText']", NS)
    assert table_style.find('.//w:keepNext', NS) is None
    wp = '{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}'
    for extent in document.iter(wp+'extent'):
        assert int(extent.get('cx')) <= 4320000
        assert int(extent.get('cy')) <= 2340000
    default = styles.find('w:docDefaults/w:pPrDefault/w:pPr', NS)
    assert default.find('w:ind', NS).get(w+'firstLine') == '567'
    assert default.find('w:spacing', NS).get(w+'after') == '80'
    assert default.find('w:spacing', NS).get(w+'line') == '288'
    for name in ('Caption', 'TableCaption'):
        st = styles.find(f"w:style[@w:styleId='{name}']", NS)
        assert st.find('w:rPr/w:sz', NS).get(w+'val') == '24'
        assert st.find('w:rPr/w:i', NS) is not None
    assert len(re.findall(r'PHẦN [1-9]\.', text)) == 18  # headings and cached TOC
    heading = styles.find("w:style[@w:styleId='Heading1']", NS)
    assert heading.find('.//w:keepNext', NS) is not None
    assert heading.find('.//w:pageBreakBefore', NS) is not None
    assert 'DANH MỤC THUẬT NGỮ VÀ TỪ VIẾT TẮT' in text
    # All internal document relationship targets must exist.
    rels = ET.fromstring(z.read('word/_rels/document.xml.rels'))
    for rel in rels:
        assert 'word/'+rel.get('Target') in z.namelist()
content = (ROOT/'content.md').read_text()
body = content.split('# PHẦN 1. GIỚI THIỆU',1)[1].split('# TÀI LIỆU THAM KHẢO',1)[0]
body = re.sub(r'<!--.*?-->', '', body)
words = len(body.split())
assert 5400 <= words <= 6500, words
assert content.count('<!-- PAGE -->') == 3
assert '<!-- PAGE -->' not in content.split('# PHẦN 1. GIỚI THIỆU', 1)[1]
assert len(re.findall(r'^Bảng \d+\.',content,re.M)) == 8
assert len(re.findall(r'^!\[Hình \d+\.\d+\.',content,re.M)) == 4
glossary = content.split('<!-- GLOSSARY -->', 1)[1].split('# PHẦN 1.', 1)[0]
glossary_rows = [line for line in glossary.splitlines() if line.startswith('|')][2:]
assert 1 <= len(glossary_rows) <= 32
for row in glossary_rows:
    cells = [cell.strip() for cell in row.strip('|').split('|')]
    assert len(cells[2].split()) <= 12, cells
    for term in cells[0].split(' / '):
        assert re.search(r'(?<!\w)'+re.escape(term)+r'(?!\w)', body, re.I), term
labels = [line.split('|')[1].strip() for line in glossary_rows]
assert labels == sorted(labels, key=str.casefold)
assert 'CHƯƠNG' not in content
for phrase in ('Tóm lại', 'Nhìn chung', 'Đáng chú ý', 'Cần lưu ý rằng'):
    assert phrase not in content
assert content.count('Do đó') <= 2 and content.count('Điều này cho thấy') <= 2
assert 'đang trong quá trình triển khai' in content and 'Kết quả sơ bộ' in content
for ref in range(1,9):
    assert f'[{ref}]' in body
assert 'BÁO CÁO BÀI TẬP LỚN GIỮA KỲ' in text
for code, status in ((1, 'PASS'), (2, 'PASS'), (3, 'FAIL'), (4, 'FAIL')):
    row = next(line for line in content.splitlines() if line.startswith(f'| OS-T{code} '))
    assert status in row and 'đang cập nhật' in row
assert all(f'OS-T{code}' in content for code in range(5, 9))
assert '30/11/2026' in content
assert hashlib.sha256((ROOT/'BaoCao_HDH_Nhom3Stars.docx').read_bytes()).hexdigest() == json.loads((ROOT/'c1_t19_sources.json').read_text())['original_docx_sha256']
report = {
    'clean_submission_text': 'PASS', 'zip_crc': 'PASS', 'all_xml_and_relationships_parse': 'PASS',
    'part_page_breaks_figure_limits_table_pagination': 'PASS',
    'property_child_schema_order': 'PASS', 'property_nodes_checked': property_nodes,
    'static_toc_matches_headings': 'PASS',
    'relationship_targets': 'PASS', 'reproducible_build': 'PASS',
    'a4_margins_styles_toc_cover_footer': 'PASS',
    'body_whitespace_words_including_tables': words,
    'forced_front_matter_breaks': 3, 'target_word_pages': '≤20', 'report_tables': 8, 'cover_members_table': 1, 'glossary_rows': len(glossary_rows), 'figures': 4,
    'rendered_page_count': None,
    'rendering_limit': 'Word pagination requires rendering; target is at most 20 pages, not a verified page count.',
    'output_document': OUTPUT_NAME,
    'docx_sha256': hashlib.sha256(first).hexdigest()
}
(ROOT/'validation_giuaky.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
print(json.dumps(report, ensure_ascii=False, indent=2))
