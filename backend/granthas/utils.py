from docx import Document
from io import BytesIO

def filter_docx_by_commentaries(docx_path, selected_commentaries):
    """
    Filter document by commentary names.
    
    Logic:
    - If heading matches commentary name AND selected → INCLUDE
    - If heading matches commentary name AND NOT selected → REMOVE
    - If heading doesn't match any commentary → INCLUDE (structural)
    - If NO commentaries selected at all → REMOVE ALL commentaries
    """
    
    doc = Document(docx_path)
    new_doc = Document()
    new_doc.styles._element = doc.styles._element
    
    all_commentaries = selected_commentaries.get('all_commentaries', [])
    selected = selected_commentaries.get('selected', [])
    
    # Check if 'all' is selected
    include_all = 'all' in selected
    
    # Check if NOTHING is selected (empty list or only empty strings)
    nothing_selected = len(selected) == 0 or all(not s or s.strip() == '' for s in selected)
    
    skip_until_level = None
    
    print(f"\n{'='*70}")
    print(f"ALL COMMENTARIES: {all_commentaries}")
    print(f"SELECTED: {selected}")
    print(f"Include all: {include_all}")
    print(f"Nothing selected: {nothing_selected}")
    print(f"{'='*70}\n")
    
    for paragraph in doc.paragraphs:
        style_name = paragraph.style.name
        text = paragraph.text.strip()
        
        if not text:
            if skip_until_level is None:
                new_para = new_doc.add_paragraph()
                new_para.style = paragraph.style
            continue
        
        if style_name.startswith('Heading'):
            level = int(style_name.replace('Heading', '').strip() or '1')
            
            # Stop skipping if reached same or higher level
            if skip_until_level is not None:
                if level <= skip_until_level:
                    skip_until_level = None
                else:
                    print(f"  [SKIP] {style_name}: '{text}'")
                    continue
            
            # Check if this heading is a commentary
            if text in all_commentaries:
                # This IS a commentary heading
                
                if include_all:
                    # All selected - include everything
                    print(f"✓ {style_name}: '{text}' (All selected)")
                    skip_until_level = None
                    
                elif nothing_selected:
                    # Nothing selected - REMOVE ALL commentaries
                    print(f"✗ {style_name}: '{text}' (No selection - REMOVE ALL commentaries)")
                    skip_until_level = level
                    continue
                    
                elif text in selected:
                    # This specific commentary is selected
                    print(f"✓ {style_name}: '{text}' (SELECTED)")
                    skip_until_level = None
                    
                else:
                    # This commentary is NOT selected
                    print(f"✗ {style_name}: '{text}' (NOT selected - REMOVE)")
                    skip_until_level = level
                    continue
            else:
                # NOT a commentary - structural heading - ALWAYS INCLUDE
                print(f"→ {style_name}: '{text}' (Structural)")
                skip_until_level = None
        
        if skip_until_level is not None:
            continue
        
        # Add paragraph
        new_para = new_doc.add_paragraph()
        new_para.style = paragraph.style
        
        for run in paragraph.runs:
            new_run = new_para.add_run(run.text)
            new_run.bold = run.bold
            new_run.italic = run.italic
            new_run.underline = run.underline
            if run.font.size:
                new_run.font.size = run.font.size
            if run.font.name:
                new_run.font.name = run.font.name
    
    print(f"\n{'='*70}")
    print("FILTERING COMPLETE")
    print(f"{'='*70}\n")
    
    buffer = BytesIO()
    new_doc.save(buffer)
    buffer.seek(0)
    return buffer
