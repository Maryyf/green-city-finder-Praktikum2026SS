from typing import Optional

from src.pipeline import pipeline


# Define the clear function dynamically based on the number of inputs
def clear(*args):
    return tuple([None] * len(args))  # Return None for each input/output component dynamically


def generate_text(
                  country: Optional[str],
                  starting_point: Optional[str],
                  query_text: str,
                  model: Optional[str] = "gemini-2.5-flash",
                  max_tokens: Optional[int] = 2048,
                  temp: Optional[float] = 0.49,
                  start_date: Optional[str] = None,
                  end_date: Optional[str] = None,
                  is_sustainable: Optional[bool] = False,
                  ):
    model_params = {
        'max_tokens': max_tokens,
        'temperature': temp
    }
    pipeline_response = pipeline(
        query=query_text,
        model_name=model,
        sustainability=is_sustainable,
        starting_point=starting_point,
        start_date=start_date,
        end_date=end_date,
        **model_params
    )

    print("DEBUG country =", country)
    print("DEBUG starting_point =", starting_point)
    print("DEBUG query_text =", query_text)
    print("DEBUG model =", model)
    print("DEBUG max_tokens =", max_tokens)
    print("DEBUG temp =", temp)

    if pipeline_response is None:
        return "Error while generating response! Please try again."
    return pipeline_response
