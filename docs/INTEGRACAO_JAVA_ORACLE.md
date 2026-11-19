# Integração prevista: Java → Flask; Java → Oracle

Este projeto implementa a API Flask e os modelos. **Não afirma que Java, Oracle e front-end
já foram integrados.** A aplicação Python procedural recebida mantém seu JSON independente.
Não é necessário modificá-la para cumprir sua opção de persistência em arquivo.

## Responsabilidades

1. Java recebe a residência selecionada pelo site.
2. Java consulta sete dias até uma data de referência no Oracle, vinculados àquela residência.
3. Confere ordem, ausência de lacunas e unidade diária. Sem histórico suficiente, explica a pendência.
4. Monta o JSON de `docs/API.md` e faz POST para Flask, com timeout de até 15 s.
5. Valida status e resposta. Sem resposta válida, não grava resultado inventado.
6. Usa as sequences Oracle para novos IDs e persiste apenas saídas reais com origem `MODELO`.
7. Retorna resultado, data, avisos e versão ao front-end.

Consulta sugerida (parâmetros vinculados, não concatenação):

```sql
SELECT dt_consumo, vl_consumo_kwh
FROM tb_consumo_diario
WHERE cd_residencia = :residencia
  AND dt_consumo BETWEEN :referencia - 6 AND :referencia
ORDER BY dt_consumo
```

Cada data corresponde a um `DATE` sem horário. Java converte para ISO no JSON.
O código Flask não recebe usuário/senha Oracle e não sabe qual `cd_residencia` foi escolhido;
o Java é responsável por associar corretamente a resposta à residência solicitada.

## Mapeamento das saídas para o banco existente

| Oracle | Origem do valor |
|---|---|
| `tb_previsao_consumo.cd_previsao` | `sq_tb_previsao_consumo.NEXTVAL` |
| `cd_residencia` | Residência validada pelo Java |
| `dt_referencia` | `data_referencia` da resposta |
| `dt_alvo` | `data_alvo`, obrigatoriamente referência + 1 |
| `vl_previsto_kwh` | `consumo_previsto_kwh` |
| `ds_modelo` | `modelo` (máximo 80 caracteres) |
| `dt_geracao` | `SYSDATE` na persistência |
| `ds_origem` | `MODELO` |
| `tb_analise_padrao.cd_analise` | `sq_tb_analise_padrao.NEXTVAL` |
| `dt_inicio`, `dt_fim` | `data_inicio`, `data_fim` |
| `cd_grupo` | `grupo` |
| `ds_interpretacao` | `nome` + `interpretacao`, até 500 caracteres |
| `ds_modelo`, `ds_origem` | Modelo retornado e `MODELO` |

As demais colunas de análise usam a residência validada. Respeitar FK, NOT NULL e CHECKs;
usar commit/rollback do lado Java. Não reaproveitar IDs do JSON local como novos IDs Oracle.
Não executar de novo CREATE TABLE nem apagar os dados da entrega de banco para integrar.

Os dez exemplos do banco com `SIMULADO`/`FIXTURE_NAO_TREINADO` permanecem exemplos;
não devem ser renomeados para `MODELO`. Novas inferências ficam em novos registros.
Registrar e exibir os avisos da API; o esquema atual não tem coluna específica para todos eles.

## Validação necessária na máquina do grupo

Executar Java com acesso ao Oracle, apontar a URL do Flask e comprovar uma consulta, chamada
HTTP e persistência com retorno lido do banco. Essa etapa não foi executada aqui porque não
foi fornecido back-end Java nem conexão Oracle autorizada para este módulo.
Se Java estiver em outro computador, `127.0.0.1` não alcançará a máquina do Flask: combinar
uma implantação de rede apropriada antes da demonstração integrada.
