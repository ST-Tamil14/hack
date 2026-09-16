from app.services.intervention_service import calculate_intervention_response

def test_intervention_response():
    # Test improved response (<= -0.05)
    status, change = calculate_intervention_response(pre_score=0.78, post_score=0.51)
    print(f"0.78 -> 0.51: status={status}, change={change}")
    assert status == "improved"
    assert change == -0.27

    # Test increased response (>= +0.05)
    status, change = calculate_intervention_response(pre_score=0.45, post_score=0.62)
    print(f"0.45 -> 0.62: status={status}, change={change}")
    assert status == "increased"
    assert change == 0.17

    # Test unchanged response (within 0.05)
    status, change = calculate_intervention_response(pre_score=0.50, post_score=0.52)
    print(f"0.50 -> 0.52: status={status}, change={change}")
    assert status == "unchanged"
    assert change == 0.02

    # Test insufficient data (missing pre or post score)
    status, change = calculate_intervention_response(pre_score=0.60, post_score=None)
    print(f"0.60 -> None: status={status}, change={change}")
    assert status == "insufficient_data"
    assert change is None

    print("Intervention response tests passed successfully!")

if __name__ == "__main__":
    test_intervention_response()
