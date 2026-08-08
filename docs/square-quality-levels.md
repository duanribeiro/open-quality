# Níveis de qualidade SQuaRE

Todo recurso `QualityRequirement` deve informar `qualityLevel`. A classificação segue
os níveis de avaliação da qualidade usados pelo modelo SQuaRE e deixa explícito
em qual contexto cada requisito será verificado.

| Valor | Contexto de avaliação | Exemplos de evidência |
|---|---|---|
| `internal` | Artefatos estáticos, sem executar o sistema. | PRD, BRD, desenho técnico, revisão de código, análise estática e relatório de vulnerabilidades. |
| `external` | Comportamento do sistema em execução, em ambiente controlado. | Relatório de testes automatizados, teste de integração, carga, latência e disponibilidade. |
| `in-use` | Resultado obtido por usuários reais no contexto operacional. | Métricas de sucesso da tarefa, satisfação, taxa de erro do usuário e acessibilidade observada. |

## Aplicação

Use `internal` quando a qualidade puder ser avaliada em requisitos, desenho,
código ou configuração. Use `external` quando a avaliação depender da execução
do sistema. Use `in-use` quando depender da experiência e do resultado do
usuário em produção.

```yaml
kind: QualityRequirement
metadata:
  id: checkout-task-success
  name: Checkout task success
spec:
  category: usability
  statement: Customers must complete checkout without assistance.
  priority: high
  qualityLevel: in-use
```

O nível de qualidade não substitui `category`, métricas, documentação ou
relatórios. Ele define o contexto de avaliação; os demais campos definem a
característica, a meta e as evidências necessárias para demonstrá-la.
