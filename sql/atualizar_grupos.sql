-- Execute todo este arquivo no SQL Editor do Supabase.
-- Requer as tabelas da comunidade já instaladas. Preserva os grupos existentes.
begin;

alter table public.comunidade_grupos
    add column if not exists criador_id uuid references auth.users(id) on delete set null,
    add column if not exists area text not null default 'Tecnologia',
    add column if not exists criado_em timestamptz not null default now();

alter table public.comunidade_grupos
    drop constraint if exists comunidade_grupos_campos_validos;
alter table public.comunidade_grupos
    add constraint comunidade_grupos_campos_validos check (
        char_length(trim(nome)) between 3 and 80
        and char_length(trim(descricao)) between 3 and 500
        and char_length(trim(area)) between 2 and 60
    );

-- Nomes iguais, desconsiderando maiúsculas e espaços repetidos, não se duplicam.
create unique index if not exists comunidade_grupos_nome_normalizado_idx
on public.comunidade_grupos (
    lower(regexp_replace(btrim(nome), '[[:space:]]+', ' ', 'g'))
);

-- Renomear um grupo preserva publicações e vínculos de todos os membros.
alter table public.comunidade_membros
    drop constraint if exists comunidade_membros_grupo_fkey;
alter table public.comunidade_membros
    add constraint comunidade_membros_grupo_fkey
    foreign key (grupo) references public.comunidade_grupos(nome)
    on update cascade on delete cascade;

alter table public.comunidade_posts
    drop constraint if exists comunidade_posts_grupo_fkey;
alter table public.comunidade_posts
    add constraint comunidade_posts_grupo_fkey
    foreign key (grupo) references public.comunidade_grupos(nome)
    on update cascade;

alter table public.comunidade_grupos enable row level security;
revoke all on public.comunidade_grupos from anon, authenticated;
grant select on public.comunidade_grupos to authenticated;
grant insert (nome, descricao, area, criador_id)
    on public.comunidade_grupos to authenticated;
grant update (nome, descricao, area)
    on public.comunidade_grupos to authenticated;

-- O criador é imutável na API. Os grupos iniciais permanecem sem dono.
drop policy if exists leitura_grupos on public.comunidade_grupos;
create policy leitura_grupos on public.comunidade_grupos
for select to authenticated using (true);

drop policy if exists criar_proprio_grupo on public.comunidade_grupos;
create policy criar_proprio_grupo on public.comunidade_grupos
for insert to authenticated
with check (
    criador_id = (select auth.uid())
    and exists (
        select 1 from public.comunidade_perfis p
        where p.usuario_id = (select auth.uid())
    )
);

drop policy if exists editar_proprio_grupo on public.comunidade_grupos;
create policy editar_proprio_grupo on public.comunidade_grupos
for update to authenticated
using (criador_id = (select auth.uid()))
with check (criador_id = (select auth.uid()));

-- Grupo e primeira participação são gravados na mesma transação.
-- SECURITY INVOKER mantém as permissões e o RLS do usuário conectado.
create or replace function public.comunidade_adicionar_criador()
returns trigger
language plpgsql
security invoker
set search_path = ''
as $$
begin
    if new.criador_id is not null then
        insert into public.comunidade_membros (usuario_id, grupo)
        values (new.criador_id, new.nome)
        on conflict (usuario_id, grupo) do nothing;
    end if;
    return new;
end;
$$;

revoke all on function public.comunidade_adicionar_criador()
    from public, anon, authenticated;

drop trigger if exists comunidade_grupo_primeiro_membro
    on public.comunidade_grupos;
create trigger comunidade_grupo_primeiro_membro
    after insert on public.comunidade_grupos
    for each row execute function public.comunidade_adicionar_criador();

commit;
