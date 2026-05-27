-- vector_column
-- depends: 20260525_01_create_extension

ALTER TABLE papers ADD COLUMN title_embeddings halfvec(128);
