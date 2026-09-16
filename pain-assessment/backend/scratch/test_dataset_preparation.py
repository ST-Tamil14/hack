from app.services.dataset_service import prepare_facial_dataset

def test_dataset_preparation():
    result = prepare_facial_dataset("sample_annotations.csv")
    print("Dataset Preparation Result:")
    print("Total Records:", result["total_records"])
    print("Total Patients:", result["total_patients"])
    print("Split Counts:", result["split_counts"])
    print("Output Paths:", result["output_paths"])

    assert result["total_records"] == 6
    assert result["total_patients"] == 5
    assert result["split_counts"]["train"] + result["split_counts"]["validation"] + result["split_counts"]["test"] == 6
    print("Dataset preparation test passed successfully!")

if __name__ == "__main__":
    test_dataset_preparation()
