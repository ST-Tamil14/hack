from app.services.assessment_history_service import calculate_trend

def test_trend_calculation():
    # Test increasing trend (>= +0.05)
    direction, change = calculate_trend(current_score=0.58, previous_score=0.40)
    print(f"0.40 -> 0.58: direction={direction}, change={change}")
    assert direction == "increasing"
    assert change == 0.18

    # Test decreasing trend (<= -0.05)
    direction, change = calculate_trend(current_score=0.51, previous_score=0.78)
    print(f"0.78 -> 0.51: direction={direction}, change={change}")
    assert direction == "decreasing"
    assert change == -0.27

    # Test stable trend (within 0.05 threshold)
    direction, change = calculate_trend(current_score=0.62, previous_score=0.60)
    print(f"0.60 -> 0.62: direction={direction}, change={change}")
    assert direction == "stable"
    assert change == 0.02

    # Test unknown trend (missing previous score)
    direction, change = calculate_trend(current_score=0.62, previous_score=None)
    print(f"None -> 0.62: direction={direction}, change={change}")
    assert direction == "unknown"
    assert change is None

    print("Assessment history trend tests passed successfully!")

if __name__ == "__main__":
    test_trend_calculation()
