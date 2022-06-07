SELECT berta_document_exercises.id AS exercise_id, berta_documents.id AS document_id, berta_document_exercises.text, berta_document_exercises.alternatives, berta_documents.plain_text
FROM berta_document_exercises
LEFT JOIN berta_documents ON berta_documents.id = berta_document_exercises.document_id
WHERE berta_document_exercises.type_id = 3 AND berta_documents.status_id <> 4 ORDER BY berta_documents.id ASC
