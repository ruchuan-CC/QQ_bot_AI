from src.services.asset_service import AssetService


def test_asset_service_counts_supported_files_by_category(tmp_path):
    (tmp_path / "comfort").mkdir()
    (tmp_path / "comfort" / "a.png").write_bytes(b"png")
    (tmp_path / "comfort" / "note.txt").write_text("ignore", encoding="utf-8")
    (tmp_path / "meme").mkdir()
    (tmp_path / "meme" / "b.gif").write_bytes(b"gif")

    service = AssetService(tmp_path)

    assert service.count_by_category() == {"comfort": 1, "meme": 1}
    assert service.choose("comfort").name == "a.png"
