select housenames.name, streetname.name
from streetname, postcode, housenames
where
  postcode.code={postcode} and
  postcode.street_id = streetname.id and
  streetname.id = housenames.street_id