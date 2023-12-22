#creates, bigquery dataset and tables - posts, comments
provider "google" {
  credentials = file("/etc/gcp/credentials.json")
  project     = "stackai-394819"
  region      = "us-west2"
}

resource "google_bigquery_dataset" "stackai" {
  dataset_id = "StackAI"
  location = "US"
}

resource "google_bigquery_table" "posts_cleaned" {
  dataset_id = google_bigquery_dataset.stackai.dataset_id
  table_id   = "posts_cleaned"

  schema = jsonencode([
    {
      name = "question_id",
      type = "INTEGER"
    },
    {
      name = "question_title",
      type = "STRING"
    },
    {
      name = "question_body",
      type = "STRING"
    },
    {
      name = "question_tags",
      type = "STRING"
    },
    {
      name = "accepted_answer",
      type = "STRING"
    },
    {
      name = "question_creation_date",
      type = "TIMESTAMP"
    },
    {
      name = "accepted_answer_creation_date",
      type = "TIMESTAMP"
    },
    {
      name = "accepted_answer_owner_display_name",
      type = "STRING"
    },
    {
      name = "owner_reputation",
      type = "INTEGER"
    },
    {
      name = "accepted_answer_score",
      type = "INTEGER"
    },
    {
      name = "accepted_answer_view_count",
      type = "STRING"
    }
  ])
  deletion_protection = false
}

resource "google_bigquery_table" "comments_cleaned" {
  dataset_id = google_bigquery_dataset.stackai.dataset_id
  table_id   = "comments_cleaned"

  schema = jsonencode([
    {
      name = "post_id",
      type = "INTEGER"
    },
    {
      name = "text",
      type = "STRING"
    },
    {
      name = "creation_date",
      type = "TIMESTAMP"
    },
    {
      name = "score",
      type = "INTEGER"
    }
  ])
  deletion_protection = false
}