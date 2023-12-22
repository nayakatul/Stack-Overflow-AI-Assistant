#create and store embeddings for each post in BigQuery table
from google.cloud import bigquery
import pandas as pd
from sentence_transformers import SentenceTransformer

def generate_and_store_embeddings(project_id, table_name):
    # Set up BigQuery client with explicit project ID
    bq_client = bigquery.Client(project=project_id)

    # Set up query
    query = f"""
        SELECT *
        FROM `{table_name}`
    """

    # Run query and fetch results into pandas DataFrame
    df = bq_client.query(query).to_dataframe()

    # Concatenate relevant columns for embedding, handling NaN values
    relevant_text = df.apply(lambda row: ' '.join(filter(lambda x: pd.notna(x), [row['question_title'], row['question_body'] , row['accepted_answer']])), axis=1)

    # Convert relevant_text to a list
    relevant_text_list = relevant_text.tolist()

    # Load the pre-trained Sentence Transformers model
    model = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')

    def generate_embeddings(text):
        embeddings = model.encode(text)
        return embeddings

    # Generate embeddings for relevant data
    data_embeddings = generate_embeddings(relevant_text_list)

    # Add new column to DataFrame with embeddings
    df['embeddings'] = data_embeddings.tolist()

    # Update BigQuery table with new column
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",
        schema=[
            bigquery.SchemaField("embeddings", "STRING"),
        ],
    )

    job = bq_client.load_table_from_dataframe(
        df, table_name, job_config=job_config
    )
    job.result()  # Waits for table load to complete.
    print(f"Embeddings generated and stored in {table_name}.")
    
generate_and_store_embeddings('stackai-394819', 'stackai-394819.StackAI.posts_cleaned')
