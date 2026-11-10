with open('c:/LLM/deepstash_microlearning/scripts/run_test_suite.py', 'r', encoding='utf-8') as f:
    code = f.read()

bad = """def test_social_learning_and_notifications()
        test_substack_ecosystem():"""
good = """def test_social_learning_and_notifications():"""

code = code.replace(bad, good)
with open('c:/LLM/deepstash_microlearning/scripts/run_test_suite.py', 'w', encoding='utf-8') as f:
    f.write(code)
print("Syntax fixed cleanly!")
