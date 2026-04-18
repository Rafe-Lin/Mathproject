/no_think

Write Python code only.

Create a simple but valid generator for the unit `Four Arithmetic Operations of Polynomial`.

The script must:

- define `generate(level=1, **kwargs)`
- define `check(user_answer, correct_answer)`
- return a dictionary with `question_text`, `answer`, `correct_answer`, `mode`
- use LaTeX-wrapped math in `question_text`
- keep `correct_answer` non-empty

At minimum, support one polynomial family such as:

- flat add/sub
- monomial multiplication
- polynomial multiplication
- unknown polynomial by add/sub

Use textbook Chinese wording.

Examples of acceptable `question_text` style:

- `計算 $(3x^{2}-2x+1)+(-x^{2}+5x-3)$。`
- `計算 $3x(x+2)$。`
- `若 $A+(-4x^{2}+1+5x)=x^{3}+5-2x$，則多項式 $A=$？`

Answer format examples:

- `2x^2+3x-2`
- `x^3-7x+4`

Do not output markdown fences or explanations.
