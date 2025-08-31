from verify_netlogo import NetLogoVerifier, CodeComplexity
import re
# Import test data from the separate file
from verifier_test_data import basic_test_cases, advanced_test_cases, prompt_examples

def run_test_cases(test_cases):
    verifier = NetLogoVerifier()
    failures = 0
    
    for i, (test_code, expected) in enumerate(test_cases):
        is_safe, message = verifier.is_safe(test_code)
        complexity = verifier.measure_complexity(test_code)
        
        print(f'Test #{i+1}: {test_code}')
        print(f'Expected: {expected}, Result: {is_safe}, Complexity: {complexity.name}')
        
        if is_safe != expected:
            print(f'ERROR: {message}')
            failures += 1
        else:
            print(f'SUCCESS: {"Safe" if is_safe else "Unsafe"} as expected')
        print('')
    
    print(f'SUMMARY: {len(test_cases) - failures}/{len(test_cases)} tests passed')
    return failures == 0

# Test cases are now imported from src.verification.verifier_test_data

print("\n=== RUNNING BASIC TEST CASES ===\n")
basic_passed = run_test_cases(basic_test_cases)

print("\n=== RUNNING ADVANCED TEST CASES ===\n")
advanced_passed = run_test_cases(advanced_test_cases)

# Output overall result
if basic_passed and advanced_passed:
    print("\nALL TESTS PASSED: The verifier appears capable of handling the complexity in the new prompt.")
else:
    print("\nSOME TESTS FAILED: The verifier may need adjustments to handle all patterns in the new prompt.")

# Check verifier on specific examples from the prompt
print("\n=== VALIDATING EXAMPLES FROM THE PROMPT ===\n")
# prompt_examples is now imported

verifier = NetLogoVerifier()
for example in prompt_examples:
    is_safe, message = verifier.is_safe(example)
    complexity = verifier.measure_complexity(example)
    print(f'Example: {example}')
    print(f'Valid: {is_safe}, Complexity: {complexity.name}')
    if not is_safe:
        print(f'Error: {message}')
    print('')
