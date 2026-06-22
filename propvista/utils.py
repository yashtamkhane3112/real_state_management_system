"""
propvista/utils.py
------------------
Shared utility functions used across multiple Django apps.
Centralised here to avoid code duplication.
"""
import os
import uuid


def sanitize_uploaded_filenames(files_dict, max_length=60):
    """
    Sanitise the filenames for every uploaded file in *files_dict*
    (a Django MultiValueDict such as request.FILES).

    Keeps only alphanumeric characters, hyphens, and underscores.
    Generates a random UUID prefix when the sanitised name is empty.
    Truncates to *max_length* characters (including the extension).
    """
    for key in files_dict:
        for f in files_dict.getlist(key):
            name, ext = os.path.splitext(f.name)
            name = "".join(c for c in name if c.isalnum() or c in ("-", "_")).replace(" ", "_")
            if not name:
                name = uuid.uuid4().hex[:8]
            allowed_len = max_length - len(ext)
            if allowed_len <= 0:
                name = name[:10]
            else:
                name = name[:allowed_len]
            f.name = f"{name}{ext}"
