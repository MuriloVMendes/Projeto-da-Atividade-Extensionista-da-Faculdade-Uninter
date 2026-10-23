-- Execute este arquivo uma única vez no SQL Editor do Supabase.

create table if not exists public.feedbacks (
    id uuid primary key default gen_random_uuid(),
    nome varchar(60) not null,
    anonimo boolean not null default false,
    avaliacao smallint not null check (avaliacao between 0 and 5),
    comentario varchar(500) not null check (char_length(comentario) between 10 and 500),
    autorizou_publicacao boolean not null check (autorizou_publicacao = true),
    criado_em timestamptz not null default now()
);

alter table public.feedbacks enable row level security;

revoke update, delete on table public.feedbacks from anon, authenticated;
grant select, insert on table public.feedbacks to anon, authenticated;

drop policy if exists "feedbacks_publicos_podem_ser_lidos" on public.feedbacks;
create policy "feedbacks_publicos_podem_ser_lidos"
on public.feedbacks for select
to anon, authenticated
using (autorizou_publicacao = true);

drop policy if exists "visitantes_podem_enviar_feedback" on public.feedbacks;
create policy "visitantes_podem_enviar_feedback"
on public.feedbacks for insert
to anon, authenticated
with check (
    autorizou_publicacao = true
    and avaliacao between 0 and 5
    and char_length(comentario) between 10 and 500
    and char_length(nome) between 3 and 60
);
