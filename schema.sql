pragma foreign_keys = on;

create table papers (
    id text primary key,
    version integer,
    category text,
    title text,
    authors text,
    published integer,
    updated integer,
    summary text,
    state integer default 0,
    new integer default 1
);

create index papers_published on papers(published);
create index papers_updated on papers(updated);

create table authors (
    id integer primary key,
    author text,
    paper text,
    foreign key(paper) references papers(id)
);