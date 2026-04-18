/no_think

Return Python code only.

Generate one valid benchmark-ready script for `jh_數學2上_FourArithmeticOperationsOfPolynomial`.

Requirements:

1. Define `generate(level=1, **kwargs)` and `check(user_answer, correct_answer)`.
2. Use randomized same-family polynomial logic, not a fixed one-off question, unless impossible.
3. Keep `question_text` textbook-style and LaTeX-wrapped.
4. Keep `correct_answer` non-empty and deterministic.
5. Prefer `PolynomialOps` for formatting and basic operations.
6. If needed, add a small local helper for long division, quotient/remainder, reverse division, or geometry formulas.

Supported families:

- add/sub
- unknown polynomial
- multiplication
- special identities
- quotient/remainder
- reverse division
- mixed simplification
- formula geometry

Formatting:

- wrap visible math in `$...$`
- use `x^{2}`
- use `\\frac{a}{b}` for fractions
- use `\\times` and `\\div` when shown

Answer format:

- plain polynomial: `3x^2-2x+1`
- quotient/remainder: `商式：...；餘式：...`
- two targets: `周長：...；面積：...`

Do not emit markdown fences, prose, or comments outside the Python code.
