create table public.company
 (
  company_id uuid not null default gen_random_uuid (),
  owner_id text not null default (auth.uid ())::text,
  name text not null,
  name_first text not null,
  name_last text not null,
  active boolean not null default true,
  note text not null,
  created_at timestamp with time zone not null default now(),
  constraint company_pkey primary key (company_id)
) TABLESPACE pg_default;

-- SELECT: uživatel vidí jen své řádky
create policy "read own rows"
on company for select
to authenticated
using (owner_id = auth.uid()::text);

-- INSERT: smí vložit jen jako sám sebe
create policy "insert as self"
on company for insert
to authenticated
with check (owner_id = auth.uid()::text);

-- UPDATE: může měnit jen své řádky
create policy "update own rows"
on company for update
to authenticated
using (owner_id = auth.uid()::text)
with check (owner_id = auth.uid()::text);

-- DELETE: může mazat jen své řádky (pokud chceš)
create policy "delete own rows"
on company for delete
to authenticated
using (owner_id = auth.uid()::text);