from app.data_loader import load_translations

def test_load_translations():
    translations = load_translations()
    assert "french" in translations.keys()
    assert translations["french"]["abdominales"] == "/ab.dɔ.mi.nal/"