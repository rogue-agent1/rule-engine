import argparse, json, re, operator

OPS = {
    "==": operator.eq, "!=": operator.ne,
    ">": operator.gt, ">=": operator.ge,
    "<": operator.lt, "<=": operator.le,
    "in": lambda a, b: a in b,
    "contains": lambda a, b: b in a,
    "startswith": lambda a, b: str(a).startswith(str(b)),
    "matches": lambda a, b: bool(re.search(b, str(a))),
}

class Rule:
    def __init__(self, name, conditions, action, priority=0):
        self.name = name; self.conditions = conditions
        self.action = action; self.priority = priority
    def evaluate(self, facts):
        for cond in self.conditions:
            field, op, value = cond["field"], cond["op"], cond["value"]
            actual = facts.get(field)
            if actual is None: return False
            if not OPS.get(op, lambda a, b: False)(actual, value):
                return False
        return True

class RuleEngine:
    def __init__(self):
        self.rules = []
    def add_rule(self, rule):
        self.rules.append(rule)
        self.rules.sort(key=lambda r: -r.priority)
    def evaluate(self, facts, mode="all"):
        fired = []
        for rule in self.rules:
            if rule.evaluate(facts):
                fired.append(rule)
                if mode == "first": break
        return fired

def main():
    p = argparse.ArgumentParser(description="Rule engine")
    p.add_argument("--demo", action="store_true")
    p.add_argument("--file", help="JSON rules file")
    args = p.parse_args()
    if args.demo:
        engine = RuleEngine()
        engine.add_rule(Rule("VIP Discount", [
            {"field": "total", "op": ">=", "value": 100},
            {"field": "membership", "op": "==", "value": "gold"}
        ], "Apply 20% discount", priority=2))
        engine.add_rule(Rule("Free Shipping", [
            {"field": "total", "op": ">=", "value": 50}
        ], "Free shipping", priority=1))
        engine.add_rule(Rule("New Customer", [
            {"field": "orders", "op": "==", "value": 0}
        ], "Welcome 10% coupon", priority=3))
        engine.add_rule(Rule("Fraud Check", [
            {"field": "total", "op": ">", "value": 500},
            {"field": "country", "op": "!=", "value": "US"}
        ], "Flag for review", priority=10))
        tests = [
            {"total": 150, "membership": "gold", "orders": 5, "country": "US"},
            {"total": 75, "membership": "silver", "orders": 0, "country": "US"},
            {"total": 600, "membership": "basic", "orders": 2, "country": "UK"},
        ]
        for facts in tests:
            fired = engine.evaluate(facts)
            print(f"Facts: {facts}")
            for rule in fired:
                print(f"  ✅ {rule.name}: {rule.action}")
            if not fired: print("  (no rules fired)")
            print()
    else: p.print_help()

if __name__ == "__main__":
    main()
