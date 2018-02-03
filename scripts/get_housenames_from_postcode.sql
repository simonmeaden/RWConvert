SELECT housenames.name
FROM streetname, postcode, housenames
WHERE
	postcode.name={postcode} AND
	postcode.street_id = streetname.id AND
	streetname.id = housenames.street_id
