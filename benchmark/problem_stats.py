#!/usr/bin/env python

import json
from collections import defaultdict
from pathlib import Path

import yaml


def load_results(dirname):
    """Load all result files from a benchmark directory"""
    dirname = Path(dirname)
    benchmark_dir = Path("tmp.benchmarks") / dirname
    if not benchmark_dir.exists():
        return None

    all_results = []
    for fname in benchmark_dir.glob("*/.aider.results.json"):
        try:
            results = json.loads(fname.read_text())
            all_results.append(results)
        except json.JSONDecodeError:
            print(f"Failed to parse {fname}")
            continue
    return all_results


def analyze_exercise_solutions():
    # Load the leaderboard data
    with open("aider/website/_data/edit_leaderboard.yml") as f:
        leaderboard = yaml.safe_load(f)

    # Track which models solved each exercise
    exercise_solutions = defaultdict(list)

    for entry in leaderboard:
        dirname = entry["dirname"]
        model = entry["model"]

        results = load_results(dirname)
        if not results:
            print(f"Could not load results for {dirname}")
            continue

        for result in results:
            testcase = result.get("testcase")
            if not testcase:
                continue

            # Consider it solved if the last test attempt passed
            tests_outcomes = result.get("tests_outcomes", [])
            if tests_outcomes and tests_outcomes[-1]:
                exercise_solutions[testcase].append(model)

    # Print per-exercise statistics
    print("\nExercise Solution Statistics:")
    print("-" * 40)

    # Sort by number of models that solved each exercise
    sorted_exercises = sorted(exercise_solutions.items(), key=lambda x: len(x[1]), reverse=True)

    # Calculate max length for alignment
    max_name_len = max(len(testcase) for testcase, _ in sorted_exercises)
    total_models = len({model for models in exercise_solutions.values() for model in models})

    for testcase, models in sorted_exercises:
        num_solved = len(models)
        percent = (num_solved / total_models) * 100
        print(f"{testcase:<{max_name_len}} : {num_solved:>3} solved ({percent:>5.1f}%)")

    print("\nSummary:")
    print(f"Total exercises solved at least once: {len(exercise_solutions)}")
    never_solved = 133 - len(exercise_solutions)
    print(f"Never solved by any model: {never_solved}")


if __name__ == "__main__":
    analyze_exercise_solutions()