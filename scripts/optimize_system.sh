#!/bin/bash
# Advanced Dynamic System Optimization Script (CI/CD Ready)
# Features:
#   - Language auto-detection
#   - Large file finder (per language & overall top 5)
#   - System & memory optimization
#   - Tool & project-specific cache cleanup
#   - CI/CD GitHub Actions summary
# NEW: --deep flag for Repository Deep Clean (Git reset/clean)

set -e

# --- Colors ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# --- GitHub Actions summary helper ---
gh_log() { 
    msg="$1"
    echo -e "${msg}"
    [ -n "$GITHUB_STEP_SUMMARY" ] && echo -e "$msg" >> "$GITHUB_STEP_SUMMARY"
}

log()       { gh_log "${GREEN}[INFO]${NC} $1"; }
warn()      { gh_log "${YELLOW}[WARN]${NC} $1"; }
highlight() { gh_log "${CYAN}[SEARCH]${NC} $1"; }
command_exists() { command -v "$1" >/dev/null 2>&1; }

# --- Parse Arguments ---
DEEP_CLEAN=false
for arg in "$@"; do
    [ "$arg" == "--deep" ] && DEEP_CLEAN=true
done

# --- Initial stats ---
log "Capturing initial system stats..."
INITIAL_DISK=$(df -h / | awk 'NR==2 {print $4}')
INITIAL_MEM=$(free -h | awk '/^Mem:/ {print $7}')

# --- 1. Deep Repository Clean ---
if [ "$DEEP_CLEAN" = true ] && [ -d ".git" ]; then
    log "Performing DEEP CLEAN (Repository Reset)..."
    git config --system core.longpaths true || true
    git clean -ffdx -e .env || warn "Git clean failed - some files might be in use."
    # git reset --hard HEAD # Uncomment if full reset is needed
fi

# --- 2. Language Auto-Detection ---
log "Detecting programming languages in repository..."
declare -A LANG_EXTS=(
    [Python]="py"
    [JavaScript]="js"
    [TypeScript]="ts"
    [Go]="go"
    [Rust]="rs"
    [C]="c"
    [C++]="cpp"
    [Java]="java"
    [Shell]="sh"
)

for lang in "${!LANG_EXTS[@]}"; do
    count=$(find . -type f -name "*.${LANG_EXTS[$lang]}" 2>/dev/null | wc -l)
    [ "$count" -gt 0 ] && log "$lang files detected: $count"
done

# --- 3. Large File Finder ---
highlight "Top 5 largest files in workspace:"
find . -maxdepth 3 -type f -not -path '*/.*' -exec du -h {} + 2>/dev/null | sort -hr | head -n 5 || true

# Large files per language
highlight "Largest files per detected language:"
for lang in "${!LANG_EXTS[@]}"; do
    files=$(find . -type f -name "*.${LANG_EXTS[$lang]}" 2>/dev/null)
    if [ -n "$files" ]; then
        highlight "Language: $lang"
        find . -type f -name "*.${LANG_EXTS[$lang]}" -exec du -h {} + 2>/dev/null | sort -hr | head -n 3
    fi
done

# --- 4. VS Code Cache Cleanup ---
[ -d "/vscode/serverCache" ] && log "Cleaning VS Code serverCache..." && sudo rm -rf /vscode/serverCache/* 2>/dev/null || true
[ -d "/vscode/extensionsCache" ] && log "Cleaning VS Code extensionsCache..." && sudo rm -rf /vscode/extensionsCache/* 2>/dev/null || true

# Target directory cleanup (50GB max)
if [ -d "target" ]; then
    TARGET_SIZE=$(du -s target | awk '{print $1}') # KB
    MAX_SIZE_50GB=$((50 * 1024 * 1024))
    if [ "$TARGET_SIZE" -gt "$MAX_SIZE_50GB" ]; then
        log "Target directory ($(($TARGET_SIZE/1024/1024))GB) exceeds 50GB. Deleting..."
        rm -rf target
    else
        log "Target directory within limits ($(($TARGET_SIZE/1024))MB)."
    fi
fi

# --- 5. Project-Specific Cleanup ---
log "Cleaning project-specific caches and logs..."
[ -d "logs" ] && rm -rf logs/* && touch logs/.gitkeep
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true

# --- 6. Tool-Specific Cache Cleanup ---
log "Cleaning tool caches..."
command_exists docker && docker system prune -f --volumes >/dev/null 2>&1 && log "Docker cleaned."
command_exists npm    && npm cache clean --force >/dev/null 2>&1 && log "NPM cleaned."
command_exists pip    && pip cache purge >/dev/null 2>&1 && log "Pip cleaned."
command_exists uv     && uv cache clean >/dev/null 2>&1 && log "UV cleaned."
command_exists poetry && poetry cache clear pypi --all --no-interaction >/dev/null 2>&1 && log "Poetry cleaned."

# --- 7. System & Memory Optimization ---
log "Performing system optimization..."
command_exists apt-get && sudo apt-get clean
rm -rf /tmp/* 2>/dev/null || true
rm -rf ~/.cache/thumbnails/* 2>/dev/null || true

log "Dropping memory caches..."
sync
[ -w /proc/sys/vm/drop_caches ] && sudo sh -c "echo 3 > /proc/sys/vm/drop_caches"

# --- Summary ---
log "Optimization completed!"
FINAL_DISK=$(df -h / | awk 'NR==2 {print $4}')
FINAL_MEM=$(free -h | awk '/^Mem:/ {print $7}')
log "Disk: $INITIAL_DISK → $FINAL_DISK"
log "Memory: $INITIAL_MEM → $FINAL_MEM"