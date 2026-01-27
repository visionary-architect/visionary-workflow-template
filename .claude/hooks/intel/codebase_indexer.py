"""
Codebase Indexer - Automatically indexes code files when Claude edits them.

This hook runs after Write/Edit operations on code files and updates
the codebase intelligence files in .planning/intel/

Usage:
    1. Automatic (PostToolUse hook):
       Receives JSON via stdin with tool_input.file_path
       Configured in .claude/settings.json

    2. Manual:
       python codebase_indexer.py <file_path>

    3. Via /analyze-codebase command:
       Scans entire project to bootstrap intelligence

Output files:
    .planning/intel/index.json       - File exports/imports index
    .planning/intel/conventions.json - Detected naming patterns
    .planning/intel/summary.md       - Human-readable summary for Claude
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# Configuration
INTEL_DIR = ".planning/intel"
INDEX_FILE = f"{INTEL_DIR}/index.json"
CONVENTIONS_FILE = f"{INTEL_DIR}/conventions.json"
SUMMARY_FILE = f"{INTEL_DIR}/summary.md"

# File extensions to index
CODE_EXTENSIONS = {
    '.js', '.jsx', '.ts', '.tsx',  # JavaScript/TypeScript
    '.py',                          # Python
    '.go',                          # Go
    '.rs',                          # Rust
    '.java',                        # Java
    '.c', '.h',                     # C
    '.cpp', '.hpp', '.cc', '.cxx',  # C++
    '.rb',                          # Ruby
    '.php',                         # PHP
}

# Directories to skip
SKIP_DIRS = {
    'node_modules', 'venv', '.venv', '__pycache__', '.git',
    'dist', 'build', 'target', '.next', 'coverage'
}


def should_index(file_path: str) -> bool:
    """Check if a file should be indexed."""
    path = Path(file_path)

    # Check extension
    if path.suffix.lower() not in CODE_EXTENSIONS:
        return False

    # Check for skip directories
    for part in path.parts:
        if part in SKIP_DIRS:
            return False

    return True


def extract_js_ts_info(content: str) -> dict:
    """Extract exports and imports from JavaScript/TypeScript files."""
    info = {'exports': [], 'imports': [], 'type': 'module'}

    # Find imports
    import_patterns = [
        r'import\s+{([^}]+)}\s+from\s+[\'"]([^\'"]+)[\'"]',  # named imports
        r'import\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]',       # default imports
        r'import\s+\*\s+as\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]',  # namespace
    ]

    for pattern in import_patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            if isinstance(match, tuple):
                info['imports'].append(match[-1])  # module path

    # Find exports
    export_patterns = [
        r'export\s+(?:const|let|var|function|class)\s+(\w+)',  # named exports
        r'export\s+{([^}]+)}',  # export list
        r'export\s+default\s+(?:function\s+)?(\w+)',  # default export
    ]

    for pattern in export_patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            if ',' in match:
                # Multiple exports in braces
                names = [n.strip().split(' as ')[0] for n in match.split(',')]
                info['exports'].extend(names)
            else:
                info['exports'].append(match.strip())

    # Detect type
    if 'React' in content or 'jsx' in content.lower():
        info['type'] = 'component'
    elif re.search(r'export\s+(?:async\s+)?function\s+(?:GET|POST|PUT|DELETE|PATCH)', content):
        info['type'] = 'api-route'
    elif 'use' in info['exports'][0] if info['exports'] else False:
        info['type'] = 'hook'

    # Remove duplicates
    info['exports'] = list(set(info['exports']))
    info['imports'] = list(set(info['imports']))

    return info


def extract_python_info(content: str) -> dict:
    """Extract exports and imports from Python files."""
    info = {'exports': [], 'imports': [], 'type': 'module'}

    # Find imports
    import_patterns = [
        r'^import\s+(\S+)',
        r'^from\s+(\S+)\s+import',
    ]

    for pattern in import_patterns:
        matches = re.findall(pattern, content, re.MULTILINE)
        info['imports'].extend(matches)

    # Find exports (classes and functions at module level)
    export_patterns = [
        r'^class\s+(\w+)',
        r'^def\s+(\w+)',
        r'^(\w+)\s*=',  # top-level assignments
    ]

    for pattern in export_patterns:
        matches = re.findall(pattern, content, re.MULTILINE)
        # Filter out private names
        public = [m for m in matches if not m.startswith('_')]
        info['exports'].extend(public)

    # Remove duplicates
    info['exports'] = list(set(info['exports']))
    info['imports'] = list(set(info['imports']))

    return info


def extract_go_info(content: str) -> dict:
    """Extract exports and imports from Go files."""
    info = {'exports': [], 'imports': [], 'type': 'module'}

    # Find package name
    package_match = re.search(r'^package\s+(\w+)', content, re.MULTILINE)
    if package_match:
        pkg = package_match.group(1)
        if pkg == 'main':
            info['type'] = 'executable'
        else:
            info['type'] = 'package'

    # Find imports (single and grouped)
    # Single: import "fmt"
    single_imports = re.findall(r'^import\s+"([^"]+)"', content, re.MULTILINE)
    info['imports'].extend(single_imports)

    # Grouped: import ( "fmt" \n "strings" )
    grouped_match = re.search(r'import\s*\(([\s\S]*?)\)', content)
    if grouped_match:
        group_content = grouped_match.group(1)
        grouped_imports = re.findall(r'"([^"]+)"', group_content)
        info['imports'].extend(grouped_imports)

    # Find exported functions (PascalCase = public in Go)
    func_matches = re.findall(r'^func\s+(?:\([^)]+\)\s+)?([A-Z]\w*)\s*\(', content, re.MULTILINE)
    info['exports'].extend(func_matches)

    # Find exported types (type Name struct/interface)
    type_matches = re.findall(r'^type\s+([A-Z]\w*)\s+(?:struct|interface)', content, re.MULTILINE)
    info['exports'].extend(type_matches)

    # Find exported constants and variables
    const_matches = re.findall(r'^(?:const|var)\s+([A-Z]\w*)\s*(?:=|\s)', content, re.MULTILINE)
    info['exports'].extend(const_matches)

    # Remove duplicates
    info['exports'] = list(set(info['exports']))
    info['imports'] = list(set(info['imports']))

    return info


def extract_rust_info(content: str) -> dict:
    """Extract exports and imports from Rust files."""
    info = {'exports': [], 'imports': [], 'type': 'module'}

    # Find use statements (imports)
    use_matches = re.findall(r'^use\s+([\w:]+)', content, re.MULTILINE)
    info['imports'].extend(use_matches)

    # Find extern crate
    extern_matches = re.findall(r'^extern\s+crate\s+(\w+)', content, re.MULTILINE)
    info['imports'].extend(extern_matches)

    # Find public functions
    pub_fn_matches = re.findall(r'^pub\s+(?:async\s+)?fn\s+(\w+)', content, re.MULTILINE)
    info['exports'].extend(pub_fn_matches)

    # Find public structs
    pub_struct_matches = re.findall(r'^pub\s+struct\s+(\w+)', content, re.MULTILINE)
    info['exports'].extend(pub_struct_matches)

    # Find public enums
    pub_enum_matches = re.findall(r'^pub\s+enum\s+(\w+)', content, re.MULTILINE)
    info['exports'].extend(pub_enum_matches)

    # Find public traits
    pub_trait_matches = re.findall(r'^pub\s+trait\s+(\w+)', content, re.MULTILINE)
    info['exports'].extend(pub_trait_matches)

    # Find public type aliases
    pub_type_matches = re.findall(r'^pub\s+type\s+(\w+)', content, re.MULTILINE)
    info['exports'].extend(pub_type_matches)

    # Find public constants
    pub_const_matches = re.findall(r'^pub\s+const\s+(\w+)', content, re.MULTILINE)
    info['exports'].extend(pub_const_matches)

    # Find public modules
    pub_mod_matches = re.findall(r'^pub\s+mod\s+(\w+)', content, re.MULTILINE)
    info['exports'].extend(pub_mod_matches)

    # Detect if this is a binary or library
    if re.search(r'^fn\s+main\s*\(\s*\)', content, re.MULTILINE):
        info['type'] = 'binary'
    elif re.search(r'^pub\s+', content, re.MULTILINE):
        info['type'] = 'library'

    # Remove duplicates
    info['exports'] = list(set(info['exports']))
    info['imports'] = list(set(info['imports']))

    return info


def extract_java_info(content: str) -> dict:
    """Extract exports and imports from Java files."""
    info = {'exports': [], 'imports': [], 'type': 'class'}

    # Find package
    package_match = re.search(r'^package\s+([\w.]+);', content, re.MULTILINE)
    if package_match:
        info['package'] = package_match.group(1)

    # Find imports
    import_matches = re.findall(r'^import\s+(?:static\s+)?([\w.]+(?:\.\*)?);', content, re.MULTILINE)
    info['imports'].extend(import_matches)

    # Find public classes
    class_matches = re.findall(r'^public\s+(?:abstract\s+|final\s+)?class\s+(\w+)', content, re.MULTILINE)
    info['exports'].extend(class_matches)

    # Find public interfaces
    interface_matches = re.findall(r'^public\s+interface\s+(\w+)', content, re.MULTILINE)
    info['exports'].extend(interface_matches)

    # Find public enums
    enum_matches = re.findall(r'^public\s+enum\s+(\w+)', content, re.MULTILINE)
    info['exports'].extend(enum_matches)

    # Find public methods (simplified - just top-level public methods)
    method_matches = re.findall(r'^\s+public\s+(?:static\s+)?(?:[\w<>\[\],\s]+)\s+(\w+)\s*\(', content, re.MULTILINE)
    # Filter out constructors (same name as class)
    methods = [m for m in method_matches if m not in info['exports']]
    info['exports'].extend(methods)

    # Detect type
    if re.search(r'^public\s+interface\s+', content, re.MULTILINE):
        info['type'] = 'interface'
    elif re.search(r'^public\s+enum\s+', content, re.MULTILINE):
        info['type'] = 'enum'
    elif re.search(r'^public\s+abstract\s+class', content, re.MULTILINE):
        info['type'] = 'abstract-class'
    elif re.search(r'public\s+static\s+void\s+main\s*\(\s*String', content):
        info['type'] = 'executable'

    # Remove duplicates
    info['exports'] = list(set(info['exports']))
    info['imports'] = list(set(info['imports']))

    return info


def extract_c_cpp_info(content: str, file_path: str) -> dict:
    """Extract exports and imports from C/C++ files."""
    ext = Path(file_path).suffix.lower()
    is_header = ext in {'.h', '.hpp'}
    is_cpp = ext in {'.cpp', '.hpp', '.cc', '.cxx'}

    info = {'exports': [], 'imports': [], 'type': 'source'}

    if is_header:
        info['type'] = 'header'

    # Find #include statements
    # System includes: #include <stdio.h>
    system_includes = re.findall(r'#include\s*<([^>]+)>', content)
    info['imports'].extend(system_includes)

    # Local includes: #include "myheader.h"
    local_includes = re.findall(r'#include\s*"([^"]+)"', content)
    info['imports'].extend(local_includes)

    # Find function declarations/definitions
    # Matches: void func_name(...) or int main(...) etc.
    # Excludes static functions (internal linkage)
    func_pattern = r'^(?!static\s)[\w\s\*]+?\s+(\w+)\s*\([^)]*\)\s*[{;]'
    func_matches = re.findall(func_pattern, content, re.MULTILINE)
    # Filter out common keywords that might match
    keywords = {'if', 'while', 'for', 'switch', 'return', 'sizeof', 'typeof'}
    funcs = [f for f in func_matches if f not in keywords]
    info['exports'].extend(funcs)

    # Find struct definitions
    struct_matches = re.findall(r'^(?:typedef\s+)?struct\s+(\w+)', content, re.MULTILINE)
    info['exports'].extend(struct_matches)

    # Find class definitions (C++)
    if is_cpp or ext == '.h':
        class_matches = re.findall(r'^class\s+(\w+)', content, re.MULTILINE)
        info['exports'].extend(class_matches)

        # Find namespace
        namespace_matches = re.findall(r'^namespace\s+(\w+)', content, re.MULTILINE)
        info['exports'].extend(namespace_matches)

    # Find enum definitions
    enum_matches = re.findall(r'^(?:typedef\s+)?enum\s+(\w+)', content, re.MULTILINE)
    info['exports'].extend(enum_matches)

    # Find typedef type aliases
    typedef_matches = re.findall(r'^typedef\s+[\w\s\*]+\s+(\w+)\s*;', content, re.MULTILINE)
    info['exports'].extend(typedef_matches)

    # Find #define macros (uppercase typically)
    define_matches = re.findall(r'^#define\s+([A-Z][A-Z0-9_]*)', content, re.MULTILINE)
    info['exports'].extend(define_matches)

    # Find global variables (extern declarations in headers)
    if is_header:
        extern_matches = re.findall(r'^extern\s+[\w\s\*]+\s+(\w+)\s*;', content, re.MULTILINE)
        info['exports'].extend(extern_matches)

    # Detect if this has main() - executable
    if re.search(r'\bint\s+main\s*\(', content):
        info['type'] = 'executable'

    # Remove duplicates
    info['exports'] = list(set(info['exports']))
    info['imports'] = list(set(info['imports']))

    return info


def extract_file_info(file_path: str) -> dict:
    """Extract information from a code file."""
    path = Path(file_path)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {'error': str(e)}

    ext = path.suffix.lower()

    if ext in {'.js', '.jsx', '.ts', '.tsx'}:
        return extract_js_ts_info(content)
    elif ext == '.py':
        return extract_python_info(content)
    elif ext == '.go':
        return extract_go_info(content)
    elif ext == '.rs':
        return extract_rust_info(content)
    elif ext == '.java':
        return extract_java_info(content)
    elif ext in {'.c', '.h', '.cpp', '.hpp', '.cc', '.cxx'}:
        return extract_c_cpp_info(content, file_path)
    else:
        return {'exports': [], 'imports': [], 'type': 'unknown'}


def load_json(file_path: str, default: dict) -> dict:
    """Load JSON file or return default."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_json(file_path: str, data: dict):
    """Save data to JSON file."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def detect_naming_convention(names: list) -> str:
    """Detect the naming convention used in a list of names."""
    if not names:
        return None

    conventions = {
        'camelCase': 0,
        'PascalCase': 0,
        'snake_case': 0,
        'kebab-case': 0,
        'SCREAMING_SNAKE': 0,
    }

    for name in names:
        if not name or len(name) < 2:
            continue

        if '_' in name:
            if name.isupper():
                conventions['SCREAMING_SNAKE'] += 1
            else:
                conventions['snake_case'] += 1
        elif '-' in name:
            conventions['kebab-case'] += 1
        elif name[0].isupper():
            conventions['PascalCase'] += 1
        elif name[0].islower() and any(c.isupper() for c in name[1:]):
            conventions['camelCase'] += 1

    # Return most common convention if it meets threshold
    total = sum(conventions.values())
    if total < 5:
        return None

    for conv, count in sorted(conventions.items(), key=lambda x: -x[1]):
        if count / total >= 0.7:
            return conv

    return None


def update_conventions(index: dict, conventions: dict) -> dict:
    """Update conventions based on indexed files."""
    all_exports = []
    all_files = []

    for file_path, info in index.get('files', {}).items():
        all_exports.extend(info.get('exports', []))
        all_files.append(Path(file_path).stem)

    # Detect naming conventions
    func_conv = detect_naming_convention([e for e in all_exports if e[0].islower()])
    class_conv = detect_naming_convention([e for e in all_exports if e[0].isupper()])
    file_conv = detect_naming_convention(all_files)

    if func_conv:
        conventions['naming']['functions'] = func_conv
    if class_conv:
        conventions['naming']['classes'] = class_conv
    if file_conv:
        conventions['naming']['files'] = file_conv

    conventions['_lastUpdated'] = datetime.now().isoformat()

    return conventions


def generate_summary(index: dict, conventions: dict) -> str:
    """Generate human-readable summary."""
    files = index.get('files', {})

    # Count file types
    type_counts = {}
    for info in files.values():
        t = info.get('type', 'unknown')
        type_counts[t] = type_counts.get(t, 0) + 1

    # Find high-impact files (most imported)
    import_counts = {}
    for file_path, info in files.items():
        for imp in info.get('imports', []):
            if imp.startswith('.'):
                import_counts[imp] = import_counts.get(imp, 0) + 1

    # Build summary
    summary = f"""# Codebase Intelligence Summary

> Auto-generated by codebase indexer. Claude reads this for context.

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Files Indexed:** {len(files)}

---

## File Types

"""
    for t, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        summary += f"- {t}: {count} files\n"

    summary += "\n---\n\n## Naming Conventions\n\n"
    naming = conventions.get('naming', {})
    for key, value in naming.items():
        if value:
            summary += f"- **{key}:** {value}\n"

    if conventions.get('directories'):
        summary += "\n---\n\n## Directory Purposes\n\n"
        for dir_path, purpose in conventions.get('directories', {}).items():
            summary += f"- `{dir_path}/` - {purpose}\n"

    if conventions.get('patterns'):
        summary += "\n---\n\n## Detected Patterns\n\n"
        for pattern in conventions.get('patterns', []):
            summary += f"- {pattern}\n"

    summary += "\n---\n\n*This file is auto-generated. Manual edits will be overwritten.*\n"

    return summary


def index_file(file_path: str):
    """Index a single file and update intel."""
    if not should_index(file_path):
        return

    # Load existing data
    index = load_json(INDEX_FILE, {
        '_comment': 'Codebase index',
        '_version': '1.0',
        '_lastUpdated': None,
        'files': {}
    })

    conventions = load_json(CONVENTIONS_FILE, {
        '_comment': 'Detected conventions',
        '_version': '1.0',
        '_lastUpdated': None,
        '_minimumSamples': 5,
        '_confidenceThreshold': 0.7,
        'naming': {},
        'directories': {},
        'patterns': []
    })

    # Extract file info
    info = extract_file_info(file_path)

    # Update index
    rel_path = os.path.relpath(file_path).replace('\\', '/')
    index['files'][rel_path] = info
    index['_lastUpdated'] = datetime.now().isoformat()

    # Update conventions
    conventions = update_conventions(index, conventions)

    # Save files
    save_json(INDEX_FILE, index)
    save_json(CONVENTIONS_FILE, conventions)

    # Generate summary
    summary = generate_summary(index, conventions)
    os.makedirs(os.path.dirname(SUMMARY_FILE), exist_ok=True)
    with open(SUMMARY_FILE, 'w', encoding='utf-8') as f:
        f.write(summary)

    print(f"Indexed: {rel_path}")


def get_file_path_from_stdin() -> str:
    """Read JSON from stdin and extract file_path (PostToolUse hook format)."""
    try:
        # Check if there's data on stdin (non-blocking check)
        import select
        if sys.platform == 'win32':
            # Windows: check if stdin has data
            import msvcrt
            if not msvcrt.kbhit() and sys.stdin.isatty():
                return None
        else:
            # Unix: use select
            if not select.select([sys.stdin], [], [], 0.0)[0]:
                return None

        # Read JSON from stdin
        stdin_data = sys.stdin.read()
        if stdin_data:
            data = json.loads(stdin_data)
            # PostToolUse hook format: tool_input.file_path
            return data.get('tool_input', {}).get('file_path', '')
    except (json.JSONDecodeError, KeyError, IOError):
        pass
    return None


def main():
    file_path = None

    # Priority 1: Try reading from stdin (PostToolUse hook)
    file_path = get_file_path_from_stdin()

    # Priority 2: Command line argument
    if not file_path and len(sys.argv) >= 2:
        file_path = sys.argv[1]

    # Priority 3: Show usage
    if not file_path:
        print("Usage: python codebase_indexer.py <file_path>")
        print("   Or: pipe JSON from PostToolUse hook via stdin")
        sys.exit(0)  # Exit cleanly, not an error

    # Index the file if it exists and is indexable
    if os.path.isfile(file_path):
        index_file(file_path)


if __name__ == '__main__':
    main()
