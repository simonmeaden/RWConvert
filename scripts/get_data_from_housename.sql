SELECT
housename.name,
street.name,
city.name,
region.name,
countries.common,
housename.latitude,
housename.longitude
FROM
housename, street, city, region, countries
WHERE
housename.name = {housename} AND
street.name = {streetname} AND
housename.street_id = street.id AND
street.city_id = city.id AND
city.region_id = region.id AND
region.country_id = countries.native_id
;
