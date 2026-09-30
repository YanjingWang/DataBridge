DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    country TEXT NOT NULL,
    status TEXT NOT NULL,
    signup_year INTEGER NOT NULL
);

INSERT INTO customers (name, email, country, status, signup_year) VALUES
    ('Alice Johnson', 'alice@example.com', 'United States', 'active', 2021),
    ('Bob Smith', 'bob@gmail.com', 'United States', 'active', 2019),
    ('Carlos García', 'carlos@domain.de', 'Germany', 'inactive', 2020),
    ('Diana Lee', 'diana@korea.kr', 'India', 'active', 2022),
    ('Frank Brown', 'frank@brown.uk', 'United Kingdom', 'active', 2018),
    ('Grace Kim', 'grace@email.com', 'India', 'inactive', 2020),
    ('Henry Wilson', 'henry@company.com', 'United States', 'active', 2019),
    ('Isabel Cruz', 'isabel@cruz.mx', 'India', 'active', 2021),
    ('Jack Taylor', 'jack@taylor.au', 'Australia', 'active', 2020),
    ('Laura Chen', 'laura.chen@gmail.com', 'United States', 'active', 2022),
    ('Mike Davis', 'mike@davis.com', 'United States', 'active', 2020),
    ('Nina Patel', 'nina@india.in', 'Germany', 'active', 2021),
    ('Oscar Brown', 'oscar@brown.de', 'Germany', 'active', 2019),
    ('Paula Scott', 'paula@scott.ca', 'France', 'inactive', 2020),
    ('Rachel Green', 'rachel@green.us', 'United States', 'active', 2018),
    ('Tina Moore', 'tina@moore.com', 'United States', 'active', 2021),
    ('Uma Patel', 'uma@patel.in', 'India', 'active', 2020),
    ('Victor Hugo', 'victor@hugo.fr', 'France', 'active', 2019),
    ('Wendy Clark', 'wendy@clark.com', 'United States', 'inactive', 2021),
    ('Xander Reed', 'xander@reed.au', 'Australia', 'active', 2022),
    ('Yuki Tanaka', 'yuki@tanaka.jp', 'United Kingdom', 'active', 2020),
    ('Zoe Williams', 'zoe@williams.com', 'United Kingdom', 'active', 2020);