import sqlite3
from app.data_loader import download_data

DATABASE = 'data.db'

def test_load_translations():
    download_data()
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT DISTINCT language FROM translations")
    languages = c.fetchall()
    assert any(lang[0] == 'fr' for lang in languages)
    c.execute("SELECT ipa_translation FROM translations WHERE word = 'abdominales' AND language = 'fr'")
    translation = c.fetchone()[0]
    assert translation == "ab.dɔ.mi.nal"
    
