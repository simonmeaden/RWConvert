SELECT streetname.name
FROM streetname, postcode
WHERE
	postcode.code={postcode} AND
	postcode.street_id = streetname.id