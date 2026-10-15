import unittest
from pathlib import Path


SOURCE = Path(__file__).with_name("main.py").read_text(encoding="utf-8")


class PipelinePromptTests(unittest.TestCase):
    def test_interview_and_analysis_prompts_do_not_impose_a_domain(self):
        self.assertNotIn("reservar, cancelar, cadastrar salas", SOURCE)
        self.assertNotIn("roubo/sumiço de chaves", SOURCE)
        self.assertNotIn("alunos formados/inativos", SOURCE)

    def test_requirements_task_requires_implementable_acceptance_criteria(self):
        self.assertIn("Critérios de aceitação", SOURCE)
        self.assertIn("cenários no formato Dado/Quando/Então", SOURCE)

    def test_requirements_writer_uses_quality_and_atomicity_principles(self):
        self.assertIn("Especificador Sênior de Requisitos de Software", SOURCE)
        self.assertIn("necessidades e restrições, não soluções de implementação", SOURCE)
        self.assertIn("uma única obrigação verificável", SOURCE)
        self.assertIn("fonte, estímulo, ambiente, artefato, resposta e medida", SOURCE)
        self.assertIn("Não imponha tecnologia, arquitetura ou produto", SOURCE)
        self.assertIn("Tabela de controle de qualidade", SOURCE)

    def test_requirements_writer_preserves_the_existing_markdown_template(self):
        self.assertIn("### 1. Requisitos Funcionais (RF)", SOURCE)
        self.assertIn("- [ID] | [Especificação] | [Origem: Stakeholder X / Chapéu Y]", SOURCE)
        self.assertIn("### 2. Requisitos Não Funcionais (RNF)", SOURCE)
        self.assertIn("- [ID] | [Categoria] | [Especificação] | [Origem]", SOURCE)
        self.assertIn("### 3. Matriz de decomposição", SOURCE)

    def test_ra_agent_uses_architectural_significance_instead_of_technical_vocabulary(self):
        self.assertIn("Analista Sênior de Requisitos Arquiteturalmente Significativos", SOURCE)
        self.assertIn("impacto significativo e demonstrável sobre a arquitetura", SOURCE)
        self.assertIn("RF, atributos de qualidade e restrições podem ser arquiteturalmente significativos", SOURCE)
        self.assertIn("RA continua sendo uma necessidade ou restrição verificável, não uma decisão de solução", SOURCE)

    def test_ra_task_classifies_into_exactly_rf_rnf_and_ra_without_duplication(self):
        ra_task = SOURCE[SOURCE.index("t_ra = Task("):SOURCE.index("\nt5 = Task(")]
        self.assertIn("categoria primária exclusiva", ra_task)
        self.assertIn("Justificativa de significância arquitetural", ra_task)
        self.assertIn("alcance, impacto, dificuldade de mudança e risco", ra_task)
        self.assertIn("## 3. Requisitos Arquiteturais (RA)", ra_task)
        self.assertNotIn("## 4. Restrições do Sistema", ra_task)
        self.assertIn("Matriz de classificação", ra_task)

    def test_adr_task_records_inferred_decisions_as_explicit_assumptions(self):
        self.assertNotIn("tome uma decisão técnica sólida", SOURCE)
        self.assertIn("ASSUNÇÃO DE PROJETO", SOURCE)

    def test_adr_agent_decides_from_approved_rf_rnf_and_ra(self):
        self.assertIn("Arquiteto de Decisões Orientadas por Requisitos", SOURCE)
        self.assertIn("cada decisão arquitetural aos RF, RNF e RA aprovados", SOURCE)
        self.assertIn("ADRs registram decisões e seus trade-offs", SOURCE)
        self.assertIn("não são um inventário de tecnologias", SOURCE)

    def test_adr_task_compares_alternatives_and_proves_requirement_coverage(self):
        adr_task = SOURCE[SOURCE.index("t_adr = Task("):SOURCE.index("\nt_arquitetura = Task(")]
        self.assertIn("use o catálogo final aprovado como única autoridade", adr_task)
        self.assertIn("não crie um ADR por requisito", adr_task)
        self.assertIn("Matriz de cobertura da decisão", adr_task)
        self.assertIn("Critérios de decisão derivados dos requisitos", adr_task)
        self.assertIn("Plano de verificação da decisão", adr_task)
        self.assertIn("context=[t_catalogo_final]", adr_task)

    def test_architecture_task_does_not_force_components_without_requirements(self):
        self.assertNotIn("inclua OBRIGATORIAMENTE um API Gateway", SOURCE)
        self.assertIn("Somente inclua um componente", SOURCE)

    def test_architecture_agent_materializes_requirements_and_accepted_adrs(self):
        self.assertIn("Arquiteto Sênior de Software Orientado por Requisitos e Decisões", SOURCE)
        self.assertIn("materializar os RF, RNF e RA aprovados", SOURCE)
        self.assertIn("ADRs definem decisões e limites obrigatórios", SOURCE)
        self.assertIn("não contradiz, reabre ou substitui silenciosamente um ADR", SOURCE)

    def test_architecture_task_builds_traceable_views_from_final_catalog_and_adrs(self):
        architecture_task = SOURCE[SOURCE.index("t_arquitetura = Task("):SOURCE.index("\n\nMAX_RODADAS_DE_CORRECAO")]
        self.assertIn("fontes normativas exclusivas", architecture_task)
        self.assertIn("Visão lógica e decomposição", architecture_task)
        self.assertIn("Visão de execução e comunicação", architecture_task)
        self.assertIn("Visão de dados", architecture_task)
        self.assertIn("Visão de implantação e operação", architecture_task)
        self.assertIn("Matriz requisito → ADR → elemento arquitetural → verificação", architecture_task)
        self.assertIn("context=[t_catalogo_final, t_adr]", architecture_task)

    def test_context_task_keeps_pipeline_running_with_explicit_assumptions(self):
        self.assertIn("a pipeline deve continuar mesmo com lacunas", SOURCE)

    def test_interview_task_separates_facts_from_explicit_project_assumptions(self):
        self.assertIn("[FATO DO CONTEXTO]", SOURCE)
        self.assertIn("[ASSUNÇÃO DE PROJETO: AP-XX]", SOURCE)

    def test_elicitation_agents_apply_interview_and_six_hats_quality_practices(self):
        self.assertIn("Analista Sênior de Elicitação por Entrevistas Semiestruturadas", SOURCE)
        self.assertIn("perguntas abertas, aprofundamento progressivo", SOURCE)
        self.assertIn("Facilitador Sênior de Elicitação e Análise pelos Seis Chapéus", SOURCE)
        self.assertIn("Branco, Vermelho, Preto, Amarelo, Verde e Azul", SOURCE)

    def test_elicitation_tasks_produce_traceable_coverage_until_saturation(self):
        self.assertIn("até atingir saturação de informação", SOURCE)
        self.assertIn("não use uma quantidade fixa de perguntas", SOURCE)
        self.assertIn("ID único no formato ENT-[STAKEHOLDER]-[NN]", SOURCE)
        self.assertIn("Matriz de cobertura da entrevista", SOURCE)
        self.assertIn("Matriz de síntese dos seis chapéus", SOURCE)
        self.assertIn("não transforme hipótese criativa em fato", SOURCE)
        self.assertNotIn("Gere exatamente 5 perguntas", SOURCE)

    def test_requirements_only_accept_grounded_evidence(self):
        self.assertIn("Evidência:", SOURCE)
        self.assertIn("context=[t1, t2, t3]", SOURCE)

    def test_validation_and_correction_resolve_gaps_as_versioned_assumptions(self):
        self.assertIn("DECISÃO INFERIDA", SOURCE)
        self.assertIn("Nenhuma correção necessária", SOURCE)
        self.assertIn("context=[t_reverif, t6]", SOURCE)

    def test_validation_loop_applies_exactly_one_semantic_correction_without_a_judge(self):
        self.assertIn("def executar_ciclo_semantico", SOURCE)
        self.assertNotIn("DECISAO_DO_JUIZ_SEMANTICO", SOURCE)
        self.assertNotIn("juiz_semantico", SOURCE)
        self.assertNotIn("for rodada in range(1, MAX_RODADAS_DE_CORRECAO + 1)", SOURCE)
        self.assertIn("MAX_RODADAS_DE_CORRECAO = 1", SOURCE)

    def test_formal_verification_is_completed_before_validation_starts(self):
        self.assertIn("def executar_ciclo_formal", SOURCE)
        self.assertIn("catalogo_formal, relatorio_formal", SOURCE)
        self.assertIn("catalogo_semantico, relatorio_semantico", SOURCE)

    def test_task_contexts_follow_the_artifact_authority_chain(self):
        self.assertIn("context=[t1, t2]", SOURCE)
        self.assertIn("context=[t_ra, t5]", SOURCE)
        self.assertIn("context=[t_ra, t5, t_correcao_verificacao]", SOURCE)
        self.assertIn("context=[t1, t2, t3, t_reverif]", SOURCE)
        self.assertIn("context=[t_reverif, t6]", SOURCE)
        self.assertIn("context=[t1, t2, t3, t6, t_correcao]", SOURCE)

    def test_post_classification_catalog_uses_only_rf_rnf_and_ra(self):
        verification_chain = SOURCE[SOURCE.index("t5 = Task("):SOURCE.index("\nt_adr = Task(")]
        self.assertNotIn("## 4. Restrições do Sistema", verification_chain)
        self.assertNotIn("RF, RNF, RA e Restrições", verification_chain)
        self.assertNotIn("RF, RNF, RA e restrições", verification_chain)

    def test_verification_validation_and_correction_agents_fix_detected_problems(self):
        self.assertIn("Auditor e Revisor Sênior de Qualidade de Requisitos", SOURCE)
        self.assertIn("Validador Sênior de Requisitos Orientado a Stakeholders", SOURCE)
        self.assertIn("Especialista Sênior em Correção e Consolidação de Requisitos", SOURCE)
        self.assertIn("não encerra o trabalho no diagnóstico", SOURCE)

    def test_verification_and_validation_require_materialized_corrections(self):
        self.assertEqual(2, SOURCE.count("Todo problema identificado deve incluir diagnóstico, correção textual"))
        self.assertIn("Catálogo formal corrigido integral", SOURCE)
        self.assertIn("Catálogo semanticamente corrigido integral", SOURCE)
        self.assertIn("Não aceite como correção expressões como", SOURCE)
        self.assertNotIn("Liste cada erro encontrado, mas não reescreva", SOURCE)

    def test_pipeline_publishes_the_final_catalog_only_in_the_run_artifacts(self):
        self.assertIn('salvar_artefato(diretorio_execucao, "10-catalogo-final.md", catalogo_final)', SOURCE)
        self.assertNotIn('with open("requisitos.txt", "w", encoding="utf-8")', SOURCE)
        self.assertNotIn('with open("elicitacao_resultados.txt", "w", encoding="utf-8")', SOURCE)
        self.assertNotIn('with open("validacao.txt", "w", encoding="utf-8")', SOURCE)
        self.assertNotIn('with open("adr.txt", "w", encoding="utf-8")', SOURCE)
        self.assertNotIn('with open("arquitetura.md", "w", encoding="utf-8")', SOURCE)

    def test_requirements_artifact_contains_only_the_final_rf_rnf_and_ra_catalog(self):
        self.assertIn("catalogo_final = catalogo_semantico", SOURCE)
        self.assertIn('salvar_artefato(diretorio_execucao, "10-catalogo-final.md", catalogo_final)', SOURCE)
        self.assertIn("## 1. Requisitos Funcionais (RF)", SOURCE)
        self.assertIn("## 2. Requisitos Não Funcionais (RNF)", SOURCE)
        self.assertIn("## 3. Requisitos Arquiteturais (RA)", SOURCE)
        self.assertNotIn("def remover_metadados_nao_requisitos", SOURCE)

    def test_requirement_generation_decomposes_stakeholder_needs_without_a_fixed_count(self):
        self.assertIn("Não agrupe ações, regras, transições, permissões", SOURCE)
        self.assertIn("cada necessidade possuir cobertura completa", SOURCE)
        self.assertIn("cálculo de valor", SOURCE)
        self.assertIn("visualização pelo cliente dos próprios pedidos", SOURCE)

    def test_correction_materializes_every_validated_gap_as_atomic_requirements(self):
        self.assertIn("Não considere uma lacuna resolvida por uma AP isolada", SOURCE)
        self.assertIn("catálogo consolidado integral", SOURCE)
        self.assertIn("Sem os requisitos textualmente consolidados, a revalidação deve ser NÃO aprovada", SOURCE)
        self.assertIn("Catálogo formal corrigido integral", SOURCE)

    def test_correction_requires_the_atomic_catalog_before_supporting_reports(self):
        self.assertIn("A primeira seção da sua resposta DEVE ser '## Catálogo Consolidado'", SOURCE)
        self.assertIn("É proibido responder apenas com APs", SOURCE)

    def test_final_catalog_is_not_filtered_by_approval_status(self):
        self.assertNotIn("inclua somente requisitos marcados individualmente como resolvidos", SOURCE)
        self.assertNotIn('if "VALIDAÇÃO APROVADA: SIM" in str(t_revalidacao.output)', SOURCE)
        self.assertIn("catalogo_final = catalogo_semantico", SOURCE)

    def test_both_correction_stages_rewrite_invalid_requirements_before_deleting(self):
        self.assertEqual(2, SOURCE.count("Priorize reescrever, reajustar, decompor ou reclassificar"))
        self.assertEqual(2, SOURCE.count("A exclusão é o último recurso"))
        self.assertEqual(2, SOURCE.count("preserve a necessidade original do stakeholder"))

    def test_formal_and_semantic_corrections_do_not_reject_artifacts(self):
        self.assertNotIn("Juiz Independente de Conformidade Formal", SOURCE)
        self.assertNotIn("Juiz Independente de Validação Semântica", SOURCE)
        self.assertNotIn("REQUISITOS_APROVADOS_INDIVIDUALMENTE", SOURCE)
        self.assertIn("MAX_RODADAS_DE_CORRECAO = 1", SOURCE)
        self.assertIn("def executar_ciclo_formal", SOURCE)
        self.assertIn("def executar_ciclo_semantico", SOURCE)

    def test_final_catalog_keeps_the_fully_corrected_catalog_without_filtering_ids(self):
        self.assertIn("catalogo_final = catalogo_semantico", SOURCE)
        self.assertNotIn("publique somente IDs explicitamente presentes", SOURCE)

    def test_requirement_coverage_checklist_requires_the_complete_printing_3d_flow(self):
        self.assertIn("CHECKLIST DE COBERTURA OBRIGATÓRIA", SOURCE)
        self.assertIn("encaminhar pedido aprovado à produção", SOURCE)
        self.assertIn("calcular o valor da peça pela fórmula de negócio", SOURCE)
        self.assertIn("consultar histórico de pedidos, produtos, clientes, valores e STL", SOURCE)

    def test_correctors_remove_unsupported_assumptions_and_non_atomic_requirements(self):
        self.assertIn("Uma AP não confirma uma necessidade", SOURCE)
        self.assertIn("Todo RF, RNF e RA deve ter uma única obrigação testável", SOURCE)
        self.assertIn("mantenha-a como pendência/assunção fora do catálogo publicado", SOURCE)

    def test_final_artifacts_are_rendered_from_the_corrected_catalog(self):
        self.assertIn("crew_elicitacao", SOURCE)
        self.assertIn("catalogo_final = catalogo_semantico", SOURCE)
        self.assertIn("## 1. Requisitos Funcionais (RF)", SOURCE)
        self.assertIn("## 2. Requisitos Não Funcionais (RNF)", SOURCE)
        self.assertIn("## 3. Requisitos Arquiteturais (RA)", SOURCE)
        self.assertIn('salvar_artefato(diretorio_execucao, "10-catalogo-final.md", catalogo_final)', SOURCE)
        self.assertIn('salvar_artefato(diretorio_execucao, "11-adrs.md", adr_final)', SOURCE)
        self.assertIn('salvar_artefato(diretorio_execucao, "12-arquitetura.md", arquitetura_final)', SOURCE)

    def test_every_pipeline_stage_is_persisted_as_a_run_artifact(self):
        self.assertIn('DIRETORIO_ARTEFATOS = "artefatos"', SOURCE)
        self.assertIn("def salvar_artefato", SOURCE)
        for artifact in (
            "01-contexto-confirmado.md",
            "02-entrevistas.md",
            "03-seis-chapeus.md",
            "04-requisitos-iniciais.md",
            "05-classificacao-ra.md",
            "06-verificacao-formal.md",
            "07-catalogo-pos-verificacao.md",
            "08-validacao-semantica.md",
            "09-catalogo-pos-validacao.md",
            "10-catalogo-final.md",
            "11-adrs.md",
            "12-arquitetura.md",
        ):
            self.assertIn(artifact, SOURCE)

    def test_requirement_prompt_prevents_small_catalogs_by_enforcing_source_coverage(self):
        self.assertIn("NUNCA use uma quantidade-alvo arbitrária", SOURCE)
        self.assertIn("Cada comportamento independente aplicável deve originar ao menos um requisito", SOURCE)
        self.assertIn("Autochecagem de completude obrigatória", SOURCE)

    def test_critical_agents_use_low_temperature_for_repeatable_artifacts(self):
        self.assertIn("temperature=0.2", SOURCE)


if __name__ == "__main__":
    unittest.main()
