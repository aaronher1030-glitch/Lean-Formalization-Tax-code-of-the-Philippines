import unittest

import mutation_tests as m


class MutationDefinitions(unittest.TestCase):
    def test_four_guards(self):
        self.assertEqual(len(m.MUTATIONS), 4)
        self.assertEqual(
            [x["name"] for x in m.MUTATIONS],
            ["statute_guard", "tier_guard", "eight_rate", "election_eligibility"],
        )

    def test_each_pattern_occurs_exactly_once(self):
        for mut in m.MUTATIONS:
            text = (m.LEAN_DIR / mut["file"]).read_text(encoding="utf8")
            self.assertEqual(text.count(mut["old"]), 1, mut["name"])

    def test_each_mutation_changes_text(self):
        for mut in m.MUTATIONS:
            self.assertNotEqual(mut["old"], mut["new"], mut["name"])

    def test_break_file_is_built_before_dependents(self):
        order = [name for name, _ in m.BUILD]
        for mut in m.MUTATIONS:
            self.assertIn(mut["file"], order)
            self.assertEqual(mut["break_at"], mut["file"])


if __name__ == "__main__":
    unittest.main()
