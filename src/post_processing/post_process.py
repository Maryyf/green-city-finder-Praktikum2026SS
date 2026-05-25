from src.text_generation.text_generation import generate_response


def post_process_output(model_id: str, user_query: str, starting_point: str, response: str, context: dict, **params: dict) -> str | None:
    if "s-fairness" in response.lower() or "score" in response.lower() or "sustainability data" in response.lower():
        formatted_response = \
            f"You are an AI recommendation system focused on sustainable travel. Rewrite this response without " \
            f"mentioning the sustainability score or s-fairness.\n {response} "
    elif "the provided context does not have the answer" \
            in response.lower():
        formatted_response = \
            f'You are an AI recommendation system focused on sustainable travel. Rewrite this response using the information from the context: \n Starting point: {starting_point}\n Query: {user_query}\n Context: {context}'
    else:
        formatted_response = response
        return response

    final_prompt = [{"role": "system", "content": formatted_response}]
    
    # print post-process prompt for debugging
    '''
    print("\n" + "=" * 80)
    print("DEBUG POST-PROCESS PROMPT SENT TO LLM")
    print("=" * 80)

    print("\n--- ORIGINAL RESPONSE BEFORE POST-PROCESSING ---")
    print(response)

    print("\n--- POST-PROCESS FINAL PROMPT ---")
    for i, message in enumerate(final_prompt):
        print(f"\nMESSAGE {i + 1} ROLE: {message.get('role', 'unknown').upper()}")
        print(message.get("content", ""))

    print("=" * 80 + "\n")
    '''
    
    generated_response = generate_response(model_id,
                                           final_prompt, **params)
    return generated_response
