delete table public.company;
drop table if exists public.company;

DROP POLICY IF EXISTS "read own rows" ON company;
DROP POLICY IF EXISTS "insert as self" ON company;
DROP POLICY IF EXISTS "update own rows" ON company;
DROP POLICY IF EXISTS "delete own rows" ON company;

create table public.company
 (
  company_id uuid not null default gen_random_uuid (),
  owner_id SET DEFAULT get_owner_id((auth.uid())::text),
  name text not null,
  name_first text not null,
  name_last text not null,
  active boolean not null default true,
  note text not null,
  created_at timestamp with time zone not null default now(),
  constraint company_pkey primary key (company_id)
) TABLESPACE pg_default;

-- zapnutí RLS - každý vidí svoje řádky
ALTER TABLE company ENABLE ROW LEVEL SECURITY;

create policy "read own rows"
on company for select
to authenticated
using (owner_id = get_owner_id ());

-- INSERT: smí vložit jen jako sám sebe
create policy "insert as self"
on company for insert
to authenticated
with check (owner_id = get_owner_id ());

-- UPDATE: může měnit jen své řádky
create policy "update own rows"
on company for update
to authenticated
using (owner_id = get_owner_id ())
with check (owner_id = get_owner_id ());

-- DELETE: může mazat jen své řádky (pokud chceš)
create policy "delete own rows"
on company for delete
to authenticated
using (owner_id = get_owner_id ());





CREATE TABLE accounts (
  account_id text PRIMARY KEY DEFAULT gen_random_uuid(),
  auth_id text UNIQUE NOT NULL,
  owner_id text NOT NULL,
  email text NOT NULL,
  is_active boolean DEFAULT true, 
  created_at timestamp NOT NULL DEFAULT now()
);

