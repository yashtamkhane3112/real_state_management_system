from io import BytesIO

def money(value):
    try: value=float(value)
    except (TypeError,ValueError): return '₹0'
    if value>=10000000: return f'₹{value/10000000:.2f} Cr'
    if value>=100000: return f'₹{value/100000:.2f} L'
    return f'₹{value:,.0f}'

def make_simple_pdf(title, rows):
    parts=['BT','/F1 14 Tf']; y=780
    for line in ([title,'']+[str(r) for r in rows])[:42]:
        line=line.replace('\\','\\\\').replace('(','\\(').replace(')','\\)')[:95]
        parts.append(f'50 {y} Td ({line}) Tj'); parts.append('0 -18 Td'); y-=18
    parts.append('ET'); stream='\n'.join(parts).encode('latin-1','replace')
    objs=[b'<< /Type /Catalog /Pages 2 0 R >>',b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>',b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',b'<< /Length '+str(len(stream)).encode()+b' >>\nstream\n'+stream+b'\nendstream']
    buf=BytesIO(); buf.write(b'%PDF-1.4\n'); offsets=[0]
    for i,o in enumerate(objs,1): offsets.append(buf.tell()); buf.write(f'{i} 0 obj\n'.encode()+o+b'\nendobj\n')
    xref=buf.tell(); buf.write(f'xref\n0 {len(objs)+1}\n'.encode()+b'0000000000 65535 f \n')
    for off in offsets[1:]: buf.write(f'{off:010d} 00000 n \n'.encode())
    buf.write(f'trailer << /Root 1 0 R /Size {len(objs)+1} >>\nstartxref\n{xref}\n%%EOF'.encode()); return buf.getvalue()
