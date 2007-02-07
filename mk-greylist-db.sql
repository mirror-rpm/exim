CREATE TABLE resenders (
	host		TEXT PRIMARY KEY,
	helo		TEXT,
	time		INTEGER
);

CREATE TABLE greylist (
	id		TEXT PRIMARY KEY,
	expire		INTEGER,
	host		TEXT,
	helo		TEXT
);
