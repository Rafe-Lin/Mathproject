import sys
import os
import re
import unittest

# Add core directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.code_generator import fix_code_syntax, PERFECT_UTILS

class TestCodeGenV2_5(unittest.TestCase):
    def test_regex_fix_latex_braces(self):
        """Test the key regex fix for f-strings."""
        
        # Case 1: Python Variable - Should preserve single braces
        code = 'f"Answer: {a}"'
        fixed, _ = fix_code_syntax(code)
        self.assertEqual(fixed, 'f"Answer: {a}"')

        # Case 2: LaTeX Command - Should double braces
        code = 'f"Fraction: \\\\frac{1}{2}"'
        # Note: input string has double backslash because it represents the source code string
        # fix_code_syntax expects the content of the file.
        # In Python source code: f"Fraction: \frac{1}{2}" is represented as 'f"Fraction: \\frac{1}{2}"'
        # Let's emulate reading from file where backslash is a character.
        
        # fix_code_syntax handles the string content of the file.
        # If the file contains: f"Fraction: \frac{1}{2}"
        # Then the input string to fix_code_syntax is 'f"Fraction: \\frac{1}{2}"'
        
        code = r'f"Fraction: \frac{1}{2}"' 
        fixed, _ = fix_code_syntax(code)
        
        print(f"\n[DEBUG] Code: {repr(code)}")
        print(f"[DEBUG] Fixed: {repr(fixed)}")
        print(f"[DEBUG] Expect: {repr(r'f\"Fraction: \frac{{1}}{{2}}\"')}")
        
        self.assertEqual(fixed, r'f"Fraction: \frac{{1}}{{2}}"')

        # Case 3: Mixed - Python Var + LaTeX
        code = r'f"Val: {a}, Latex: \frac{1}{2}"'
        fixed, _ = fix_code_syntax(code)
        
        print(f"[DEBUG] Case 3 Fixed: {repr(fixed)}")
        
        # User Logic: If python var detected, preserve EVERYTHING. 
        # So \frac{1}{2} stays single brace (AI must handle this manually or avoid mixing)
        self.assertEqual(fixed, r'f"Val: {a}, Latex: \frac{{1}}{{2}}"')
        
        # Case 4: No LaTeX command - Should preserve braces (e.g. JSON-like or just Text)
        code = r'f"Data: {a, b}"' # Logic says: if has_latex_cmd AND has_single_brace. No latex cmd here.
        fixed, _ = fix_code_syntax(code)
        self.assertEqual(fixed, r'f"Data: {a, b}"')

        # Case 5: Newline check (User requirement: don't hurt \n)
        code = r'f"Line1\nLine2: {x}"' 
        # \n is a backslash char, but our regex is r'\\[a-zA-Z]+'. 'n' matches.
        # But wait, \n in python source is often a literal newline character if read from file?
        # If the file has literal \n (backslash n), it matches.
        # But if it's just a python var {x}, it should be preserved by the special check:
        # if re.search(r'\{[a-zA-Z_][a-zA-Z0-9_]*\}', content): return f"{content}"
        
        fixed, _ = fix_code_syntax(code)
        self.assertEqual(fixed, r'f"Line1\nLine2: {x}"')

    def test_perfect_utils_expansion(self):
        """Test if PERFECT_UTILS has the new classes execution valid."""
        # Create a dummy environment to execute the utils
        env = {}
        try:
            exec(PERFECT_UTILS, env)
        except Exception as e:
            self.fail(f"PERFECT_UTILS execution failed: {e}")
            
        self.assertIn('Vector3', env)
        self.assertIn('Matrix', env)
        
        # Test Vector3
        Vec3 = env['Vector3']
        v1 = Vec3(1, 2, 3)
        v2 = Vec3(4, 5, 6)
        v3 = v1 + v2
        self.assertEqual(v3.x, 5)
        self.assertEqual(v3.y, 7)
        self.assertEqual(v3.z, 9)
        
        # Test Matrix
        Mat = env['Matrix']
        m = Mat([[1, 2], [3, 4]])
        det = m.det()
        # 1*4 - 2*3 = 4 - 6 = -2
        self.assertEqual(det, -2)

if __name__ == '__main__':
    unittest.main()
