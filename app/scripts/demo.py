from pathlib import Path

from app.domain.models import Sample
from app.services.lab_service import LabService
from app.io.storage_json import save_samples, load_samples


DATA_PATH = Path("data/lab_state.json")


def main():

    service = LabService()

    # Laden
    loaded_samples = load_samples(DATA_PATH)
    service.set_state(loaded_samples)

    print("Loaded samples:")
    for s in service.list_samples():
        print(s)

    # Neues Sample hinzufügen
    sample1 = Sample("987654321", "ACGCTGATGCTAGCCTATCGATCGGATATCGCGAT")

    try:
        service.add_sample(sample1)
        print("Added:", sample1)

    except ValueError as e:
        print("Error:", e)

    print("Current samples:")
    for s in service.list_samples():
        print(s)

    # Speichern
    save_samples(DATA_PATH, service.get_state())


if __name__ == "__main__":
    main()