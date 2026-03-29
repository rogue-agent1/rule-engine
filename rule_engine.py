#!/usr/bin/env python3
"""Rule engine: condition-action rules, forward chaining, conflict resolution."""
import sys, re

class Condition:
    def __init__(self, field, op, value):
        self.field,self.op,self.value = field,op,value
    def evaluate(self, facts):
        val = facts.get(self.field)
        if val is None: return False
        if self.op == "==": return val == self.value
        if self.op == "!=": return val != self.value
        if self.op == ">": return val > self.value
        if self.op == "<": return val < self.value
        if self.op == ">=": return val >= self.value
        if self.op == "<=": return val <= self.value
        if self.op == "in": return val in self.value
        if self.op == "contains": return self.value in val
        return False

class Rule:
    def __init__(self, name, conditions, actions, priority=0, salience=0):
        self.name,self.conditions,self.actions = name,conditions,actions
        self.priority,self.salience = priority,salience
    def matches(self, facts): return all(c.evaluate(facts) for c in self.conditions)
    def fire(self, facts):
        for action in self.actions: action(facts)

class RuleEngine:
    def __init__(self): self.rules = []; self.log = []
    def add_rule(self, rule): self.rules.append(rule)
    def run(self, facts, max_iterations=100):
        fired = set()
        for _ in range(max_iterations):
            candidates = [(r.salience, r) for r in self.rules if r.name not in fired and r.matches(facts)]
            if not candidates: break
            candidates.sort(key=lambda x: -x[0])
            _, rule = candidates[0]
            rule.fire(facts); fired.add(rule.name)
            self.log.append(f"Fired: {rule.name}")
        return facts

def main():
    engine = RuleEngine()
    engine.add_rule(Rule("high_value_customer",
        [Condition("total_purchases",">",1000), Condition("years_active",">=",2)],
        [lambda f: f.update({"tier":"gold","discount":0.15})], salience=10))
    engine.add_rule(Rule("regular_customer",
        [Condition("total_purchases",">",100)],
        [lambda f: f.update({"tier":"silver","discount":0.05})], salience=5))
    engine.add_rule(Rule("new_customer",
        [Condition("years_active","<",1)],
        [lambda f: f.update({"welcome_offer":True})], salience=3))
    engine.add_rule(Rule("gold_free_shipping",
        [Condition("tier","==","gold")],
        [lambda f: f.update({"free_shipping":True})], salience=1))
    facts = {"name":"Alice","total_purchases":1500,"years_active":3}
    result = engine.run(facts)
    print(f"  Customer: {result['name']}")
    print(f"  Tier: {result.get('tier')}, Discount: {result.get('discount')}")
    print(f"  Free shipping: {result.get('free_shipping')}")
    print(f"  Rules fired: {engine.log}")

if __name__ == "__main__": main()
