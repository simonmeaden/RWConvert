CREATE TABLE IF NOT EXISTS "housename" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "street_id" INTEGER,
    "name" VARCHAR(50),
    "latitude" INTEGER,
    "longitude" INTEGER
);
CREATE TABLE IF NOT EXISTS "postcode" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "street_id" INTEGER,
    "code" VARCHAR(20),
    "def_longitude" INTEGER,
    "def_latitude" INTEGER
);
CREATE TABLE IF NOT EXISTS "region" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "name" VARCHAR(50),
    "country_id" INTEGER);
CREATE TABLE IF NOT EXISTS "city" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "name" VARCHAR(20),
    "region_id" INTEGER);
CREATE TABLE IF NOT EXISTS "street" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "city_id" INTEGER,
    "name" VARCHAR(50)
);
