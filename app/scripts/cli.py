import click
from pathlib import Path
from datetime import datetime
from pydantic import ValidationError
from app.domain.models import Sample, validate_sample_id_format, validate_sample_dna_format
from app.services.lab_service import LabService
from app.io.storage_json import save_samples, load_samples
from app.io.fasta_import import parse_fasta, generate_sample_id
from app.analysis.dna_tools import reverse_complement, transcribe, translate

DATA_PATH = Path("data/lab_state.json")
FASTA_IMPORT_DIR = Path("data/fasta_import")
FASTA_PROCESSED_DIR = FASTA_IMPORT_DIR / "processed"
FASTA_EXTENSIONS = {".fasta", ".fa"}

# Available analyses: (field name on Sample, display label, function computing the result)
ANALYSES = [
    ("reverse_complement", "Reverse complement", reverse_complement),
    ("rna_transcript", "Transcription (DNA to RNA)", transcribe),
    ("protein", "Translation (RNA to protein)", translate),
]

def get_service():
    service = LabService()
    loaded = load_samples(DATA_PATH)
    service.set_state(loaded)
    return service

def validate_id_option(ctx, param, value):
    """Click callback: validates the sample ID as it's entered, reprompting on invalid input."""
    try:
        return validate_sample_id_format(value)
    except ValueError as e:
        raise click.BadParameter(str(e))

def validate_dna_option(ctx, param, value):
    """Click callback: validates the DNA sequence as it's entered, reprompting on invalid input."""
    try:
        return validate_sample_dna_format(value)
    except ValueError as e:
        raise click.BadParameter(str(e))

@click.group()
def cli():
    """Lab Software CLI"""
    pass

@cli.command()
@click.option("--id", "sample_id", required=True, prompt="Sample ID", callback=validate_id_option, help="Unique sample ID")
@click.option("--dna", "sample_dna", required=True, prompt="DNA sequence", callback=validate_dna_option, help="DNA sequence of the sample")
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
@click.option("--id", "sample_id", required=True, prompt="Sample ID", callback=validate_id_option, help="Sample ID to update")
@click.option("--dna", "sample_dna", required=True, prompt="New DNA sequence", callback=validate_dna_option, help="New DNA sequence of the sample")
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
        return
    click.echo(f"\nID:       {sample.sample_id}")
    click.echo(f"DNA:      {sample.sample_dna}")
    click.echo(f"Length:   {len(sample.sample_dna)} bases")
    if sample.reverse_complement is not None:
        click.echo(f"Reverse complement: {sample.reverse_complement}")
    if sample.rna_transcript is not None:
        click.echo(f"RNA transcript:     {sample.rna_transcript}")
    if sample.protein is not None:
        click.echo(f"Protein:            {sample.protein}")

@cli.command()
@click.option("--id", "sample_id", required=True, prompt="Sample ID", help="Sample ID to analyze")
def analyze(sample_id):
    """Interactively perform one or more DNA analyses on a sample"""
    service = get_service()
    sample = service.find_sample(sample_id)
    if sample is None:
        click.echo(click.style(f"✗ No sample found with ID '{sample_id}'.", fg="red"))
        return

    while True:
        remaining = [(key, label, func) for key, label, func in ANALYSES if getattr(sample, key) is None]

        if not remaining:
            click.echo("All analyses have already been performed for this sample.")
            return

        click.echo("\nAvailable analyses:")
        for i, (key, label, func) in enumerate(remaining, start=1):
            click.echo(f"{i}. {label}")

        choice = click.prompt("Select an analysis to perform", type=click.IntRange(1, len(remaining)))
        key, label, func = remaining[choice - 1]

        try:
            result = func(sample.sample_dna)
            setattr(sample, key, result)
            save_samples(DATA_PATH, service.get_state())
            click.echo(click.style(f"✓ {label}: {result}", fg="green"))
        except ValueError as e:
            click.echo(click.style(f"✗ Error: {e}", fg="red"))

        if not click.confirm("Do you want to perform further analysis?"):
            return

@cli.command(name="import-fasta")
def import_fasta():
    """Import samples from FASTA files placed in data/fasta_import/"""
    service = get_service()

    FASTA_IMPORT_DIR.mkdir(parents=True, exist_ok=True)
    FASTA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    fasta_files = sorted(
        p for p in FASTA_IMPORT_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in FASTA_EXTENSIONS
    )

    if not fasta_files:
        click.echo(f"No FASTA files found in '{FASTA_IMPORT_DIR}'.")
        return

    existing_ids = set(service.get_state().keys())
    total_imported = 0
    total_failed = 0

    for file_path in fasta_files:
        text = file_path.read_text(encoding="utf-8")
        records = parse_fasta(text)

        if not records:
            click.echo(click.style(f"✗ {file_path.name}: no FASTA records found.", fg="red"))
            continue

        for header, sequence in records:
            try:
                sample_id = generate_sample_id(existing_ids)
                sample = Sample(sample_id=sample_id, sample_dna=sequence)
                service.add_sample(sample)
                existing_ids.add(sample_id)
                click.echo(click.style(f"✓ Imported '{header}' as sample '{sample_id}'.", fg="green"))
                total_imported += 1
            except (ValidationError, ValueError) as e:
                click.echo(click.style(f"✗ Failed to import '{header}' from {file_path.name}: {e}", fg="red"))
                total_failed += 1

        save_samples(DATA_PATH, service.get_state())

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        destination = FASTA_PROCESSED_DIR / f"{timestamp}_{file_path.name}"
        file_path.rename(destination)

    click.echo(f"\nImport complete: {total_imported} sample(s) imported, {total_failed} failed.")

if __name__ == "__main__":  # pragma: no cover
    cli()
