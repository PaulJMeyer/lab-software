import click
from pathlib import Path
from pydantic import ValidationError
from app.domain.models import Sample
from app.services.lab_service import LabService
from app.io.storage_json import save_samples, load_samples
from app.analysis.dna_tools import reverse_complement, transcribe

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
@click.option("--id", "sample_id", required=True, prompt="Sample ID", help="Unique sample ID")
@click.option("--dna", "sample_dna", required=True, prompt="DNA sequence", help="DNA sequence of the sample")
def add(sample_id, sample_dna):
    """Register a new sample"""
    service = get_service()
    try:
        sample = Sample(sample_id=sample_id, sample_dna=sample_dna)
        service.add_sample(sample)
        save_samples(DATA_PATH, service.get_state())
        click.echo(click.style(f"✓ Sample '{sample_id}' added successfully.", fg="green"))
    except (ValidationError, ValueError) as e:
        click.echo(click.style(f"✗ Error: {e}", fg="red"))

@cli.command(name="list")
def list_samples():
    """List all registered samples"""
    service = get_service()
    samples = service.list_samples()
    if not samples:
        click.echo("No samples available.")
        return
    click.echo(f"\n{'ID':<20} {'DNA length':<12} {'Sequence (preview)'}")
    click.echo("-" * 55)
    for s in samples:
        preview = s.sample_dna[:20] + "..." if len(s.sample_dna) > 20 else s.sample_dna
        click.echo(f"{s.sample_id:<20} {len(s.sample_dna):<12} {preview}")
    click.echo(f"\n{len(samples)} sample(s) total.")

@cli.command()
@click.option("--id", "sample_id", required=True, prompt="Sample ID", help="Sample ID to update")
@click.option("--dna", "sample_dna", required=True, prompt="New DNA sequence", help="New DNA sequence of the sample")
def update(sample_id, sample_dna):
    """Update the DNA sequence of an existing sample"""
    service = get_service()
    try:
        service.update_sample(sample_id, sample_dna)
        save_samples(DATA_PATH, service.get_state())
        click.echo(click.style(f"✓ Sample '{sample_id}' updated successfully.", fg="green"))
    except (ValidationError, ValueError) as e:
        click.echo(click.style(f"✗ Error: {e}", fg="red"))

@cli.command()
@click.option("--id", "sample_id", required=True, prompt="Sample ID", help="Sample ID to delete")
def delete(sample_id):
    """Delete a sample by ID"""
    service = get_service()
    try:
        service.delete_sample(sample_id)
        save_samples(DATA_PATH, service.get_state())
        click.echo(click.style(f"✓ Sample '{sample_id}' deleted successfully.", fg="green"))
    except (ValidationError, ValueError) as e:
        click.echo(click.style(f"✗ Error: {e}", fg="red"))

@cli.command()
@click.option("--id", "sample_id", required=True, prompt="Sample ID", help="Sample ID to search for")
def search(sample_id):
    """Search for a sample by ID"""
    service = get_service()
    sample = service.find_sample(sample_id)
    if sample is None:
        click.echo(click.style(f"✗ No sample found with ID '{sample_id}'.", fg="red"))
    else:
        click.echo(f"\nID:       {sample.sample_id}")
        click.echo(f"DNA:      {sample.sample_dna}")
        click.echo(f"Length:   {len(sample.sample_dna)} bases")

@cli.command()
@click.option("--id", "sample_id", required=True, prompt="Sample ID", help="Sample ID to analyze")
def analyze(sample_id):
    """Show the reverse complement and RNA transcript of a sample"""
    service = get_service()
    sample = service.find_sample(sample_id)
    if sample is None:
        click.echo(click.style(f"✗ No sample found with ID '{sample_id}'.", fg="red"))
        return
    click.echo(f"\nID:                 {sample.sample_id}")
    click.echo(f"DNA:                {sample.sample_dna}")
    click.echo(f"Reverse complement: {reverse_complement(sample.sample_dna)}")
    click.echo(f"RNA transcript:     {transcribe(sample.sample_dna)}")

if __name__ == "__main__":  # pragma: no cover
    cli()
