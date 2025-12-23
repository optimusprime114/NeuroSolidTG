#!/bin/bash

# -------- CONFIG --------
CURRENT_DIR="$(pwd)"
CONTRACT_DIR="$CURRENT_DIR/myproject"
OUTPUT_ROOT="$CURRENT_DIR/results_combined"
HOST_RESULTS_DIR="$CURRENT_DIR/results" # The host directory mapped to Docker
TIMEOUT=40
API_KEY = "<add_api_key_here>"

mkdir -p "$OUTPUT_ROOT"

FAILED_LOG="$OUTPUT_ROOT/failed_contracts.txt"
> "$FAILED_LOG"

echo "📄 Failed contracts will be logged at:"
echo "   $FAILED_LOG"
echo "==============================================="

# -------- RUN TOOL --------
for contract in "$CONTRACT_DIR"/*.sol; do
  if [ ! -f "$contract" ]; then
    echo "⚠️  No Solidity files found in $CONTRACT_DIR"
    exit 0
  fi

  contract_name=$(basename "$contract" .sol)
  echo "🚀 Running NeuroSolidTG (Docker) on: $contract_name.sol"

  # 1. Ensure clean workspace for the Docker output
  # We delete the host results folder so we don't mix previous runs
  rm -rf "$HOST_RESULTS_DIR"
  mkdir -p "$HOST_RESULTS_DIR"

  # 2. Run Docker
  # -v "$CURRENT_DIR:/data": Maps current folder to /data so the tool can find the input file
  # -v "$HOST_RESULTS_DIR:/app/test": Maps host 'results' to container output '/app/test'
  docker run --rm \
      -v "$CURRENT_DIR:/data" \
      -v "$HOST_RESULTS_DIR:/app/test" \
      optimusprime114/neurosolidtg:latest \
      -i "/data/myproject/$contract_name.sol" \
      -t "$TIMEOUT"
      # --apikey "$API_KEY"
    

  RETVAL=$?

  # 3. Handle failure
  # We check exit code AND if the results directory actually contains data
  if [ $RETVAL -ne 0 ] || [ -z "$(ls -A "$HOST_RESULTS_DIR" 2>/dev/null)" ]; then
    echo "❌ FAILED: $contract_name (exit code=$RETVAL)" | tee -a "$FAILED_LOG"
    rm -rf "$HOST_RESULTS_DIR"
    echo "-----------------------------------------------"
    continue
  fi

  # 4. Move output
  # Move the 'results' folder to the destination and rename it to 'test'
  # to match your original script's output structure
  DEST="$OUTPUT_ROOT/test_$contract_name"
  mkdir -p "$DEST"
  
  mv "$HOST_RESULTS_DIR" "$DEST/test"

  echo "✅ Success"
  echo "-----------------------------------------------"
done

# Cleanup empty results dir if left over
if [ -d "$HOST_RESULTS_DIR" ]; then
    rm -rf "$HOST_RESULTS_DIR"
fi

echo "🎉 Processing complete."
echo "📁 Results directory: $OUTPUT_ROOT"

if [ -s "$FAILED_LOG" ]; then
  echo "⚠️  Some contracts failed. See:"
  echo "   $FAILED_LOG"
else
  echo "✅ All contracts processed successfully."
fi