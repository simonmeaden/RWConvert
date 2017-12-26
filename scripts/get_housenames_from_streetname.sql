SELECT housenames.name
FROM housenames, streetname
WHERE
	streetname.name = {street} AND
	housenames.street_id = streetname.id