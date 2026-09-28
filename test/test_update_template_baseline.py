import json
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "script" / "update-template-baseline.py"


class UpdateTemplateBaselineTest(unittest.TestCase):
    def test_updates_baseline_release_and_package_version(self) -> None:
        root, candidate, temporary = self.fixture()
        self.addCleanup(temporary.cleanup)

        result = self.run_update(root, candidate, "v1.6.0")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((root / "TEMPLATE_BASELINE").read_text(), "v1.6.0\n")
        self.assertEqual((root / "VERSION").read_text(), "0.25.9\n")
        self.assertEqual((root / "dex-sdk" / "VERSION").read_text(), "0.25.9\n")
        self.assertIn(
            "TEMPLATE_BASELINE=v1.6.0",
            (
                root / "dex-sdk" / "references" / "core" / "bundle-baselines.md"
            ).read_text(),
        )
        self.assertIn("## 0.25.9 - 2026-09-27", (root / "CHANGELOG.md").read_text())
        for manifest in self.versioned_manifests(root):
            self.assertIn('"version": "0.25.9"', manifest.read_text())

    def test_rejects_a_template_that_still_vendors_skills(self) -> None:
        root, candidate, temporary = self.fixture()
        self.addCleanup(temporary.cleanup)
        manifest_path = candidate / ".superverse" / "template.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["dexSkill"] = ".agents/skills/dex-app-builder/SKILL.md"
        manifest_path.write_text(json.dumps(manifest))

        result = self.run_update(root, candidate, "v1.6.0")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("project-local skill path", result.stderr)

    def test_keeps_a_newer_current_baseline(self) -> None:
        root, candidate, temporary = self.fixture()
        self.addCleanup(temporary.cleanup)
        (root / "TEMPLATE_BASELINE").write_text("v2.0.0\n")

        result = self.run_update(root, candidate, "v1.6.0")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((root / "TEMPLATE_BASELINE").read_text(), "v2.0.0\n")
        self.assertEqual((root / "VERSION").read_text(), "0.25.8\n")

    def fixture(self) -> tuple[Path, Path, tempfile.TemporaryDirectory]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        script = root / "script" / SCRIPT.name
        script.parent.mkdir()
        script.write_bytes(SCRIPT.read_bytes())
        (root / "VERSION").write_text("0.25.8\n")
        (root / "TEMPLATE_BASELINE").write_text("v0.2.1\n")
        (root / "dex-sdk" / "references" / "core").mkdir(parents=True)
        (root / "dex-sdk" / "VERSION").write_text("0.25.8\n")
        (root / "dex-sdk" / "references" / "core" / "bundle-baselines.md").write_text(
            "TEMPLATE_BASELINE=v0.2.1\n"
        )
        (root / "CHANGELOG.md").write_text(
            "# Changelog\n\nAll notable changes to Dex Skills are documented here.\n\n"
        )
        for manifest in self.versioned_manifests(root):
            manifest.parent.mkdir(parents=True, exist_ok=True)
            if manifest.name == "marketplace.json":
                manifest.write_text('{"plugins":[{"version":"0.25.8"}]}')
            else:
                manifest.write_text('{"version":"0.25.8"}')
        candidate = root / "candidate"
        (candidate / ".superverse").mkdir(parents=True)
        (candidate / ".superverse" / "template.json").write_text(json.dumps({
            "schemaVersion": 1,
            "templateVersion": "1.6.0",
            "minimumSandboxImageContractRevision": 3,
        }))
        return root, candidate, temporary

    def versioned_manifests(self, root: Path) -> list[Path]:
        return [
            root / ".codex-plugin" / "plugin.json",
            root / ".claude-plugin" / "plugin.json",
            root / ".cursor-plugin" / "plugin.json",
            root / ".claude-plugin" / "marketplace.json",
            root / ".cursor-plugin" / "marketplace.json",
        ]

    def run_update(
        self,
        root: Path,
        candidate: Path,
        template_tag: str,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "python3",
                str(root / "script" / SCRIPT.name),
                "--template-tag",
                template_tag,
                "--template-root",
                str(candidate),
                "--release-date",
                "2026-09-27",
            ],
            check=False,
            capture_output=True,
            text=True,
        )


if __name__ == "__main__":
    unittest.main()
