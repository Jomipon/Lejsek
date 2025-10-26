CREATE OR REPLACE FUNCTION get_owner_id()
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
  v_owner_id TEXT;
BEGIN
  SELECT owner_id INTO v_owner_id from accounts where auth_id = (auth.uid ())::text LIMIT 1;
  RETURN v_owner_id;
END;
$$;

CREATE OR REPLACE FUNCTION create_owner_id()
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
  v_owner_id text; 
  v_auth_id text := auth.uid()::text; 
  v_email text := auth.jwt() ->> 'email';
BEGIN
  -- Pokus o založení záznamu; při duplicitě na auth_id vrátí existující řádek
  INSERT INTO accounts (auth_id, email, owner_id)
  VALUES (auth.uid()::text, auth.jwt() ->> 'email', gen_random_uuid()::text)
  ON CONFLICT (auth_id) DO UPDATE
    SET auth_id = EXCLUDED.auth_id  -- no-op, jen aby šlo použít RETURNING
  RETURNING owner_id INTO v_owner_id;
  
  INSERT INTO settings (settings_id, owner_id) VALUES (v_auth_id, v_owner_id) ON CONFLICT (settings_id) DO NOTHING;
  
  RETURN v_owner_id;
END;
$$;

CREATE OR REPLACE FUNCTION set_email(p_email TEXT)
RETURNS boolean
LANGUAGE sql
AS $$
  WITH upd AS (
    UPDATE accounts
       SET email = p_email
     WHERE owner_id = auth.uid()::text
       AND email IS DISTINCT FROM p_email   -- bezpečné i kdyby někdy nebyl NOT NULL
     RETURNING 1
  )
  SELECT EXISTS(SELECT 1 FROM upd);
$$;
