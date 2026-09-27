import hashlib
import json
import os
import unittest
from pathlib import Path


class MapleLeafRagEndToEndArtifactTest(unittest.TestCase):
    """Validate a separately generated E2E artifact directory."""

    @classmethod
    def setUpClass(cls):
        value = os.environ.get("POCKET_SWEEPER_MAPLE_E2E")
        if not value:
            raise unittest.SkipTest("set POCKET_SWEEPER_MAPLE_E2E to an E2E output directory")
        cls.root = Path(value)

    def test_manifest_and_artifact_hashes(self):
        manifest = json.loads((self.root / "maple_leaf_rag.manifest.json").read_text())
        self.assertEqual(manifest["source_sha256"], "3dd712a85fabd267f5a2cee5cb23af4683408c2f29b8814721844498f1ee4f66")
        self.assertEqual(manifest["ticks_per_row"], 6)
        self.assertEqual(manifest["source_tempo"][0]["microseconds_per_quarter"], 500000)
        self.assertEqual(manifest["arrangement_configuration"]["loop_policy"], "none")
        for field, name in {
            "musicxml_sha256": "maple_leaf_rag.generated.musicxml",
            "json_sha256": "maple_leaf_rag.prototype.json",
        }.items():
            self.assertEqual(manifest[field], hashlib.sha256((self.root / name).read_bytes()).hexdigest(), field)
        for name in ("maple_leaf_rag.uge", "maple_leaf_rag.asm"):
            self.assertTrue((self.root / name).is_file())
        self.assertTrue((self.root / "maple_leaf_rag.gb").is_file())


if __name__ == "__main__":
    unittest.main()
