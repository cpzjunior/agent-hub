

🇺🇸 [English](README.md) | 🇧🇷 [Português](README.pt-BR.md)

# Hub de Agentes

Um ambiente de trabalho modular para criar, organizar e orquestrar agentes de IA, com habilidades, ferramentas e recursos compartilhados encapsulados.

## Objetivos

- Organizar agentes como módulos independentes.
- Encapsular habilidades e ferramentas específicas de cada agente.
- Compartilhar recursos comuns por meio do núcleo.
- Oferecer suporte a agentes simples e baseados em fluxos de trabalho.
- Disponibilizar agentes por meio de um servidor MCP.

## Requisitos

- Python 3.12+
- Git

## Configuração

Execute os seguintes comandos a partir da raiz do projeto usando PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Se o PowerShell bloquear a execução de scripts:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Agentes

Atualmente, o ambiente de trabalho inclui:

- Git Agent — executa operações Git em repositórios locais.
- Agent Builder — auxilia na criação e no aprimoramento de agentes, habilidades e ferramentas.
- Archmage Scribe — desenvolve conceitos de mundos de fantasia, mantém a consistência com um repositório local de cânone e escreve textos ambientados nesses mundos.
- Bookmark Agent — cria, extrai, descreve e classifica favoritos.
- Decision Architect — oferece suporte à análise de decisões por meio de um processo iterativo que abrange contexto, objetivos, incertezas, consequências e evolução.
- Project Ideas Agent — gera documentos estruturados de ideias de projetos.
- Writing Assistant — explora ideias, escreve, revisa, resume e traduz artigos, preservando a voz editorial do autor.

Cada agente possui suas próprias instruções, fluxos de trabalho e ferramentas, quando aplicável. A interpretação por LLM é fornecida por meio de implementações intercambiáveis da interface principal `Interpreter`, atualmente com suporte a OpenAI e Anthropic.

## Servidor MCP

O servidor MCP expõe os agentes registrados como ferramentas por meio do transporte padrão de entrada/saída (`stdio`).

Cada agente é exposto por meio de uma ferramenta MCP:

| Agente | Ferramenta MCP |
|---|---|
| Git Agent | `git_agent` |
| Agent Builder | `agent_builder` |
| Archmage Scribe | `archmage_scribe` |
| Bookmark Agent | `bookmark_agent` |
| Decision Architect | `decision_architect` |
| Project Ideas Agent | `project_ideas_agent` |
| Writing Assistant | `writing_assistant` |

O servidor é iniciado com:

```powershell
python -m agent_hub.mcp
```

O ponto de entrada atual configura interpretadores OpenAI para todos os agentes. Defina `OPENAI_API_KEY` antes de iniciar o servidor.

Exemplo de configuração de cliente MCP:

```json
{
  "mcpServers": {
    "agent-hub": {
      "command": "python",
      "args": ["-m", "agent_hub.mcp"],
      "env": {
        "OPENAI_API_KEY": "your-api-key"
      }
    }
  }
}
```

Ajuste `command` para apontar para o executável Python do ambiente virtual do projeto, quando necessário.

### Seleção do provedor por agente

Também é possível utilizar Anthropic ou combinar provedores diferentes entre os agentes. A seleção é feita individualmente no dicionário `interpreters`, definido no arquivo [`src/agent_hub/mcp/__main__.py`](https://github.com/cpzjunior/agent-hub/blob/main/src/agent_hub/mcp/__main__.py).

Para utilizar Anthropic em um agente, importe `AnthropicInterpreter` e substitua a implementação correspondente:

```python
from agent_hub.integrations.langchain.anthropic import AnthropicInterpreter
from agent_hub.integrations.langchain.openai import OpenAIInterpreter

interpreters = {
    "git-agent": OpenAIInterpreter(),
    "agent-builder": AnthropicInterpreter(),
    "archmage-scribe": OpenAIInterpreter(),
    # Demais agentes...
}
```

Defina `ANTHROPIC_API_KEY` no ambiente do servidor MCP para os agentes que utilizarem Anthropic. O modelo padrão é `claude-sonnet-4-5` e pode ser alterado pela variável `ANTHROPIC_MODEL`.

Dessa forma, cada agente pode utilizar OpenAI ou Anthropic independentemente dos demais. Caso ambos os provedores sejam utilizados, configure as respectivas chaves de API no ambiente do servidor.

## Validação

Execute as verificações automatizadas a partir da raiz do projeto:

```powershell
pytest -v
ruff check src tests
mypy src tests
```

Todas as verificações devem passar antes de realizar o commit das alterações.

## Fluxo de desenvolvimento

1. Ative o ambiente virtual.
2. Implemente as alterações.
3. Execute os testes, a verificação de lint e a verificação de tipos.
4. Faça o commit somente após a aprovação de todas as verificações.

## Contribuição

Contribuições são bem-vindas!

Se você deseja contribuir com este projeto:

1. Faça um fork do repositório.
2. Crie uma branch para suas alterações.
3. Faça as alterações e certifique-se de que o projeto seja compilado com sucesso.
4. Execute os testes existentes e adicione novos testes quando aplicável.
5. Envie um Pull Request descrevendo suas alterações.

Para relatar bugs, solicitar funcionalidades ou fazer perguntas, abra uma issue.

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a mesma licença deste projeto.

## Licença

Este projeto está licenciado sob a [Licença MIT](LICENSE).
