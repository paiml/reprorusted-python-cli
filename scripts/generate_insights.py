#!/usr/bin/python3
"""Generate corpus insights with Tarantula fault localization scores."""

import json
import pyarrow.parquet as pq
from pathlib import Path

def main():
    # Load the corpus
    corpus_path = Path(__file__).parent.parent / "data" / "depyler_citl_corpus_uncompressed.parquet"
    df = pq.read_table(corpus_path).to_pandas()

    # Tarantula suspiciousness scores from our analysis
    tarantula_scores = {
        "async_await": 0.946,
        "generator": 0.927,
        "lambda": 0.783,
        "context_manager": 0.652,
        "class_definition": 0.612,
        "exception_handling": 0.577,
        "stdin_usage": 0.566,
        "list_comprehension": 0.538,
        "import_statement": 0.500,
        "function_definition": 0.500,
        "walrus_operator": 0.850,
        "generator_expression": 0.890,
    }

    # Feature detection patterns for Python code
    feature_patterns = {
        "async_await": ["async def", "await ", "asyncio"],
        "generator": ["yield ", "yield("],
        "lambda": ["lambda "],
        "context_manager": ["with ", "__enter__", "__exit__"],
        "class_definition": ["class "],
        "exception_handling": ["try:", "except ", "raise "],
        "stdin_usage": ["stdin", "input("],
        "walrus_operator": [":="],
        "decorator": ["@"],
        "multiprocessing": ["multiprocessing", "Pool", "Process"],
        "functools": ["functools", "partial", "reduce"],
        "eval_exec": ["eval(", "exec("],
    }

    def detect_features(code):
        """Detect Python features in code."""
        features = []
        if not code:
            return features
        for feature, patterns in feature_patterns.items():
            if any(p in code for p in patterns):
                features.append(feature)
        return features

    # Analyze each category
    category_insights = {}
    for _, row in df.iterrows():
        cat = row['category']
        python_code = row['python_code'] if row['python_code'] else ""
        has_rust = row['has_rust']

        if cat not in category_insights:
            category_insights[cat] = {
                "total_examples": 0,
                "with_rust": 0,
                "features_detected": set(),
                "blocking_features": set(),
            }

        category_insights[cat]["total_examples"] += 1
        if has_rust:
            category_insights[cat]["with_rust"] += 1

        features = detect_features(python_code)
        category_insights[cat]["features_detected"].update(features)

        if not has_rust:
            category_insights[cat]["blocking_features"].update(features)

    # Convert sets to lists
    for cat in category_insights:
        category_insights[cat]["features_detected"] = list(category_insights[cat]["features_detected"])
        category_insights[cat]["blocking_features"] = list(category_insights[cat]["blocking_features"])
        category_insights[cat]["success_rate"] = round(
            category_insights[cat]["with_rust"] / category_insights[cat]["total_examples"] * 100, 1
        )

    # Identify categories with 0% success
    zero_success_categories = [
        cat for cat, info in category_insights.items()
        if info["success_rate"] == 0
    ]

    # Calculate feature impact
    feature_impact = {}
    for cat, info in category_insights.items():
        if info["success_rate"] < 100:
            for feat in info["blocking_features"]:
                if feat not in feature_impact:
                    feature_impact[feat] = {"affected_categories": [], "count": 0}
                feature_impact[feat]["affected_categories"].append(cat)
                feature_impact[feat]["count"] += 1

    # Add suspiciousness scores
    for feat in feature_impact:
        feature_impact[feat]["suspiciousness"] = tarantula_scores.get(feat, 0.5)

    # Sort features by impact
    sorted_features = sorted(
        feature_impact.items(),
        key=lambda x: (x[1]["suspiciousness"], x[1]["count"]),
        reverse=True
    )

    # Priority recommendations
    priority_features = []
    for feat, info in sorted_features[:10]:
        priority_features.append({
            "feature": feat,
            "suspiciousness": info["suspiciousness"],
            "affected_categories": info["count"],
            "categories": info["affected_categories"][:5],
            "priority": "HIGH" if info["suspiciousness"] > 0.7 else "MEDIUM"
        })

    # Build final insights
    insights = {
        "generated": "2025-11-30",
        "corpus_version": "1.0",
        "summary": {
            "total_pairs": len(df),
            "with_rust": int(df['has_rust'].sum()),
            "success_rate": round(df['has_rust'].mean() * 100, 1),
            "total_categories": len(category_insights),
            "zero_success_categories": len(zero_success_categories),
        },
        "tarantula_fault_localization": {
            "description": "Suspiciousness scores from Tarantula algorithm - higher means more correlated with failures",
            "scores": tarantula_scores,
        },
        "priority_features_to_implement": priority_features,
        "zero_success_categories": zero_success_categories,
        "category_insights": category_insights,
    }

    output_path = Path(__file__).parent.parent / "data" / "corpus_insights.json"
    with open(output_path, 'w') as f:
        json.dump(insights, f, indent=2)

    print(f"Generated insights for {len(category_insights)} categories")
    print(f"Zero success categories: {len(zero_success_categories)}")
    print(f"Priority features: {len(priority_features)}")
    print("\nTop priority features to implement:")
    for pf in priority_features[:5]:
        print(f"  - {pf['feature']}: suspiciousness={pf['suspiciousness']}, affects {pf['affected_categories']} categories")
    print(f"\nSaved to: {output_path}")


if __name__ == "__main__":
    main()
