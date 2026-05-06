green-city-finder/
  -database
  -european-city-data/
    -city_abstracts_embeddings.csv
  -env

export HF_TOKEN=your Hugging Face TOKEN
export GOOGLE_CREDENTIALS="$(base64 -w 0 /your/path/to/green-city-finder/green-city-finder-aec7003fcaf7.json)"
export VERTEXAI_PROJECTID=green-city-finder
export DATA_REPO=ashmib/wikivoyage-eu-city-embeddings
export BUCKET_NAME=/your/path/to/green-city-finder/database/wikivoyage