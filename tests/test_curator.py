import csv
from contextlib import redirect_stderr, redirect_stdout
from datetime import date
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import fetch_and_rank as curator


def paper(title="Example benchmark", **attrs):
    fields = dict(title=title, abstract="An example abstract.", source="arXiv",
                  date="2026-11-24", tier="Tier-2 Preprint", url="")
    return curator.Paper(**{**fields, **attrs})


def score(idx=0, **attrs):
    fields = dict(id=idx, method_score=90, alignment_score=80, clinical_score=70,
                  pillar=curator.PILLARS[0], takeaway="测试看点。")
    return {**fields, **attrs}


class CuratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        curator.load_dependencies()

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.history_path = self.root / "data" / "history.json"

    def test_empty_and_legacy_history(self):
        self.assertEqual(curator.load_history(self.history_path), {})
        self.history_path.parent.mkdir()
        self.history_path.write_text(" \n")
        self.assertEqual(curator.load_history(self.history_path), {})
        legacy = {"examplebenchmark": {"tier": "Tier-2 Preprint"}}
        self.history_path.write_text(json.dumps(legacy))
        self.assertEqual(curator.new_works([paper()], curator.load_history(self.history_path)), [])
        self.history_path.write_text("{invalid")
        with self.assertRaises(curator.CuratorError):
            curator.load_history(self.history_path)

    def test_aliases_merge_versions_and_promote_published_work(self):
        doi = "10.1234/journal"
        preprint = paper(arxiv_id="2401.01234v1", published_doi=doi)
        changed = paper("Changed title", arxiv_id="2401.01234v2")
        published = paper("Journal title", doi=doi.upper(), tier=curator.JOURNAL)
        history = {"arxiv:2401.01234": {"tier": preprint.tier}}
        works = curator.new_works([preprint, changed, published], history)
        self.assertEqual(len(works), 1)
        selected, keys = works[0]
        self.assertIs(selected, published)
        self.assertEqual(selected.status_tag, "预印本转正")
        self.assertIn("changedtitle", keys)
        self.assertIn(f"doi:{doi}", keys)

    def test_scores_are_complete_and_bounded(self):
        self.assertEqual(curator.validate_scores({"results": [score()]}, 1)[0]["score"], 81.5)
        for results, size in (([], 1), ([score(method_score=200)], 1), ([score(), score()], 2)):
            with self.subTest(results=results), self.assertRaises(ValueError):
                curator.validate_scores({"results": results}, size)

    def test_export_failure_leaves_existing_history_and_output_intact(self):
        self.history_path.parent.mkdir()
        self.history_path.write_text("{}")
        output = self.root / "digests"
        output.mkdir()
        old_md = output / "reading_list_2026-11-24.md"
        old_md.write_text("Existing digest")
        original = Path.replace

        def fail_csv(source, target):
            if target.suffix == ".csv":
                raise OSError("Simulated CSV write failure")
            return original(source, target)

        with patch.object(Path, "replace", fail_csv), self.assertRaises(OSError):
            curator.export_results(output, date(2026, 11, 24), "new", "new", self.history_path, {"new": {}})
        self.assertEqual(self.history_path.read_text(), "{}")
        self.assertEqual(list(output.iterdir()), [old_md])
        self.assertEqual(old_md.read_text(), "Existing digest")

    def test_both_outputs_respect_large_top_k(self):
        records = [(paper(str(i)), {str(i)}, curator.validate_scores({"results": [score()]}, 1)[0])
                   for i in range(105)]
        when = date(2026, 11, 24)
        rendered, table = curator.render_results(records, records, when, when, [], [])
        self.assertEqual(rendered.count("\n### "), 105)
        self.assertEqual(len(list(csv.DictReader(io.StringIO(table)))), 105)

    def test_feedback_retains_legacy_entries_and_updates_reason(self):
        path = self.root / "feedback.yaml"
        path.write_text("positive_examples: ['Existing title']\nnegative_filters: ['Old theme']\n")
        curator.record_feedback(path, "positive", "Existing title", "Clear ablations")
        curator.record_feedback(path, "positive", "Existing title", "Clear ablations")
        actual = curator.load_feedback(path)
        self.assertEqual(actual["positive_examples"], [
            {"title": "Existing title", "reason": "Clear ablations"},
        ])
        self.assertEqual(actual["negative_filters"], ["Old theme"])

    def test_partial_cli_run_can_be_retried_with_the_same_history(self):
        document = paper(doi="10.1234/example")
        dest = self.root / "digests"
        args = [
            "--history", str(self.history_path), "--output-dir", str(dest),
            "--end-date", "2026-11-24",
        ]
        result = SimpleNamespace(ok=True, json=lambda: {
            "choices": [{"message": {"content": json.dumps({"results": [score()]})}}],
        })

        def partial(journals, start, end, key, warnings):
            warnings.append("Simulated OpenAlex outage.")
            return [], 0

        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-fixture-key"}), \
                patch.object(curator, "fetch_openalex", side_effect=partial) as openalex, \
                patch.object(curator, "fetch_biorxiv", return_value=([document], 1)), \
                patch.object(curator, "fetch_arxiv", return_value=([], 1)), \
                patch.object(curator.http, "post", return_value=result) as post, \
                redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(curator.main(args), 1)
            self.assertFalse(self.history_path.exists())
            self.assertEqual(len(list(dest.glob("*.md"))), 1)
            openalex.side_effect = None
            openalex.return_value = ([], 13)
            self.assertEqual(curator.main(args), 0)
            self.assertIn("doi:10.1234/example", curator.load_history(self.history_path))
            self.assertEqual(len(list(dest.glob("*.md"))), 2)
            self.assertEqual(len(list(dest.glob("*.csv"))), 2)
            self.assertEqual(curator.main(args), 0)
            self.assertEqual(post.call_count, 2)


if __name__ == "__main__":
    unittest.main()
