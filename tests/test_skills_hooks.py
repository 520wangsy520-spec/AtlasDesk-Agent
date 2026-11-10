import unittest
from agent.skills import catalog, match_skill
from agent.hooks import before_tool

class Tests(unittest.TestCase):
    def test_three_skills(self): self.assertGreaterEqual(len(catalog()),3)
    def test_triggers(self):
        cases={"帮我跑一下测试":"run-tests","为什么挂了":"run-tests","把这段 diff 审一遍":"review-diff","看看改了什么":"review-diff","帮我查 issue 101":"fetch-issue","今天天气怎么样":None}
        for q,e in cases.items(): self.assertEqual(match_skill(q),e)
    def test_env_block(self):
        ok,msg=before_tool("write",{"path":".env","content":"x"}); self.assertFalse(ok); self.assertTrue(msg)
    def test_rm_block(self):
        ok,msg=before_tool("bash",{"command":"rm -rf build/"}); self.assertFalse(ok); self.assertIn("替代方案",msg)
