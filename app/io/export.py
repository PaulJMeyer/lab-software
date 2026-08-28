from pathlib import Path
import pandas as pd

# Only base sample data is exported for now (ID, DNA sequence).
# Analysis results and mutation-match data may be added as extra
# columns in a future iteration.
EXPORT_COLUMNS = ["sample_id", "sample_dna"]


def _samples_to_dataframe(samples) -> pd.DataFrame:
    data = [{"sample_id": s.sample_id, "sample_dna": s.sample_dna} for s in samples]
    return pd.DataFrame(data, columns=EXPORT_COLUMNS)


def export_to_csv(samples, path: Path) -> None:
    """Export samples (base data only) to a CSV file, creating parent directories if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df = _samples_to_dataframe(samples)
    df.to_csv(path, index=False)


def export_to_excel(samples, path: Path) -> None:
    """Export samples (base data only) to an Excel (.xlsx) file, creating parent directories if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df = _samples_to_dataframe(samples)
    df.to_excel(path, index=False)
