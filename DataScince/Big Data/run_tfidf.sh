#!/bin/bash

DATA_DIR="data"
TF_OUT="tf_output.txt"
TFIDF_OUT="tfidf_output.txt"
DECODED_OUT="tfidf_decoded.txt"

echo "=== Running TFJob ==="
python tf_job.py ${DATA_DIR}/*.txt > "${TF_OUT}"

DOCS_COUNT=$(ls ${DATA_DIR}/*.txt | wc -l)
echo "Processing ${DOCS_COUNT} documents"

echo "=== Running TFIDFJob ==="
python tfidf_job.py "${TF_OUT}" --total_docs "${DOCS_COUNT}" > "${TFIDF_OUT}"

echo "=== DECODING RESULTS ==="
python decode_output.py < "${TFIDF_OUT}" > "${DECODED_OUT}"

echo "=== FINAL RESULTS ==="
echo "TF-IDF output (decoded):"
cat "${DECODED_OUT}"

echo "=== Done ==="
echo "Raw output: ${TFIDF_OUT}"
echo "Decoded output: ${DECODED_OUT}"



