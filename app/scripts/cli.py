import click
from pathlib import Path
from app.domain.models import Sample
from app.services.lab_service import LabService
from app.io.storage_json import save_samples, load_samples

DATA_PATH = Path("data/lab_state.json")

def get_service():
    service = LabService()
    loaded = load_samples(DATA_PATH)
    service.set_state(loaded)
    return service

@click.group()
def cli():
    """Lab Software CLI"""
    pass

@cli.command()
@click.option("--id", "sample_id", required=True, prompt="Sample ID", help="Eindeutige Sample-ID")
@click.option("--dna", "sample_dna", required=True, prompt="DNA-Sequenz", help="DNA-Sequenz des Samples")
def add(sample_id, sample_dna):
    """Neues Sample registrieren"""
    service = get_service()
    sample = Sample(sample_id=sample_id, sample_dna=sample_dna)
    try:
        service.add_sample(sample)
        save_samples(DATA_PATH, service.get_state())
        click.echo(click.style(f"✓ Sample '{sample_id}' erfolgreich hinzugefügt.", fg="green"))
    except ValueError as e:
        click.echo(click.style(f"✗ Fehler: {e}", fg="red"))

@cli.command(name="list")
def list_samples():
    """Alle registrierten Samples anzeigen"""
    service = get_service()
    samples = service.list_samples()
    if not samples:
        click.echo("Keine Samples vorhanden.")
        return
    click.echo(f"\n{'ID':<20} {'DNA-Länge':<12} {'Sequenz (Vorschau)'}")
    click.echo("-" * 55)
    for s in samples:
        preview = s.sample_dna[:20] + "..." if len(s.sample_dna) > 20 else s.sample_dna
        click.echo(f"{s.sample_id:<20} {len(s.sample_dna):<12} {preview}")
    click.echo(f"\n{len(samples)} Sample(s) insgesamt.")

@cli.command()
@click.option("--id", "sample_id", required=True, prompt="Sample ID", help="Sample-ID zum Löschen")
def delete(sample_id):
    """Sample anhand der ID löschen"""
    service = get_service()
    try:
        service.delete_sample(sample_id)
        save_samples(DATA_PATH, service.get_state())
        click.echo(click.style(f"✓ Sample '{sample_id}' erfolgreich gelöscht.", fg="green"))
    except ValueError as e:
        click.echo(click.style(f"✗ Fehler: {e}", fg="red"))

@cli.command()
@click.option("--id", "sample_id", required=True, prompt="Sample ID", help="Sample-ID zum Suchen")
def search(sample_id):
    """Sample anhand der ID suchen"""
    service = get_service()
    sample = service.find_sample(sample_id)
    if sample is None:
        click.echo(click.style(f"✗ Kein Sample mit ID '{sample_id}' gefunden.", fg="red"))
    else:
        click.echo(f"\nID:       {sample.sample_id}")
        click.echo(f"DNA:      {sample.sample_dna}")
        click.echo(f"Länge:    {len(sample.sample_dna)} Basen")

if __name__ == "__main__":
    cli()