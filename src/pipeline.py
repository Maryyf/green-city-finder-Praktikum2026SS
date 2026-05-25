"""
Main file to execute the TRS Pipeline.
"""
import sys
from augmentation import prompt_generation as pg
from information_retrieval import info_retrieval as ir
from text_generation.models import (
    Llama3,
    Mistral,
    Gemma2,
    Llama3Point1,
    Llama3Instruct,
    MistralInstruct,
    Llama3Point1Instruct,
    Phi3SmallInstruct,
    GPT4,
    Gemini,
    Claude3Point5Sonnet,
)
from text_generation import text_generation as tg
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)
from src.text_generation.mapper import MODEL_MAPPER
from src.post_processing.post_process import post_process_output

TEST_DIR = "../tests/"

MODELS = {
    'GPT-4': GPT4,
    'Llama3': Llama3,
    'Mistral': Mistral,
    'Gemma2': Gemma2,
    'Llama3.1': Llama3Point1,
    'Llama3-Instruct': Llama3Instruct,
    'Mistral-Instruct': MistralInstruct,
    'Llama3.1-Instruct': Llama3Point1Instruct,
    'Phi3-Instruct': Phi3SmallInstruct,
    "Gemini-1.0-pro": Gemini,
    "Claude3.5-sonnet": Claude3Point5Sonnet,
}


def pipeline(starting_point: str,
             query: str,
             model_name: str,
             test: int = 0, **params):
    """
    
    Executes the entire RAG pipeline, provided the query and model class name.

    Args: 
        - query: str
        - model_name: string, one of the following: Llama3, Mistral, Gemma2, Llama3Point1
        - test: whether the pipeline is running a test
        - params: 
            - limit (number of results to be retained) 
            - reranking (binary, whether to rerank results using ColBERT or not)
            - sustainability
            - cost_of_living
            - start_date (optional, for travel date range)
            - end_date (optional, for travel date range)

    
    """
    try:
        model_id = MODEL_MAPPER[model_name]
    except KeyError:
        logger.error(f"Model {model_name} not found in the model mapper.")
        model_id = MODEL_MAPPER['Gemini-1.0-pro']
    context_params = {
        'limit': 10,
        'reranking': 0,
        'sustainability': 0,
        'cost_of_living':0,
        'carbon_footprint': 1,
    }
    
    if 'carbon_footprint' in params:
        context_params['carbon_footprint'] = params['carbon_footprint']
        context_params['carbon_footprint_preference'] = params.get('carbon_footprint_preference')

    if 'limit' in params:
        context_params['limit'] = params['limit']

    if 'reranking' in params:
        context_params['reranking'] = params['reranking']

    if 'sustainability' in params:
        context_params['sustainability'] = params['sustainability']

    if 'cost_of_living' in params:
        context_params['cost_of_living'] = params['cost_of_living']
    context_params['cost_preference'] = params.get('cost_preference')
    # print("DEBUG pipeline params =", params)
    # print("DEBUG pipeline cost_preference =", params.get("cost_preference"))
    # Extract optional travel date range from params and forward to context params
    start_date = params.get('start_date')
    end_date = params.get('end_date')
    if start_date:
        context_params['start_date'] = start_date
    if end_date:
        context_params['end_date'] = end_date

    logger.info(f"Received travel dates: start_date={start_date}, end_date={end_date}")

    logger.info("Retrieving context..")
    try:
        context = ir.get_context(starting_point=starting_point, query=query, **context_params)
        if test:
            retrieved_cities = ir.get_cities(context)
        else:
            retrieved_cities = None

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(f"Error at line {exc_tb.tb_lineno} while trying to get context: {e}")
        return None

    logger.info("Retrieved context, augmenting prompt..")
    try:
        prompt = pg.augment_prompt(
            query=query,
            starting_point=starting_point,
            context=context,
            params=context_params
        )
        '''
        print("\n" + "=" * 80)
        print("DEBUG PROMPT SENT TO LLM")
        print("=" * 80)

        for i, message in enumerate(prompt):
            print(f"\n--- MESSAGE {i + 1}: {message.get('role', 'unknown').upper()} ---")
            print(message.get("content", ""))

        print("=" * 80 + "\n")
        '''
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(f"Error at line {exc_tb.tb_lineno} while trying to augment prompt: {e}")
        return None

    # return prompt

    logger.info(f"Augmented prompt, initializing {model_name} and generating response..")
    try:
        response = tg.generate_response(model_id, prompt, **params)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.info(f"Error at line {exc_tb.tb_lineno} while generating response: {e}")
        return None

    try:
        # Safely read model generation params (may be None if not provided by the UI)
        model_params = {"max_tokens": params.get("max_tokens"), "temperature": params.get("temperature")}
        # Forward optional travel dates so downstream components can use them
        if start_date:
            model_params["start_date"] = start_date
        if end_date:
            model_params["end_date"] = end_date

        post_processed_response = post_process_output(
            model_id=model_id, user_query=query,
            starting_point=starting_point,
            context=context, response=response, **model_params)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.info(f"Error at line {exc_tb.tb_lineno} while generating response: {e}")
        return None
    if test:
        return retrieved_cities, prompt[1]['content'], post_processed_response

    else:
        return post_processed_response


if __name__ == "__main__":
    # sample_query = "I'm planning a trip in the summer and I love art, history, and visiting museums. Can you
    # suggest " \ "some " \ "European cities? "
    sample_query = "I'm planning a trip in July and enjoy beaches, nightlife, and vibrant cities. Recommend some " \
                   "cities. "
    model_name = "GPT-4"

    pipeline_response = pipeline(
        query=sample_query,
        model_name=model_name,
        sustainability=1
    )

    print(pipeline_response)
