#!/bin/bash
#
# VRAM Optimization Testing Script
#
# This script tests different VRAM configurations to measure performance impact
# on MiniMax M2.1 models.
#
# Usage:
#   ./scripts/benchmark_vram.sh --model mlx-community/MiniMax-M2.1-4bit
#   ./scripts/benchmark_vram.sh --model mlx-community/MiniMax-M2.1-8bit
#   ./scripts/benchmark_vram.sh --gguf ~/models/MiniMax-M2.1-Q4_K_M.gguf
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
MODEL=""
GGUF_MODEL=""
OUTPUT_DIR="docs/test-results/vram-optimization"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# VRAM configurations to test (in MB)
VRAM_CONFIGS=(
    "0:default"          # System default (~384GB on 512GB system)
    "458752:448gb"       # 448GB (recommended)
    "491520:480gb"       # 480GB (aggressive)
)

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --model)
            MODEL="$2"
            shift 2
            ;;
        --gguf)
            GGUF_MODEL="$2"
            shift 2
            ;;
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --model MODEL        MLX model to test (e.g., mlx-community/MiniMax-M2.1-4bit)"
            echo "  --gguf PATH          GGUF model to test (e.g., ~/models/model.gguf)"
            echo "  --output-dir DIR     Output directory (default: docs/test-results/vram-optimization)"
            echo "  --help               Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 --model mlx-community/MiniMax-M2.1-4bit"
            echo "  $0 --gguf ~/models/MiniMax-M2.1-Q4_K_M.gguf"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Validate inputs
if [ -z "$MODEL" ] && [ -z "$GGUF_MODEL" ]; then
    echo -e "${RED}Error: Either --model or --gguf must be specified${NC}"
    echo "Use --help for usage information"
    exit 1
fi

if [ -n "$MODEL" ] && [ -n "$GGUF_MODEL" ]; then
    echo -e "${RED}Error: Cannot specify both --model and --gguf${NC}"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Determine test type
if [ -n "$MODEL" ]; then
    TEST_TYPE="mlx"
    TEST_MODEL="$MODEL"
else
    TEST_TYPE="llama"
    TEST_MODEL="$GGUF_MODEL"
fi

MODEL_SHORT=$(basename "$TEST_MODEL" | sed 's/[^a-zA-Z0-9-]/_/g' | tr '[:upper:]' '[:lower:]')

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}VRAM Optimization Testing${NC}"
echo -e "${BLUE}================================${NC}"
echo ""
echo -e "Test type: ${GREEN}$TEST_TYPE${NC}"
echo -e "Model: ${GREEN}$TEST_MODEL${NC}"
echo -e "Output: ${GREEN}$OUTPUT_DIR${NC}"
echo -e "Timestamp: ${GREEN}$TIMESTAMP${NC}"
echo ""

# Check current VRAM setting
CURRENT_VRAM=$(sysctl -n iogpu.wired_limit_mb 2>/dev/null || echo "unknown")
echo -e "Current VRAM limit: ${YELLOW}${CURRENT_VRAM} MB${NC}"
echo ""

# Summary file
SUMMARY_FILE="$OUTPUT_DIR/summary-${MODEL_SHORT}-${TIMESTAMP}.md"
echo "# VRAM Optimization Test Results" > "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"
echo "**Test Date:** $(date '+%Y-%m-%d %H:%M:%S')" >> "$SUMMARY_FILE"
echo "**Model:** $TEST_MODEL" >> "$SUMMARY_FILE"
echo "**Test Type:** $TEST_TYPE" >> "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"
echo "## Results" >> "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"
echo "| Config | VRAM Limit | TPS | TTFT | Memory | Status |" >> "$SUMMARY_FILE"
echo "|--------|------------|-----|------|--------|--------|" >> "$SUMMARY_FILE"

# Function to get VRAM limit
get_vram_limit() {
    sysctl -n iogpu.wired_limit_mb 2>/dev/null || echo "0"
}

# Function to set VRAM limit
set_vram_limit() {
    local limit=$1
    local name=$2

    if [ "$limit" = "0" ]; then
        echo -e "${YELLOW}Using system default VRAM limit${NC}"
        return 0
    fi

    echo -e "${YELLOW}Setting VRAM limit to ${limit} MB (${name})...${NC}"

    # Check if we need sudo
    if ! sysctl iogpu.wired_limit_mb="${limit}" 2>/dev/null; then
        echo -e "${YELLOW}Requires sudo access...${NC}"
        sudo sysctl iogpu.wired_limit_mb="${limit}"
    fi

    # Verify
    local new_limit=$(get_vram_limit)
    if [ "$new_limit" = "$limit" ] || [ "$limit" = "0" ]; then
        echo -e "${GREEN}✓ VRAM limit set successfully${NC}"
        return 0
    else
        echo -e "${RED}✗ Failed to set VRAM limit (got ${new_limit})${NC}"
        return 1
    fi
}

# Function to parse TPS from output
parse_tps() {
    local output_file=$1
    # Try to extract "Average TPS:" or "avg_tps" from output
    grep -i "average tps\|avg_tps" "$output_file" | grep -oE '[0-9]+\.[0-9]+' | head -1 || echo "N/A"
}

# Function to parse TTFT from output
parse_ttft() {
    local output_file=$1
    # Try to extract "Average TTFT:" or "avg_ttft" from output
    grep -i "average ttft\|avg_ttft" "$output_file" | grep -oE '[0-9]+\.[0-9]+' | head -1 || echo "N/A"
}

# Function to parse peak memory from output
parse_memory() {
    local output_file=$1
    # Try to extract "Peak memory:" from output
    grep -i "peak memory" "$output_file" | grep -oE '[0-9]+\.[0-9]+' | head -1 || echo "N/A"
}

# Run tests for each VRAM configuration
TEST_COUNT=0
for config in "${VRAM_CONFIGS[@]}"; do
    IFS=':' read -r vram_limit vram_name <<< "$config"
    TEST_COUNT=$((TEST_COUNT + 1))

    echo ""
    echo -e "${BLUE}════════════════════════════════${NC}"
    echo -e "${BLUE}Test $TEST_COUNT/${#VRAM_CONFIGS[@]}: $vram_name${NC}"
    echo -e "${BLUE}════════════════════════════════${NC}"
    echo ""

    # Set VRAM limit
    if ! set_vram_limit "$vram_limit" "$vram_name"; then
        echo -e "${RED}Skipping this configuration${NC}"
        echo "| $vram_name | ${vram_limit} MB | - | - | - | Failed to set |" >> "$SUMMARY_FILE"
        continue
    fi

    # Output files
    TEST_OUTPUT="$OUTPUT_DIR/${TEST_TYPE}-${MODEL_SHORT}-${vram_name}-${TIMESTAMP}.log"

    # Run benchmark
    echo -e "${GREEN}Running benchmark...${NC}"

    if [ "$TEST_TYPE" = "mlx" ]; then
        # MLX test
        python scripts/benchmark_mlx.py \
            --model "$MODEL" \
            --output-dir "$OUTPUT_DIR" \
            2>&1 | tee "$TEST_OUTPUT"
        STATUS=$?
    else
        # llama.cpp test
        python scripts/benchmark_llama.py \
            --model "$GGUF_MODEL" \
            --output-dir "$OUTPUT_DIR" \
            2>&1 | tee "$TEST_OUTPUT"
        STATUS=$?
    fi

    # Parse results
    if [ $STATUS -eq 0 ]; then
        TPS=$(parse_tps "$TEST_OUTPUT")
        TTFT=$(parse_ttft "$TEST_OUTPUT")
        MEMORY=$(parse_memory "$TEST_OUTPUT")
        echo "| $vram_name | ${vram_limit} MB | $TPS | ${TTFT}s | ${MEMORY} GB | ✅ Success |" >> "$SUMMARY_FILE"
        echo -e "${GREEN}✓ Test completed successfully${NC}"
    else
        echo "| $vram_name | ${vram_limit} MB | - | - | - | ❌ Failed |" >> "$SUMMARY_FILE"
        echo -e "${RED}✗ Test failed with exit code $STATUS${NC}"
    fi

    # Wait a bit before next test
    if [ $TEST_COUNT -lt ${#VRAM_CONFIGS[@]} ]; then
        echo ""
        echo -e "${YELLOW}Waiting 10 seconds before next test...${NC}"
        sleep 10
    fi
done

# Restore default VRAM setting (optional)
# Uncomment if you want to restore default after tests
# echo ""
# echo -e "${YELLOW}Tests complete. VRAM settings will reset on next restart.${NC}"

echo ""
echo -e "${BLUE}════════════════════════════════${NC}"
echo -e "${BLUE}All Tests Complete!${NC}"
echo -e "${BLUE}════════════════════════════════${NC}"
echo ""
echo -e "Summary saved to: ${GREEN}$SUMMARY_FILE${NC}"
echo ""
echo "View results:"
echo "  cat $SUMMARY_FILE"
echo ""

# Display summary
cat "$SUMMARY_FILE"

echo ""
echo -e "${YELLOW}Note: VRAM settings will revert to default after restart${NC}"
echo ""
