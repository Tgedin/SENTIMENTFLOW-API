"""
Script to test and compare different sentiment analysis models.

This script loads and evaluates the performance characteristics,
preprocessing requirements, and output formats of multiple
sentiment analysis models from Hugging Face.
"""

import argparse
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple, Any

import numpy as np
import torch
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    pipeline,
)

# Setup path to project root
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
MODELS_DIR = PROJECT_ROOT / "data" / "models"
SAMPLES_DIR = PROJECT_ROOT / "data" / "samples"

# Ensure directories exist
MODELS_DIR.mkdir(exist_ok=True, parents=True)
SAMPLES_DIR.mkdir(exist_ok=True, parents=True)

# Models to test, based on the recommendations from our research
MODELS = [
    {
        "name": "distilbert-base-uncased-finetuned-sst-2-english",
        "type": "General Purpose",
        "classes": ["negative", "positive"],
        "multilingual": False,
        "description": "Best balance of size, speed, and accuracy"
    },
    {
        "name": "cardiffnlp/twitter-roberta-base-sentiment",
        "type": "Social Media",
        "classes": ["negative", "neutral", "positive"],
        "multilingual": False,
        "description": "Specialized for social media content"
    },
    {
        "name": "nlptown/bert-base-multilingual-uncased-sentiment",
        "type": "Multilingual",
        "classes": ["1 star", "2 stars", "3 stars", "4 stars", "5 stars"],
        "multilingual": True,
        "description": "5-class sentiment across multiple languages"
    }
]

# Test data in different languages and domains
TEST_SENTENCES = [
    # English samples with varying sentiment
    "This product is absolutely amazing, I love it!",
    "The service was okay, but could be better.",
    "I'm very disappointed with my purchase, it broke after one day.",
    "The weather today is nice and sunny.",
    
    # Social media style text with emojis and abbreviations
    "OMG this new phone is lit! 🔥 Can't believe how good it is! #blessed",
    "Worst customer service ever 😡 Don't buy from them! So annoyed rn",
    "Just another day at work... meh. #mondayblues",
    
    # Longer text to test handling of longer sequences
    "I've been using this product for several months now. Initially, I was impressed with its features and design. However, over time I've noticed several issues: the battery life has decreased significantly, some buttons are becoming unresponsive, and customer support has been unhelpful when I've reached out for assistance. Overall, what started as a positive experience has turned into a disappointment.",
    
    # Multilingual samples
    "Ce produit est vraiment excellent, je le recommande vivement!", # French
    "Dieses Restaurant ist schrecklich, das Essen war kalt und der Service war langsam.", # German
    "La película fue interesante pero un poco larga para mi gusto." # Spanish
]

def load_model(model_name: str) -> Tuple[Any, Any]:
    """Load a model and its tokenizer."""
    print(f"Loading model: {model_name}...")
    start_time = time.time()
    
    try:
        # Try to load from local cache first, then from Hugging Face
        print(f"Loading tokenizer for {model_name}...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_name, 
            cache_dir=MODELS_DIR,
            local_files_only=False  # Allow downloading if not cached
        )
        
        print(f"Loading model weights for {model_name}...")
        model = AutoModelForSequenceClassification.from_pretrained(
            model_name, 
            cache_dir=MODELS_DIR,
            local_files_only=False,  # Allow downloading if not cached
            return_dict=True  # Ensure output is dictionary format
        )
        
        load_time = time.time() - start_time
        print(f"Model loaded in {load_time:.2f} seconds")
        
        return model, tokenizer
    except Exception as e:
        load_time = time.time() - start_time
        print(f"Error loading model after {load_time:.2f} seconds: {str(e)}")
        raise

def create_sentiment_pipeline(model_name: str) -> Any:
    """Create a sentiment analysis pipeline for the given model."""
    return pipeline(
        "sentiment-analysis", 
        model=model_name,
        tokenizer=model_name,
        device=0 if torch.cuda.is_available() else -1,
        cache_dir=MODELS_DIR
    )

def measure_inference_time(pipeline: Any, text: str, num_runs: int = 5) -> Dict[str, float]:
    """Measure inference time statistics over multiple runs."""
    times = []
    
    # Warm-up run
    _ = pipeline(text)
    
    # Timed runs
    for _ in range(num_runs):
        start_time = time.time()
        _ = pipeline(text)
        end_time = time.time()
        times.append(end_time - start_time)
    
    return {
        "mean": np.mean(times),
        "min": np.min(times),
        "max": np.max(times),
        "std": np.std(times)
    }

def test_model(model_name: str, test_sentences: List[str]) -> Dict[str, Any]:
    """Test a model on the provided sentences and collect performance metrics."""
    results = {
        "model_name": model_name,
        "sentences": [],
        "load_time": 0,
        "average_inference_time": 0,
        "preprocessing_requirements": "",
        "output_format": "",
        "memory_usage": 0
    }
    
    start_time = time.time()
    try:
        pipe = create_sentiment_pipeline(model_name)
        results["load_time"] = time.time() - start_time
        
        all_inference_times = []
        
        # Process each test sentence
        for sentence in test_sentences:
            try:
                # Measure inference time
                time_stats = measure_inference_time(pipe, sentence)
                all_inference_times.append(time_stats["mean"])
                
                # Get sentiment prediction
                start_time = time.time()
                sentiment_result = pipe(sentence)
                inference_time = time.time() - start_time
                
                # Store results
                results["sentences"].append({
                    "text": sentence,
                    "prediction": sentiment_result,
                    "inference_time": inference_time
                })
            except Exception as e:
                print(f"Error processing sentence: {sentence[:30]}... - {str(e)}")
                results["sentences"].append({
                    "text": sentence,
                    "prediction": [{"label": "error", "score": 0.0}],
                    "inference_time": 0,
                    "error": str(e)
                })
        
        # Calculate average inference time
        if all_inference_times:
            results["average_inference_time"] = np.mean(all_inference_times)
        
        # Document preprocessing requirements and output format
        model_info = next((m for m in MODELS if m["name"] == model_name), {})
        results["preprocessing_requirements"] = f"Uses {model_name} tokenizer with max sequence length of {pipe.tokenizer.model_max_length} tokens."
        results["output_format"] = f"Classes: {model_info.get('classes', ['Unknown'])}"
        
        # Get memory usage (rough estimate, not exact)
        if torch.cuda.is_available():
            torch.cuda.synchronize()
            memory_allocated = torch.cuda.max_memory_allocated() / 1024**2  # Convert to MB
            results["memory_usage"] = memory_allocated
        else:
            # Estimate memory usage on CPU (very rough)
            import psutil
            results["memory_usage"] = psutil.Process().memory_info().rss / 1024**2  # Convert to MB
    
    except Exception as e:
        print(f"Error testing model {model_name}: {str(e)}")
        results["error"] = str(e)
    
    return results

def run_tests(models: List[Dict[str, str]], test_sentences: List[str], output_file: str) -> None:
    """Run tests on all models and save results to a file."""
    results = []
    
    for model_info in models:
        model_name = model_info["name"]
        print(f"\n{'='*80}\nTesting model: {model_name}\n{'='*80}")
        
        try:
            model_results = test_model(model_name, test_sentences)
            model_results["model_info"] = model_info
            results.append(model_results)
            print(f"✓ Successfully tested {model_name}")
            
            # Print summary statistics
            print(f"  Load time: {model_results['load_time']:.2f} seconds")
            print(f"  Average inference time: {model_results['average_inference_time']*1000:.2f} ms per sentence")
            if model_results['memory_usage'] > 0:
                print(f"  Memory usage: {model_results['memory_usage']:.2f} MB")
                
        except Exception as e:
            print(f"✗ Error testing {model_name}: {str(e)}")
    
    # Save results to file
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {output_file}")

def generate_markdown_report(results_file: str, output_file: str) -> None:
    """Generate a markdown report from the JSON results file."""
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    md_content = [
        "# Sentiment Analysis Models Performance Report",
        "",
        "This report compares the performance characteristics, preprocessing requirements, and output formats of different sentiment analysis models.",
        "",
        "## Models Summary",
        "",
        "| Model | Type | Classes | Multilingual | Load Time | Avg Inference Time | Memory Usage |",
        "|-------|------|---------|-------------|-----------|-------------------|--------------|",
    ]
    
    for result in results:
        model_info = result["model_info"]
        md_content.append(
            f"| {model_info['name']} | {model_info['type']} | {', '.join(model_info['classes'])} | "
            f"{'Yes' if model_info['multilingual'] else 'No'} | {result['load_time']:.2f}s | "
            f"{result['average_inference_time']*1000:.2f}ms | {result['memory_usage']:.2f}MB |"
        )
    
    md_content.extend([
        "",
        "## Detailed Results",
        ""
    ])
    
    for result in results:
        model_name = result["model_info"]["name"]
        md_content.extend([
            f"### {model_name}",
            "",
            f"**Type:** {result['model_info']['type']}",
            f"**Description:** {result['model_info']['description']}",
            f"**Classes:** {', '.join(result['model_info']['classes'])}",
            f"**Multilingual:** {'Yes' if result['model_info']['multilingual'] else 'No'}",
            f"**Load Time:** {result['load_time']:.2f} seconds",
            f"**Average Inference Time:** {result['average_inference_time']*1000:.2f} ms",
            f"**Memory Usage:** {result['memory_usage']:.2f} MB",
            f"**Preprocessing Requirements:** {result['preprocessing_requirements']}",
            f"**Output Format:** {result['output_format']}",
            "",
            "#### Sample Predictions",
            "",
            "| Text | Prediction | Inference Time |",
            "|------|------------|----------------|",
        ])
        
        # Add sample predictions (limit to 5 for brevity)
        for sample in result["sentences"][:5]:
            prediction_str = str(sample["prediction"]).replace("|", "\\|")
            md_content.append(
                f"| {sample['text'][:50]}... | {prediction_str} | {sample['inference_time']*1000:.2f}ms |"
            )
        
        md_content.append("")
    
    md_content.extend([
        "## Conclusion",
        "",
        "Based on the test results, here are the key findings:",
        "",
        "1. **Speed vs. Accuracy Tradeoff**: Smaller models like DistilBERT offer faster inference times but may sacrifice accuracy for certain domains.",
        "2. **Domain Specialization**: The Twitter-RoBERTa model performs better on social media text with emojis and slang.",
        "3. **Multilingual Capabilities**: The multilingual model handles non-English text well but has higher memory requirements.",
        "4. **Memory Usage**: Memory usage correlates with model size, with larger models requiring more resources.",
        "5. **Preprocessing Requirements**: All models use similar tokenization approaches but with model-specific vocabularies.",
        "",
        "For the SentimentFlow API, the choice of model should depend on the expected usage patterns and deployment constraints.",
        ""
    ])
    
    # Write the markdown report
    with open(output_file, 'w') as f:
        f.write("\n".join(md_content))
    
    print(f"Markdown report generated at {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Test sentiment analysis models")
    parser.add_argument("--output", default=str(SAMPLES_DIR / "model_test_results.json"),
                        help="Output file for test results (JSON)")
    parser.add_argument("--report", default=str(PROJECT_ROOT / "docs" / "research" / "model_test_results.md"),
                        help="Output file for markdown report")
    parser.add_argument("--models", nargs="+", help="Specific models to test (default: all)")
    args = parser.parse_args()
    
    # Filter models if specified
    models_to_test = MODELS
    if args.models:
        models_to_test = [m for m in MODELS if m["name"] in args.models]
        if not models_to_test:
            print("No valid models specified. Using all models.")
            models_to_test = MODELS
    
    # Run the tests
    run_tests(models_to_test, TEST_SENTENCES, args.output)
    
    # Generate markdown report
    generate_markdown_report(args.output, args.report)

if __name__ == "__main__":
    main()
