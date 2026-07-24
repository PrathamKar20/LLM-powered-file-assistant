import os
import datetime
import pypdf
import docx

def read_file(filepath: str) -> dict:
    """
    Read resume files (PDF, TXT, DOCX) and return content and metadata.
    """
    _, ext = os.path.splitext(filepath.lower())
    try:
        if ext == '.txt':
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        elif ext == '.pdf':
            reader = pypdf.PdfReader(filepath)
            content = "\n".join(page.extract_text() or "" for page in reader.pages)
        elif ext == '.docx':
            doc = docx.Document(filepath)
            content = "\n".join(p.text for p in doc.paragraphs)
        else:
            return {"error": f"Unsupported extension: {ext}"}
            
        stat = os.stat(filepath)
        return {
            "content": content.strip(),
            "metadata": {
                "name": os.path.basename(filepath),
                "size": stat.st_size,
                "modified": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()
            }
        }
    except Exception as e:
        return {"error": str(e)}

def list_files(directory: str, extension: str = None) -> list:
    """
    List all files in a directory, optionally filtering by extension.
    """
    try:
        files = []
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                if extension:
                    ext = extension if extension.startswith('.') else f'.{extension}'
                    if not filename.lower().endswith(ext.lower()):
                        continue
                stat = os.stat(filepath)
                files.append({
                    "name": filename,
                    "size": stat.st_size,
                    "modified": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        return files
    except Exception:
        return []

def write_file(filepath: str, content: str) -> dict:
    """
    Write content to a file, creating directories if needed.
    """
    try:
        directory = os.path.dirname(filepath)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"status": "success"}
    except Exception as e:
        return {"error": str(e)}

def search_in_file(filepath: str, keyword: str) -> dict:
    """
    Search for a keyword inside a file (case-insensitive) and return matching lines along with surrounding context.
    """
    read_res = read_file(filepath)
    if "error" in read_res:
        return read_res
        
    content = read_res["content"]
    lines = content.split('\n')
    matches = []
    keyword_lower = keyword.lower()
    
    for idx, line in enumerate(lines):
        if keyword_lower in line.lower():
            start_idx = max(0, idx - 2)
            end_idx = min(len(lines), idx + 3)
            context_lines = lines[start_idx:end_idx]
            
            matches.append({
                "line_number": idx + 1,
                "matched_line": line.strip(),
                "context": "\n".join(context_lines)
            })
            
    return {
        "keyword": keyword,
        "matches_count": len(matches),
        "matches": matches
    }
