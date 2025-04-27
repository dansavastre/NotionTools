import requests
import json

# AnkiConnect URL
ANKI_CONNECT_URL = "http://localhost:8765"

def invoke(action, params):
    """Send an HTTP request to AnkiConnect."""
    request_data = {
        "action": action,
        "version": 6,  # Change based on your AnkiConnect version
        "params": params
    }
    response = requests.post(ANKI_CONNECT_URL, json=request_data)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()

def add_note(deck_name, front_html, back_html):
    """Add a new note to Anki with HTML for front and back."""
    note = {
        "deckName": deck_name,
        "modelName": "Basic",
        "fields": {
            "Front": front_html,
            "Back": back_html
        },
        "tags": [],
        "options": {
            "allowDuplicate": False
        }
    }
    result = invoke("addNote", {"note": note})
    return result

def create_deck(deck_name):
    """Create a new deck in Anki."""
    result = invoke("createDeck", {"deck": deck_name})
    return result

def get_deck_names():
    """Get a list of all deck names in Anki."""
    result = invoke("deckNames", {})
    return result["result"] if isinstance(result, dict) else []

def get_note_count(deck_name):
    """Get the number of notes in a specific deck."""
    result = invoke("findNotes", {"query": f"deck:{deck_name}"})
    return len(result) if isinstance(result, list) else 0

def get_notes(deck_name):
    """Get all notes in a specific deck."""
    note_ids = invoke("findNotes", {"query": f"deck:{deck_name}"})
    notes = []
    for note_id in note_ids:
        note = invoke("getNoteInfo", {"note": note_id})
        notes.append(note)
    return notes
