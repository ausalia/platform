-- The original demo seed used "Agrícola Punto Azul" - the name of a real
-- company (its real KML property survey supplied the boundary shapes for
-- the old prototype dashboard's farm map). Renaming to a generic, clearly
-- fictional name for the public demo.
update organizations
set name = 'Campo Verde'
where id = '00000000-0000-0000-0000-000000000001';
