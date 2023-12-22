from unittest.mock import Mock, patch
from pipeline import bigquery_posts, bigquery_comments  # Import the module you want to test

def test_get_top_tags_data():
    bq_client_mock = Mock()
    bq_client_mock.query.return_value.result.return_value = [
        ("tag1", 10),
        ("tag2", 8),
        ("tag3", 6),
    ]
    
    with patch("pipeline.bigquery_posts", bq_client_mock):
        top_tags = bigquery_posts.get_top_tags_data(bq_client_mock)
    
    assert top_tags == ["tag1", "tag2", "tag3"]

def test_insert_data_into_posts_table():
    bq_client_mock = Mock()
    bq_client_mock.query.return_value.result.return_value = None
    
    top_tags = ["tag1", "tag2", "tag3"]
    
    with patch("pipeline.bigquery_posts", bq_client_mock):
        bigquery_posts.insert_data_into_posts_table(bq_client_mock, top_tags)


    expected_query = f"""
        INSERT INTO StackAI.posts_cleaned (question_id, question_title, question_body, question_tags, accepted_answer, question_creation_date, accepted_answer_creation_date, accepted_answer_owner_display_name, owner_reputation, accepted_answer_score, accepted_answer_view_count)
        WITH posts_answers AS (
            SELECT
                p1.id AS question_id,
                p1.title AS question_title,
                p1.body AS question_body,
                p1.tags AS question_tags,
                p2.body AS accepted_answer,
                p1.creation_date AS question_creation_date,
                p2.creation_date AS accepted_answer_creation_date,
                u.display_name AS accepted_answer_owner_display_name,
                u.reputation AS owner_reputation,
                p2.score AS accepted_answer_score,
                p2.view_count AS accepted_answer_view_count
            FROM
                `bigquery-public-data.stackoverflow.posts_questions` p1
            LEFT JOIN
                `bigquery-public-data.stackoverflow.posts_answers` p2
            ON
                p1.accepted_answer_id = p2.id
            LEFT JOIN
                `bigquery-public-data.stackoverflow.users` u
            ON
                p2.owner_user_id = u.id
            WHERE
                REGEXP_CONTAINS(p1.tags, r'{top_tags[0]}|{top_tags[1]}|{top_tags[2]}')
        )
        SELECT *
        FROM posts_answers limit 500
    """
    
    # Add assertions here to check the behavior of the function after data insertion
    # For example, you could assert that the query was executed and the job was waited for
    # You might also want to check the call arguments to the mock
    assert bq_client_mock.query.called
    assert bq_client_mock.query.call_args[0][0] == expected_query

def test_insert_data_into_comments_table():
    bq_client_mock = Mock()
    bq_client_mock.query.return_value.result.return_value = None
    
    with patch("pipeline.bigquery_comments", bq_client_mock):
        bigquery_comments.insert_data_into_comments_table(bq_client_mock)
    
    # Define the expected query based on your requirements
    expected_query = """
        INSERT INTO StackAI.comments_cleaned (post_id, text, creation_date, score)
        SELECT
            c.post_id,
            c.text,
            c.creation_date,
            c.score
        FROM
            `bigquery-public-data.stackoverflow.comments` c
        JOIN
            `stackai-394819.StackAI.posts_cleaned` p
        ON 
            c.post_id = p.question_id
    """
    
    # Add assertions here to check the behavior of the function after data insertion
    # For example, you could assert that the query was executed and the job was waited for
    # You might also want to check the call arguments to the mock
    assert bq_client_mock.query.called
    assert bq_client_mock.query.call_args[0][0] == expected_query

