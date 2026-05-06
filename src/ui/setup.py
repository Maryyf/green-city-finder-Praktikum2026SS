from src.helpers.data_loaders import load_places


# TODO add the gcp application json file loading
# TODO examples

def load_html_from_file(file_path: str) -> str:
    """
    Reads the HTML content from a file and returns it as a string.

    Args:
        file_path (str): The path to the HTML file.

    Returns:
        str: The HTML content of the file.
    """
    with open(file_path, 'r') as file:
        return file.read()

