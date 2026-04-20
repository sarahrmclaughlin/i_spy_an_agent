
# Quick notebook to test out Prompt Evaluation
# - Create a prompt
# - Create a test dataset
# - Create eval scripts to grade answers
# - Iterate on prompt
# - Repeat process

import json
import logging
import os
import sys
from typing import Dict, List
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

load_dotenv()

sys.path.insert(0, str(Path(".").resolve()))

from src.eval_funcs import (load_prompt, load_eval_set, calculate_translation_similarity,
                             calculate_score, parse_output)


def run_evaluation(prompt_config: Dict, eval_set: Dict) -> List[Dict]:

    client = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))
    model_name = "claude-sonnet-4-0"
    results = []
    
    for test_case in eval_set['translations']:
        # Format the user message
        english_text = test_case['english']  
        user_msg = prompt_config['user_template'].format(
            english_text=test_case['english']
        )
        
        # Call the LLM
        response = client.messages.create(
            model=model_name,
            max_tokens=100,
            system=prompt_config['system']['role'],
            messages=[{"role": "user", "content": user_msg}]
        )
        # Score the response
        actual_output = parse_output(response.content[0].text)

        print(f"user_msg: {user_msg}")
        print(f"Actual: {actual_output}")
        # print(f"Score: {score}")

        # Prepare expected output (match your data structure)
        expected_output = {
            'italian': test_case['italian'],
            'french': test_case['french'],
            'sentiment': test_case['sentiment'],
            'sentence_type': test_case['type'],
            'notes': test_case.get('notes', '')
        }
        
        # Score with breakdown
        total_score, score_breakdown = calculate_score(
            expected=expected_output,
            actual=actual_output,
            category=test_case.get('category', 'general')
        )
        
        results.append({
            "english": english_text,
            "expected": expected_output,
            "actual": actual_output,
            "total_score": total_score,
            "score_breakdown": score_breakdown,
            "status": "success",
            "passed": total_score >= 0.75  # Adjust threshold as needed
        })
    
    return results


# %%
if __name__ == "__main__":

    prompt = load_prompt("prompts/fr_it_prompt_v1.yml")
    eval_set = load_eval_set("evaluations/fr_it_prompt_eval_v1.json")

    prompt = load_prompt(f"{Path.cwd()}/prompts/fr_it_prompt_v1.yml")
    eval_set = load_eval_set(f"{Path.cwd()}/evaluations/fr_it_prompt_eval_v1.json") 
    
    results = run_evaluation(prompt, eval_set)

        # Save results
    Path("evaluations/results").mkdir(parents=True, exist_ok=True)
    with open("evaluations/results/latest_eval.json", "w") as f:
        json.dump(results, f, indent=2)

    # Print summary
    passed = sum(1 for r in results if r.get('passed', False))
    print(f"✓ Evaluation complete: {passed}/{len(results)} passed")




