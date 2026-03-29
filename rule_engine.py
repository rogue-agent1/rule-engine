#!/usr/bin/env python3
"""Rule Engine - Evaluate business rules with conditions and actions."""
import sys, re, operator

OPS = {"==": operator.eq, "!=": operator.ne, ">": operator.gt, "<": operator.lt,
       ">=": operator.ge, "<=": operator.le, "in": lambda a,b: a in b, "contains": lambda a,b: b in str(a)}

class Rule:
    def __init__(self, name, conditions, actions, priority=0):
        self.name = name; self.conditions = conditions; self.actions = actions; self.priority = priority
    def evaluate(self, facts):
        for cond in self.conditions:
            field, op, value = cond["field"], cond["op"], cond["value"]
            fact_val = facts.get(field)
            if fact_val is None: return False
            if not OPS.get(op, lambda a,b: False)(fact_val, value): return False
        return True
    def fire(self, facts):
        results = []
        for action in self.actions:
            if action["type"] == "set": facts[action["field"]] = action["value"]; results.append(f"Set {action['field']}={action['value']}")
            elif action["type"] == "log": results.append(f"Log: {action['message']}")
            elif action["type"] == "alert": results.append(f"ALERT: {action['message']}")
        return results

class Engine:
    def __init__(self): self.rules = []
    def add(self, rule): self.rules.append(rule); self.rules.sort(key=lambda r: -r.priority)
    def run(self, facts, mode="all"):
        fired = []
        for rule in self.rules:
            if rule.evaluate(facts):
                results = rule.fire(facts)
                fired.append((rule.name, results))
                if mode == "first": break
        return fired

def main():
    engine = Engine()
    engine.add(Rule("VIP Discount", [{"field": "total", "op": ">=", "value": 100}, {"field": "tier", "op": "==", "value": "vip"}],
        [{"type": "set", "field": "discount", "value": 0.2}, {"type": "log", "message": "20% VIP discount applied"}], priority=10))
    engine.add(Rule("Bulk Discount", [{"field": "quantity", "op": ">=", "value": 10}],
        [{"type": "set", "field": "discount", "value": 0.1}, {"type": "log", "message": "10% bulk discount"}], priority=5))
    engine.add(Rule("Fraud Alert", [{"field": "total", "op": ">", "value": 5000}],
        [{"type": "alert", "message": "High-value order needs review"}], priority=20))
    print("=== Rule Engine ===\n")
    orders = [
        {"customer": "Alice", "total": 150, "quantity": 3, "tier": "vip"},
        {"customer": "Bob", "total": 50, "quantity": 15, "tier": "basic"},
        {"customer": "Charlie", "total": 7500, "quantity": 1, "tier": "basic"},
    ]
    for order in orders:
        print(f"Order from {order['customer']} (${order['total']}, qty={order['quantity']}):")
        fired = engine.run(dict(order))
        for name, results in fired:
            print(f"  Rule '{name}':"); 
            for r in results: print(f"    {r}")
        if not fired: print("  No rules fired")
        print()

if __name__ == "__main__":
    main()
