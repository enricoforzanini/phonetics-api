from app.data_loader import load_translations

def test_load_translations():
    translations = load_translations()
    assert "fr" in translations.keys()
    assert translations["fr"]["abdominales"] == "/ab.dɔ.mi.nal/"