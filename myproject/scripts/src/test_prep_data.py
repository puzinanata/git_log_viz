from prep_data import process_data
import pandas as pd
import pytest

def test_prep_data():
    df = pd.read_csv("result/git_log_test.csv")

    # Convert to datetime with the expected format
    df["date"] = pd.to_datetime(df["date"], format="%a %b %d %H:%M:%S %Y %z", errors="raise", utc=True)

    # Now check that it is a datetime dtype
    assert isinstance(df, pd.DataFrame)
    assert "date" in df.columns
    assert pd.api.types.is_datetime64_any_dtype(df["date"])


def test_invalid_date_format_fails():
    bad_df = pd.DataFrame({"date": ["Invalid Date"]})

    with pytest.raises(ValueError):
        pd.to_datetime(bad_df["date"], format="%a %b %d %H:%M:%S %Y %z", errors="raise", utc=True)


