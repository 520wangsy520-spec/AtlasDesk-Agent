import unittest
from agent.config import WORKSPACE
from agent.tools import read, write, edit, bash

class ToolTests(unittest.TestCase):
    def setUp(self):
        self.p=WORKSPACE/"_tool_test.txt"; self.p.write_text("alpha\nbeta\n",encoding="utf-8")
    def tearDown(self): self.p.unlink(missing_ok=True)
    def test_read(self): self.assertIn("1 | alpha",read("_tool_test.txt",1,1))
    def test_write_edit(self):
        self.assertIn("现在 2 行",write("_tool_test.txt","one\ntwo\n"))
        self.assertIn("+three",edit("_tool_test.txt","two","three"))
    def test_edit_multiple(self):
        self.p.write_text("x\nx\n",encoding="utf-8")
        with self.assertRaises(ValueError): edit("_tool_test.txt","x","y")
    def test_escape(self):
        with self.assertRaises(ValueError): read("../AGENTS.md")
    def test_bash(self):
        out=bash(f'"{__import__("sys").executable}" -c "print(123)"',5)
        self.assertEqual(out["exit_code"],0)
