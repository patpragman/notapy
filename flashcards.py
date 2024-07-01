"""
future code to build anki decks from the notes
"""

from anki.collection import Collection

# Path to your Anki collection
collection_path = "/home/patrickpragman/.local/share/Anki2/pat@pragman.io/collection.anki2"

# Open an Anki collection
col = Collection(collection_path)

# Iterating over all cards
for cid in col.find_cards(''):
    card = col.get_card(cid)
    note = card.note()
    print(f"Card ID: {card.id}, Note ID: {note.id}")
    print(f"  Front: {note.fields[0]}, Back: {note.fields[1]}")

