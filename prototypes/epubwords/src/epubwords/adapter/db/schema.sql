CREATE TABLE IF NOT EXISTS ebooks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chapters (
    ebook_id INTEGER,
    chapter_number INTEGER,
    content TEXT NOT NULL,
    PRIMARY KEY (ebook_id, chapter_number),
    FOREIGN KEY (ebook_id) REFERENCES ebooks(id)
);