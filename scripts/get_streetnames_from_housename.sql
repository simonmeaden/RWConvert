SELECT streetname.name
FROM housenames, streetname
WHERE
	housenames.name = {housename} AND
	housenames.street_id = streetname.id