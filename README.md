# Lab Software
A lightweight command-line application for managing biological lab samples. Supports registering, listing, searching, and deleting samples with persistent JSON storage.

# Features
Register new samples with ID and DNA sequence validation
List all registered samples with a formatted overview
Search for a specific sample by ID
Delete samples by ID
Persistent storage via JSON file
Duplicate ID prevention

# Usage
add sample:
python main.py add --id "123456789" --dna "ACGTNNRRY"

add sample (interactive)
python main.py add

list samples:
python main.py list

search sample:
python main.py search --id "123456789"

delete sample:
python main.py delete --id "123456789"

# Validation Rules
Sample ID
- must be 9 characters long
- only numbers 1-9
- must be distinct

DNA sequence
- must not be empty
- allowed characters (IUPAC notation): A C G T N R Y K M S W B D H V -

# Roadmap
 Unit tests (pytest)
 Sample update
 Pydantic based validation
 Export (CSV, Excel)
 Adding DNA analysis tools:
 - transcription
 - translation
 - search for DNA fragments

 # Dependencies
  click >= 8.3.1
  
  pandas >= 3.0.1
  
  pydantic >= 2.12.5
 
