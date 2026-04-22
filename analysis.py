"""Analysis module for data processing."""

import math
import statistics


def analyze_numbers(numbers: list[float]) -> dict:
    """Analyze a list of numbers and return statistics."""
    if not numbers:
        return {"error": "Empty list provided"}

    return {
        "mean": statistics.mean(numbers),
        "median": statistics.median(numbers),
        "stdev": statistics.stdev(numbers) if len(numbers) > 1 else 0.0,
        "sqrt_mean": math.sqrt(abs(statistics.mean(numbers))),
        "count": len(numbers),
    }


if __name__ == "__main__":
    data = [1.0, 2.5, 3.7, 4.2, 5.8, 6.1, 7.3]
    result = analyze_numbers(data)
    for key, value in result.items():
        print(f"{key}: {value}")
