create table  if not exists posts (
id integer primary key autoincrement,
name text not null,
email text not null,
post text not null,
message text not null,
time integer not null
);
