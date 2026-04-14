import re
from sympy import sympify, diff, integrate, solve, limit, simplify, trigsimp, Eq
from sympy import factorial

# =========================
# FORMULA DATABASE
# =========================
FORMULAS = {
    "trigonometry": [
        "sin^2(x) + cos^2(x) = 1",
        "1 + tan^2(x) = sec^2(x)",
        "tan(x) = sin(x)/cos(x)"
    ],
    "derivative": [
        "d/dx (x^n) = n*x^(n-1)",
        "d/dx (sin x) = cos x"
    ],
    "integration": [
        "∫ x^n dx = x^(n+1)/(n+1) + C"
    ]
}

# =========================
# HELPERS
# =========================
def _format(expr):
    expr = simplify(expr)
    expr = trigsimp(expr)

    try:
        if expr.is_number:
            return str(round(float(expr), 2))
    except:
        pass

    return str(expr).replace("**", "^")

def _get_variable(expr):
    symbols = list(expr.free_symbols)
    return symbols[0] if symbols else None

def _extract_equation(expr_text):
    if "=" in expr_text:
        left, right = expr_text.split("=")
        return Eq(sympify(left), sympify(right))
    return sympify(expr_text)

def _parse_numbers(text):
    return list(map(float, re.findall(r"-?\d+\.?\d*", text)))

# =========================
# MAIN SOLVER
# =========================
def solve_math_query(query):
    original_query = query
    query = query.lower().strip()
    query = query.replace("^", "**")

    try:

        # =========================
        # FORMULAS
        # =========================
        if "formula" in query:
            for key in FORMULAS:
                if key in query:
                    return "Formulas:\n" + "\n".join(FORMULAS[key])

        # =========================
        # MEAN
        # =========================
        if "mean" in query or "average" in query:
            nums = _parse_numbers(original_query)
            if nums:
                s = sum(nums)
                n = len(nums)
                return f"""
Numbers: {nums}

Step 1: Sum = {s}
Step 2: Count = {n}

Final Answer:
Mean = {round(s/n,2)}
"""

        # =========================
        # VARIANCE
        # =========================
        if "variance" in query:
            nums = _parse_numbers(original_query)
            if nums:
                mean = sum(nums)/len(nums)
                var = sum((x-mean)**2 for x in nums)/len(nums)
                return f"""
Numbers: {nums}

Step 1: Mean = {round(mean,2)}
Step 2: Apply formula Σ(x-mean)^2 / n

Final Answer:
Variance = {round(var,2)}
"""

        # =========================
        # STANDARD DEVIATION
        # =========================
        if "standard deviation" in query or "std" in query:
            nums = _parse_numbers(original_query)
            if nums:
                mean = sum(nums)/len(nums)
                var = sum((x-mean)**2 for x in nums)/len(nums)
                std = var**0.5
                return f"""
Numbers: {nums}

Step 1: Mean = {round(mean,2)}
Step 2: Variance = {round(var,2)}
Step 3: Square root of variance

Final Answer:
Standard Deviation = {round(std,2)}
"""

        # =========================
        # PROBABILITY
        # =========================
        if "probability" in query:
            nums = _parse_numbers(original_query)
            if len(nums) >= 2:
                fav, total = nums[0], nums[1]
                return f"""
Step 1: Favorable outcomes = {fav}
Step 2: Total outcomes = {total}

Final Answer:
Probability = {round(fav/total,2)}
"""

        # =========================
        # COIN TOSS
        # =========================
        if "head" in query and "toss" in query:
            nums = list(map(int, re.findall(r"\d+", query)))
            if len(nums) >= 2:
                k, n = nums[0], nums[1]
                prob = (factorial(n) / (factorial(k) * factorial(n-k))) * (0.5**n)
                return f"""
Step 1: Use formula nCk * (1/2)^n
Step 2: n = {n}, k = {k}

Final Answer:
P = {_format(prob)}
"""

        # =========================
        # DERIVATIVE
        # =========================
        if "differentiate" in query or "derivative" in query:
            expr_text = re.sub(r"(differentiate|derivative|of)", "", query)
            expr = sympify(expr_text)
            var = _get_variable(expr)
            if var:
                result = diff(expr, var)
                return f"""
Step 1: Given function = {expr}
Step 2: Apply derivative rules

Final Answer:
d/d{var} = {_format(result)}
"""

        # =========================
        # INTEGRATION
        # =========================
        if "integrate" in query:
            expr_text = re.sub(r"(integrate|of)", "", query)
            expr = sympify(expr_text)
            var = _get_variable(expr)
            if var:
                result = integrate(expr, var)
                return f"""
Step 1: Given function = {expr}
Step 2: Apply integration rules

Final Answer:
∫ = {_format(result)} + C
"""

        # =========================
        # LIMIT
        # =========================
        if "limit" in query:
            match = re.search(r"limit(.+)as(.+)->(.+)", query)
            if match:
                expr = sympify(match.group(1))
                var = sympify(match.group(2))
                point = sympify(match.group(3))
                result = limit(expr, var, point)
                return f"""
Step 1: Substitute value {point} into function

Final Answer:
Limit = {_format(result)}
"""

        # =========================
        # SOLVE
        # =========================
        if "solve" in query:
            expr_text = re.sub(r"(solve|for)", "", query)
            expr = _extract_equation(expr_text)
            var = _get_variable(expr)
            if var:
                result = solve(expr, var)
                return f"""
Step 1: Given equation = {expr}
Step 2: Solve for {var}

Final Answer:
{var} = {_format(result)}
"""

        # =========================
        # BASIC CALC
        # =========================
        if re.search(r"[0-9+\-*/().]", query):
            expr = sympify(query)
            result = expr.evalf()
            return f"""
Step 1: Evaluate expression

Final Answer:
Result = {round(float(result),2)}
"""

    except Exception:
        return None

    return None