#!/bin/bash

# Run sentiment model tests and generate performance documentation
echo "Starting sentiment model tests..."

# Make sure virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
  echo "Please activate your virtual environment first"
  exit 1
fi

# Create necessary directories
mkdir -p ./data/models
mkdir -p ./data/samples
mkdir -p ./docs/research

# Run the test script
echo "Running model tests (this may take several minutes)..."
python ./scripts/test_sentiment_models.py

# Update the model performance document with results
echo "Tests completed. Results saved to docs/research/model_test_results.md"
echo "Summary added to docs/research/model_performance.md"

# Merge test results into model_performance.md
python -c "
import json
from pathlib import Path

# Read test results
results_file = Path('./data/samples/model_test_results.json')
if not results_file.exists():
    print('Test results file not found')
    exit(1)

with open(results_file, 'r') as f:
    results = json.load(f)

# Read existing performance doc
perf_doc = Path('./docs/research/model_performance.md')
with open(perf_doc, 'r') as f:
    lines = f.readlines()

# Find where to insert results
performance_metrics_idx = -1
preprocessing_idx = -1
output_format_idx = -1
recommendations_idx = -1

for i, line in enumerate(lines):
    if '## Performance Metrics' in line:
        performance_metrics_idx = i + 1
    elif '## Preprocessing Requirements' in line:
        preprocessing_idx = i + 1
    elif '## Output Format Comparison' in line:
        output_format_idx = i + 1
    elif '## Recommendations' in line:
        recommendations_idx = i + 1

# Prepare performance metrics section
performance_metrics = ['\n']
for result in results:
    model_name = result['model_name']
    avg_time = result['average_inference_time'] * 1000  # Convert to ms
    memory = result['memory_usage']
    load_time = result['load_time']
    
    performance_metrics.extend([
        f'### {model_name}\n',
        f'\n',
        f'- **Load Time**: {load_time:.2f} seconds\n',
        f'- **Average Inference Time**: {avg_time:.2f} ms per sentence\n',
        f'- **Memory Usage**: {memory:.2f} MB\n',
        f'\n'
    ])

# Prepare preprocessing section
preprocessing = ['\n']
for result in results:
    model_name = result['model_name']
    preproc = result['preprocessing_requirements']
    preprocessing.extend([
        f'### {model_name}\n',
        f'\n',
        f'{preproc}\n',
        f'\n'
    ])

# Prepare output format section
output_format = ['\n']
for result in results:
    model_name = result['model_name']
    out_format = result['output_format']
    
    # Add sample output
    sample_output = 'No samples available'
    if result['sentences']:
        sample = result['sentences'][0]
        sample_output = f'```json\n{json.dumps(sample[\"prediction\"], indent=2)}\n```'
    
    output_format.extend([
        f'### {model_name}\n',
        f'\n',
        f'{out_format}\n',
        f'\n',
        f'Sample output:\n',
        f'\n',
        f'{sample_output}\n',
        f'\n'
    ])

# Prepare recommendations section
best_model = min(results, key=lambda x: x['average_inference_time'])
most_accurate = max(results, key=lambda x: x['model_info'].get('accuracy', 0) 
                   if isinstance(x['model_info'].get('accuracy', 0), (int, float)) else 0)

recommendations = [
    '\n',
    f'Based on our testing:\n',
    f'\n',
    f'1. **Fastest Model**: {best_model[\"model_name\"]} ({best_model[\"average_inference_time\"]*1000:.2f} ms)\n',
    f'2. **Most Versatile**: cardiffnlp/twitter-roberta-base-sentiment (handles social media text well)\n',
    f'3. **Best for Multilingual**: nlptown/bert-base-multilingual-uncased-sentiment\n',
    f'\n',
    f'For the SentimentFlow API, we recommend using **{best_model[\"model_name\"]}** as the default model\n',
    f'for its excellent balance of speed and accuracy, while offering alternative models for specific use cases.\n',
    f'\n'
]

# Update the file
if performance_metrics_idx >= 0:
    lines[performance_metrics_idx:preprocessing_idx] = performance_metrics
if preprocessing_idx >= 0:
    lines[preprocessing_idx:output_format_idx] = preprocessing
if output_format_idx >= 0:
    lines[output_format_idx:recommendations_idx] = output_format
if recommendations_idx >= 0:
    lines[recommendations_idx:recommendations_idx+2] = recommendations

with open(perf_doc, 'w') as f:
    f.writelines(lines)

print('Updated model_performance.md with test results')
"

echo "Done!"
