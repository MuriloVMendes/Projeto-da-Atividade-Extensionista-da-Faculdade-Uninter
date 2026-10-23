# StudyTrack

Aplicação acadêmica para organização de estudos e inclusão digital, com Streamlit e Supabase.

## Executar no Windows

Abra o terminal nesta pasta, onde está StudyTrack.py:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Copie `.streamlit/secrets.toml.example` para `.streamlit/secrets.toml` e preencha com a URL e a chave pública do seu projeto Supabase. Se já possui um arquivo configurado, reutilize-o.

```powershell
.\.venv\Scripts\python.exe -m streamlit run StudyTrack.py
```

## Estrutura

- `StudyTrack.py`: entrada e navegação.
- `auth.py`: cadastro, login e sessão individual.
- `operations.py`: disciplinas, estudos, cálculos, datas e feedbacks.
- `comunidade_db.py`: perfis, feed, comentários, curtidas, grupos e ranking.
- `style.py`: estilos da interface.
- `paginas/`: telas da aplicação.
- `.streamlit/`: configuração visual e exemplo de credenciais.
- `data/feedbacks.json`: armazenamento opcional para testes locais de feedback; criado automaticamente caso esteja ausente.
- `sql/`: scripts existentes de configuração dos feedbacks e atualização dos grupos.

## Banco existente

O projeto usa as tabelas de disciplinas, sessões, feedbacks e comunidade já configuradas no Supabase. A organização dos arquivos não exige alteração no banco nem nova execução de SQL. Os scripts de `sql/` são mantidos para manutenção; eles não constituem uma instalação completa de um banco novo.

O ranking é semanal e opcional. Grupos e conteúdo da comunidade ficam visíveis aos participantes autenticados. As metas e sessões são individuais. O Pomodoro registra ciclos de foco concluídos; mantenha sua página aberta até terminar o ciclo.

## Publicação

Envie o conteúdo desta pasta ao repositório, com `StudyTrack.py` na raiz. Não envie ambientes virtuais, caches nem `.streamlit/secrets.toml`. Configure o conteúdo desse arquivo em Secrets da hospedagem. Use `requirements.txt` para instalar as dependências e `StudyTrack.py` como entrada. Ajuste a URL do aplicativo nas configurações de autenticação do Supabase quando publicar.

Antes de convidar participantes, teste duas contas: os estudos devem ser separados e as interações da comunidade compartilhadas. Apenas o criador pode editar seus grupos.
