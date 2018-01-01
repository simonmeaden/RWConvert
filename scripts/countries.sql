CREATE TABLE IF NOT EXISTS countries (
	"common" TEXT,
	"official" TEXT,
	"native_id" INTEGER,
	"tld_id" INTEGER,
	"cca2" CHAR(2),
	"cca3" CHAR(3),
	"ccn3" CHAR(3),
	"cioc" CHAR(3),
	"currency_id" INTEGER,
	"calling_code_id" INTEGER,
	"capital" TEXT,
	"altspellings" INTEGER,
	"region" TEXT,
	"subregion" TEXT,
	"language_id" INTEGER,
	"translations" INTEGER,
	"lat" TEXT,
	"lon" TEXT,
	"demonym" TEXT,
	"landlocked" BOOLEAN,
	"borders" INTEGER,
	"area" INTEGER
);
CREATE TABLE IF NOT EXISTS tld (
	"id" INTEGER,
	"tld" CHAR(3)
);
CREATE TABLE IF NOT EXISTS native (
	"id" INTEGER,
	"language" CHAR(3),
	"official" TEXT,
	"common" TEXT
);
CREATE TABLE IF NOT EXISTS currency (
	"id" INTEGER,
	"name" CHAR(3)
);
CREATE TABLE IF NOT EXISTS callingcode (
	"id" INTEGER,
	"code" CHAR(3)
);
CREATE TABLE IF NOT EXISTS altspellings (
	"id" INTEGER,
	"altspelling" TEXT
);
CREATE TABLE IF NOT EXISTS languages (
	"id" INTEGER,
	"code" CHAR(3),
	"name" TEXT
);
CREATE TABLE IF NOT EXISTS translations (
	"id" INTEGER,
	"language" CHAR(3),
	"official" TEXT,
	"common" TEXT
);
CREATE TABLE IF NOT EXISTS borders (
	"id" INTEGER,
	"border" CHAR(3)
);

