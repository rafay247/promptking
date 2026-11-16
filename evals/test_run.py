import unittest
import run


class CommandTests(unittest.TestCase):
    def test_baseline_cmd_is_isolated_and_has_no_plugin(self):
        cmd = run.build_baseline_cmd("hello")
        self.assertEqual(cmd[:4], ["claude", "-p", "--setting-sources", "project"])
        self.assertNotIn("--plugin-dir", cmd)
        self.assertEqual(cmd[-1], "hello")

    def test_skill_cmd_loads_plugin_and_prefixes_command(self):
        cmd = run.build_skill_cmd("hello", "/repo", model="opus")
        self.assertIn("--plugin-dir", cmd)
        self.assertEqual(cmd[cmd.index("--plugin-dir") + 1], "/repo")
        self.assertEqual(cmd[cmd.index("--model") + 1], "opus")
        self.assertEqual(cmd[-1], "/promptking hello")

    def test_all_cmds_block_file_writing_tools(self):
        # Headless runs can't approve permission prompts; answers must come back inline.
        # Must be a single `--flag=value` token: the option is variadic and a
        # separate value token would make it swallow the prompt as a tool name.
        for cmd in (run.build_baseline_cmd("x"), run.build_skill_cmd("x", "/r"), run.build_judge_cmd("x")):
            self.assertIn("--disallowedTools=Write,Edit,NotebookEdit", cmd)
            self.assertNotIn("--disallowedTools", cmd)

    def test_judge_cmd_disables_skills(self):
        self.assertIn("--disable-slash-commands", run.build_judge_cmd("x"))


class JudgeTests(unittest.TestCase):
    def test_render_fills_all_slots(self):
        out = run.render_judge_prompt("{{REQUEST}}|{{RESPONSE_A}}|{{RESPONSE_B}}", "r", "a", "b")
        self.assertEqual(out, "r|a|b")

    def test_parse_verdict_extracts_json_from_noise(self):
        text = 'Sure:\n{"reason": "x", "winner": "B", "a_asks_before_answering": false, "b_asks_before_answering": true}\n'
        v = run.parse_verdict(text)
        self.assertEqual(v["winner"], "B")
        self.assertTrue(v["b_asks_before_answering"])

    def test_parse_verdict_rejects_bad_winner(self):
        with self.assertRaises(ValueError):
            run.parse_verdict('{"reason": "x", "winner": "C", "a_asks_before_answering": false, "b_asks_before_answering": false}')

    def test_parse_verdict_rejects_missing_json(self):
        with self.assertRaises(ValueError):
            run.parse_verdict("no json here")

    def test_map_verdict_when_skill_is_b(self):
        v = {"winner": "B", "a_asks_before_answering": False, "b_asks_before_answering": True}
        self.assertEqual(run.map_verdict(v, skill_is_a=False), ("skill", True))
        self.assertEqual(run.map_verdict(v, skill_is_a=True), ("baseline", False))

    def test_map_verdict_tie(self):
        v = {"winner": "tie", "a_asks_before_answering": False, "b_asks_before_answering": False}
        self.assertEqual(run.map_verdict(v, skill_is_a=True)[0], "tie")


class BehaviorTests(unittest.TestCase):
    def test_flags_asking_when_it_should_proceed(self):
        fails = run.behavior_failures({"expect": {"asks": False}}, "Which language?", True)
        self.assertEqual(fails, ["asked when it should have proceeded"])

    def test_flags_not_asking_when_it_should(self):
        fails = run.behavior_failures({"expect": {"asks": True}}, "Here is a proposal...", False)
        self.assertEqual(fails, ["should have asked first"])

    def test_flags_overlong_trivial_answer(self):
        fails = run.behavior_failures({"expect": {"max_chars": 10}}, "x" * 11, False)
        self.assertEqual(len(fails), 1)
        self.assertIn("too long", fails[0])

    def test_flags_leaked_brief(self):
        fails = run.behavior_failures({"expect": {}}, "Real goal: ship it", False)
        self.assertEqual(len(fails), 1)
        self.assertIn("leaked", fails[0])

    def test_clean_output_passes(self):
        self.assertEqual(run.behavior_failures({"expect": {"asks": False}}, "36", False), [])


class SummaryTests(unittest.TestCase):
    def test_win_rate_excludes_ties(self):
        rows = [
            {"winner": "skill", "behavior_failures": []},
            {"winner": "skill", "behavior_failures": ["x"]},
            {"winner": "baseline", "behavior_failures": []},
            {"winner": "tie", "behavior_failures": []},
        ]
        s = run.summarize(rows)
        self.assertEqual((s["cases"], s["skill"], s["baseline"], s["tie"]), (4, 2, 1, 1))
        self.assertAlmostEqual(s["win_rate"], 0.667, places=3)
        self.assertEqual(s["behavior_pass"], 3)

    def test_summary_md_has_table(self):
        rows = [{"id": "c1", "winner": "skill", "reason": "better", "behavior_failures": []}]
        md = run.render_summary_md(run.summarize(rows), rows)
        self.assertIn("| c1 | skill |", md)


if __name__ == "__main__":
    unittest.main()
