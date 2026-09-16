#!/usr/bin/env python3
"""
Quick validation script for skills - minimal version
"""

import sys
import os
import re
from pathlib import Path

def validate_skill(skill_path):
    """Basic validation of a skill"""
    skill_path = Path(skill_path)
    
    # Check SKILL.md exists
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False, "SKILL.md not found"
    
    # Read and validate frontmatter
    content = skill_md.read_text()
    if not content.startswith('---'):
        return False, "No YAML frontmatter found"
    
    # Extract frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format"
    
    frontmatter = match.group(1)

    # Parse the frontmatter as YAML rather than by regex.  A regex for
    # `description:\s*(.+)` captures the block-scalar marker on a folded
    # description (`description: >-`) and then rejects it for containing '>',
    # which failed three valid skills in this repo.
    try:
        import yaml
        meta = yaml.safe_load(frontmatter)
        if not isinstance(meta, dict):
            return False, "Frontmatter is not a mapping"
        name = meta.get('name')
        description = meta.get('description')
        if not isinstance(name, str) or not name.strip():
            return False, "Missing 'name' in frontmatter"
        if not isinstance(description, str) or not description.strip():
            return False, "Missing 'description' in frontmatter"
    except ImportError:
        # No PyYAML: fall back to the original single-line extraction, and
        # skip fields whose value is a block scalar rather than guess at it.
        if 'name:' not in frontmatter:
            return False, "Missing 'name' in frontmatter"
        if 'description:' not in frontmatter:
            return False, "Missing 'description' in frontmatter"
        name_match = re.search(r'name:\s*(.+)', frontmatter)
        name = name_match.group(1).strip() if name_match else ''
        desc_match = re.search(r'description:\s*(.+)', frontmatter)
        description = desc_match.group(1).strip() if desc_match else ''
        if description in ('>-', '>', '|', '|-'):
            description = ''          # block scalar; unparseable without yaml
    except yaml.YAMLError as exc:
        return False, f"Frontmatter does not parse: {str(exc).splitlines()[0]}"

    if name:
        # Check naming convention (hyphen-case: lowercase with hyphens)
        if not re.match(r'^[a-z0-9-]+$', name):
            return False, f"Name '{name}' should be hyphen-case (lowercase letters, digits, and hyphens only)"
        if name.startswith('-') or name.endswith('-') or '--' in name:
            return False, f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens"

    # Check for angle brackets in the actual description text
    if description and ('<' in description or '>' in description):
        return False, "Description cannot contain angle brackets (< or >)"

    return True, "Skill is valid!"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python quick_validate.py <skill_directory>")
        sys.exit(1)
    
    valid, message = validate_skill(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)