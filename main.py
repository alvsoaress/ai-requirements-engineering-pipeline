import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
import os

load_dotenv()

os.environ["CREWAI_TRACING_ENABLED"] = "false"

gemini = LLM(
    model="gemini/gemini-3.6-flash", 
    api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.2
)

chatgpt = LLM(
    model="gpt-4o-mini",
    api_key=os.getenv("CHATGPT_API_KEY"),
    temperature=0.2
)

DIRETORIO_ARTEFATOS = "artefatos"


def criar_diretorio_execucao():
    """Cria um pacote imutável de evidências para uma execução da pipeline."""
    identificador = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    diretorio = Path(DIRETORIO_ARTEFATOS) / identificador
    diretorio.mkdir(parents=True, exist_ok=False)
    return diretorio


def salvar_artefato(diretorio, nome, conteudo):
    """Persiste a saída bruta de cada etapa sem alterar sua rastreabilidade."""
    caminho = diretorio / nome
    caminho.write_text(str(conteudo), encoding="utf-8")
    print(f"Artefato gerado: {caminho}")
    return caminho


def task_delay_callback(output):
    print("Pausa de segurança")
    time.sleep(20)


contextualizador = Agent(
    role="Engenheiro de Requisitos Sênior",
    goal="Absorver, delimitar e confirmar o contexto do projeto antes da elicitação.",
    backstory=(
        "Você é especialista em entendimento de domínio. Trabalha somente com fatos presentes no contexto recebido. "
        "Distingue fatos, inferências e termos fora de escopo. Quando faltar detalhe necessário para implementar, "
        "formula uma ASSUNÇÃO DE PROJETO explícita, plausível e rastreável ao domínio; nunca importa exemplos de outro domínio."
    ),
    llm=chatgpt,
    verbose=True
)

entrevistador = Agent(
    role="Analista Sênior de Elicitação por Entrevistas Semiestruturadas",
    goal=(
        "Elicitar objetivos, necessidades, regras de negócio, dados, restrições, atributos de qualidade, exceções, prioridades e critérios de sucesso "
        "de cada stakeholder, produzindo evidências rastreáveis e suficientes para a especificação posterior dos requisitos."
    ),
    backstory=(
        "Você é especialista em Engenharia de Requisitos e entrevistas semiestruturadas. Conduz perguntas abertas, aprofundamento progressivo, "
        "sondagem de exemplos concretos, perguntas de confirmação e síntese final com o entrevistado. Evita perguntas compostas, indutivas, "
        "hipotéticas demais ou carregadas de solução. Investiga primeiro objetivos e trabalho atual; depois fluxos, exceções, regras, dados, "
        "qualidade e critérios de aceitação. Cada afirmação recebe origem e classificação. Você nunca apresenta uma resposta simulada como fala "
        "real do stakeholder: o que não estiver nas fontes é registrado como questão em aberto ou [ASSUNÇÃO DE PROJETO: AP-XX], com justificativa e risco."
    ),
    llm=chatgpt,
    verbose=True
)

chapeus = Agent(
    role="Facilitador Sênior de Elicitação e Análise pelos Seis Chapéus",
    goal=(
        "Ampliar e confrontar os achados das entrevistas pelas perspectivas Branco, Vermelho, Preto, Amarelo, Verde e Azul, "
        "identificando cobertura, riscos, valor, alternativas, conflitos e decisões sem confundir criatividade com evidência."
    ),
    backstory=(
        "Você domina facilitação de grupos, pensamento paralelo e análise de requisitos. Mantém as seis perspectivas separadas para evitar debate "
        "desordenado: Branco examina evidências e lacunas; Vermelho registra percepções e preocupações atribuídas; Preto analisa riscos e falhas; "
        "Amarelo explicita benefícios e valor; Verde propõe alternativas e hipóteses; Azul sintetiza, prioriza e controla a cobertura. "
        "Toda conclusão referencia IDs das entrevistas. Ideias criativas permanecem candidatas ou assunções até possuírem evidência; você não as promove a fatos."
    ),
    llm=chatgpt,
    verbose=True
)

documentador = Agent(
    role="Especificador Sênior de Requisitos de Software",
    goal=(
        "Transformar os achados rastreáveis da elicitação em um catálogo completo de RF e RNF corretos, necessários, atômicos, "
        "não ambíguos, consistentes, viáveis, verificáveis e rastreáveis, preservando o template vigente e cobrindo cada comportamento independente da fonte."
    ),
    backstory=(
        "Você é especialista na ISO/IEC/IEEE 29148, em escrita normativa, padrões EARS, cenários de qualidade e critérios BDD. "
        "Especifica necessidades e restrições, não soluções de implementação. Cada RF contém uma única obrigação verificável, com ator, "
        "condição ou gatilho, resposta observável e origem. Cada RNF expressa um cenário mensurável de qualidade. Você preserva o significado "
        "das fontes, usa vocabulário consistente, evita termos vagos e não transforma hipótese, preferência ou decisão arquitetural em fato."
        " A quantidade de requisitos decorre da decomposição e da matriz de cobertura: nunca reduz cobertura para produzir uma lista curta."
    ),
    llm=chatgpt,
    verbose=True
)

arquiteto_requisitos = Agent(
    role="Analista Sênior de Requisitos Arquiteturalmente Significativos",
    goal=(
        "Classificar cada requisito em RF, RNF ou RA por sua obrigação primária e identificar, com evidência, somente os requisitos com "
        "impacto significativo e demonstrável sobre a arquitetura, sem confundir necessidade com decisão de projeto."
    ),
    backstory=(
        "Você combina Engenharia de Requisitos, análise de atributos de qualidade e arquitetura orientada por requisitos arquiteturalmente "
        "significativos (ASR). Sabe que RF, atributos de qualidade e restrições podem ser arquiteturalmente significativos, mas significância "
        "arquitetural é uma propriedade que precisa ser justificada, não uma licença para chamar todo requisito técnico de RA. "
        "Um RA continua sendo uma necessidade ou restrição verificável, não uma decisão de solução: padrões, componentes, frameworks, bancos, "
        "protocolos e topologias pertencem a ADRs, salvo quando uma fonte autorizada os impõe como restrição. Você avalia alcance transversal, "
        "efeito sobre estruturas e interfaces, dificuldade ou custo de mudança, risco, trade-offs e impacto nos objetivos de negócio. "
        "Preserva significado, evidência e rastreabilidade, evita duplicação entre categorias e explicita casos limítrofes."
    ),
    llm=chatgpt,
    verbose=True
)

verificador = Agent(
    role="Auditor e Revisor Sênior de Qualidade de Requisitos",
    goal=(
        "Verificar cada RF, RNF e RA contra critérios objetivos de qualidade e fornecer uma correção textual completa, "
        "rastreável e aplicável para todo defeito encontrado, registrando um veredito por requisito e por evidência de origem."
    ),
    backstory=(
        "Você domina ISO/IEC/IEEE 29148, atomicidade semântica, EARS, cenários de qualidade, rastreabilidade e análise de consistência. "
        "Você não encerra o trabalho no diagnóstico: demonstra o defeito, preserva a intenção e a origem, propõe o texto corrigido e define como comprovar a correção. "
        "Não aceita como solução excluir conteúdo útil, mover detalhes para AP/ADR/SDD ou prometer definição futura. Quando a correção exigir decomposição, "
        "mantém o ID original no primeiro requisito e cria IDs rastreáveis para as demais obrigações."
    ),
    llm=chatgpt,
    verbose=True
)

validador = Agent(
    role="Validador Sênior de Requisitos Orientado a Stakeholders",
    goal=(
        "Comparar o catálogo com objetivos, necessidades, fluxos, regras, riscos e critérios de sucesso dos stakeholders e transformar "
        "cada lacuna, excesso ou conflito em uma correção materializável e rastreável, sem perder necessidades que ainda não possuem requisito."
    ),
    backstory=(
        "Você é especialista em validação de requisitos, cobertura de necessidades e adequação ao uso. Trabalha requisito por requisito e necessidade por necessidade. "
        "Você não encerra o trabalho no diagnóstico: para toda cobertura parcial/ausente, regra incompatível, requisito sem valor ou solução prematura, fornece uma redação corrigida "
        "ou novos requisitos atômicos com origem. Como os stakeholders são simulados, distingue FATO RASTREÁVEL, DECLARAÇÃO SIMULADA e ASSUNÇÃO DE PROJETO; "
        "aprovação por simulação não equivale a aceite humano. Nunca considera uma nota de correção futura como problema resolvido."
    ),
    llm=gemini,
    verbose=True
)

corretor = Agent(
    role="Especialista Sênior em Correção e Consolidação de Requisitos",
    goal=(
        "Aplicar integralmente as correções prescritas pela verificação e pela validação, entregando um catálogo completo, coerente, "
        "atômico e rastreável em que a intenção aprovada permaneça materializada no próprio texto dos requisitos."
    ),
    backstory=(
        "Você reescreve, decompõe, consolida e reclassifica requisitos sem apagar necessidades legítimas. Toda decisão sem fonte explícita recebe uma "
        "ASSUNÇÃO DE PROJETO com justificativa e risco, mas a AP nunca substitui o requisito corrigido. Você confere o catálogo inteiro após cada alteração "
        "para evitar contradições e efeitos colaterais, e não declara uma correção aplicada se o texto antigo ou a lacuna ainda estiver presente."
    ),
    llm=chatgpt,
    verbose=True
)

criador_adr = Agent(
    role="Arquiteto de Decisões Orientadas por Requisitos",
    goal=(
        "Derivar, avaliar e registrar as decisões arquiteturais necessárias para satisfazer o catálogo final, vinculando "
        "cada decisão arquitetural aos RF, RNF e RA aprovados e tornando explícitos alternativas, trade-offs e verificações."
    ),
    backstory=(
        "Você é especialista em arquitetura orientada por requisitos, análise de trade-offs e documentação do ciclo de vida de decisões. "
        "Para você, ADRs registram decisões e seus trade-offs; não são um inventário de tecnologias, uma descrição genérica da arquitetura "
        "nem uma repetição dos requisitos. Você parte dos comportamentos dos RF, das medidas de qualidade dos RNF e dos drivers dos RA para "
        "identificar questões que realmente exigem escolha. Compara alternativas pelos mesmos critérios derivados dos requisitos, registra "
        "consequências positivas e negativas e mantém rastreabilidade muitos-para-muitos. Não inventa demanda para justificar uma tecnologia. "
        "Quando o catálogo não determina uma única resposta, escolhe a opção mais simples e reversível que satisfaça os requisitos, rotula a "
        "decisão como inferida e explicita assunção, risco, gatilho de revisão e evidência necessária para confirmá-la."
    ),
    llm=chatgpt,
    verbose=True
)

arquiteto_sistemas = Agent(
    role="Arquiteto Sênior de Software Orientado por Requisitos e Decisões",
    goal=(
        "Transformar o catálogo final e os ADRs vigentes em uma descrição arquitetural coerente, implementável e verificável, capaz de "
        "materializar os RF, RNF e RA aprovados com rastreabilidade até responsabilidades, interfaces, dados, execução e implantação."
    ),
    backstory=(
        "Você domina descrição de arquitetura por múltiplas visões, decomposição por responsabilidades, contratos de interface, modelagem de dados, "
        "cenários de qualidade e avaliação de trade-offs. Requisitos definem resultados e qualidades que a arquitetura precisa realizar; "
        "ADRs definem decisões e limites obrigatórios para a solução. Você não contradiz, reabre ou substitui silenciosamente um ADR: aplica decisões vigentes, "
        "identifica decisões propostas ou inferidas e registra conflito ou lacuna quando surgir necessidade de uma nova escolha. Cada elemento arquitetural "
        "deve existir por causa de pelo menos um requisito ou ADR, e cada requisito deve apontar para elementos e mecanismos que o atendem. Você prefere "
        "a menor arquitetura suficiente, define fronteiras coesas e evita componentes, camadas, integrações ou tecnologias ornamentais. Escreve para que "
        "equipes e agentes de SDD consigam derivar especificações e testes sem confundir decisão confirmada com hipótese."
    ),
    llm=chatgpt,
    verbose=True
)

CONTEXTO = """
Escopo:

O sistema deve apoiar o gerenciamento de uma empresa de impressão 3D personalizada, digitalizando a comunicação e o fluxo de produção de pedidos atualmente conduzidos por WhatsApp.

O escopo funcional inclui:

- Solicitação de impressão personalizada pelo cliente, com descrição da peça desejada, tamanho, características obrigatórias e anexos de imagens ou arquivos de referência.
- Análise da solicitação pela empresa, incluindo orçamento, prazo de entrega e possíveis alterações na proposta.
- Aprovação do cliente antes do encaminhamento do pedido à produção.
- Acompanhamento do ciclo de vida do pedido pelos estados:
  SOLICITAÇÃO RECEBIDA, EM ANÁLISE, AGUARDANDO APROVAÇÃO,
  EM PRODUÇÃO, EM IMPRESSÃO, FINALIZADO e ENTREGUE.
- Visualização dos dados do produto e do status do pedido por cliente e empresa.
- Histórico de pedidos contendo produtos produzidos, clientes, valores cobrados e, para uso interno da empresa, arquivos STL associados.
- Cálculo do valor da peça a partir de uma fórmula previamente definida, apresentando o valor ao cliente.

Objetivo:

Melhorar a comunicação entre cliente e empresa, organizar o processo de criação e fabricação de peças personalizadas e oferecer rastreabilidade dos pedidos desde a solicitação até a entrega.

Stakeholders:

1. Cliente
- Solicita uma peça personalizada.
- Descreve a ideia, o tamanho e as características obrigatórias.
- Envia imagens ou arquivos de referência.
- Recebe orçamento, prazo e possíveis alterações propostas pela empresa.
- Aprova a proposta antes do início da produção.
- Acompanha os dados e o status do próprio pedido.

2. Empresa / equipe de atendimento e produção
- Visualiza e analisa solicitações recebidas.
- Informa orçamento, prazo de entrega e possíveis alterações técnicas.
- Encaminha pedidos aprovados à produção.
- Necessita acompanhar o andamento dos pedidos e consultar o histórico de fabricação, clientes, valores e arquivos STL.
- Espera que o sistema organize os dados e reduza a dependência da comunicação manual por WhatsApp.

Restrições e Premissas Tecnológicas:

- Não há tecnologias, linguagem, framework, banco de dados, arquitetura, mecanismo de autenticação ou infraestrutura definidos no contexto de origem.
- O sistema deve atender ao domínio de impressão 3D personalizada; não assumir regras de outros domínios, como reservas de salas, controle de chaves ou estudantes.
- Os pedidos podem envolver produtos como chaveiros, miniaturas, lembrancinhas e outras peças sob demanda.
- A fórmula de cálculo do valor é uma premissa de negócio, mas seus parâmetros, pesos e regras ainda não foram especificados.
- O fluxo possui sete estados de pedido explicitamente definidos, mas ainda precisam ser confirmados: responsáveis por cada transição, transições permitidas, possibilidade de cancelamento e efeitos como notificações.
- Permanecem pendentes: formatos e limites dos anexos, regras de acesso/autenticação, persistência dos arquivos STL, política de histórico, pagamentos, notificações e critérios de atualização “em tempo real”.

"""

t1 = Task(
    description=(
        f"Absorva e confirme o contexto do projeto abaixo. Liste somente fatos explícitos que guiarão a elicitação.\n\n{CONTEXTO}\n\n"
        "Produza: (1) objetivo e fronteira do sistema; (2) stakeholders e responsabilidades citados; "
        "(3) glossário de termos do domínio; (4) hipóteses e informações ausentes; (5) termos ou domínios que não possuem lastro. "
        "Não proponha tecnologias nesta etapa. Para cada detalhe ausente que será necessário nas próximas etapas, proponha uma "
        "ASSUNÇÃO DE PROJETO com ID (AP-01, ...), justificativa e risco; a pipeline deve continuar mesmo com lacunas."
    ),
    expected_output="Contexto confirmado com fronteira, stakeholders, glossário, fatos, lacunas e Assunções de Projeto versionadas.",
    agent=contextualizador
)

t2 = Task(
    description=(
        "Conduza uma entrevista semiestruturada para cada stakeholder identificado no contexto confirmado. Produza perguntas e respostas "
        "rastreáveis a partir das informações disponíveis; quando a fonte não contiver a resposta, registre 'NÃO INFORMADO' e formule separadamente "
        "uma [ASSUNÇÃO DE PROJETO: AP-XX] somente quando ela for necessária para a continuidade da pipeline.\n\n"
        "Procedimento obrigatório:\n"
        "1. Inicie por objetivos, responsabilidades, vocabulário, processo atual, eventos de início/fim, dores e resultados esperados do stakeholder.\n"
        "2. Aprofunde cada fluxo com caminho principal, alternativas, exceções, erros, estados, transições, dados de entrada/saída e evidência observável de conclusão.\n"
        "3. Investigue separadamente permissões por ator, regras de negócio, validações, frequência/volume, prioridades e dependências externas.\n"
        "4. Elicite atributos de qualidade por cenários concretos: estímulo, contexto, resposta e medida, sem impor tecnologia ou números não fornecidos.\n"
        "5. Formule uma pergunta por vez. Evite perguntas indutivas, respostas embutidas e termos vagos; peça exemplos e contraexemplos para esclarecer respostas abstratas.\n"
        "6. Atribua a cada pergunta e resposta um ID único no formato ENT-[STAKEHOLDER]-[NN]. Classifique a resposta como [FATO DO CONTEXTO], "
        "[DECLARAÇÃO SIMULADA] ou [ASSUNÇÃO DE PROJETO: AP-XX], informando fonte, confiança e impacto.\n"
        "7. Continue a entrevista até atingir saturação de informação: todos os tópicos aplicáveis estão cobertos e novas perguntas não revelam "
        "novas necessidades, regras, exceções ou dados relevantes; não use uma quantidade fixa de perguntas.\n"
        "8. Encerre com confirmação: resuma necessidades, conflitos, prioridades, termos do glossário e questões em aberto para cada stakeholder."
    ),
    expected_output=(
        "Documento de elicitação contendo, nesta ordem:\n"
        "1. Plano da entrevista: stakeholder | objetivo | tópicos aplicáveis.\n"
        "2. Entrevistas por stakeholder: ID | pergunta atômica | resposta | classificação | fonte/confiança.\n"
        "3. Catálogo de achados: ID do achado | tipo (objetivo, necessidade, regra, dado, restrição, qualidade, exceção) | descrição | IDs de origem.\n"
        "4. Fluxos elicitados com caminho principal, alternativas, exceções, estados, entradas, saídas e responsáveis.\n"
        "5. Glossário do domínio com termo, definição e origem.\n"
        "6. Questões em aberto e Assunções de Projeto: ID | lacuna | decisão provisória | justificativa | risco | stakeholder para confirmação.\n"
        "7. Matriz de cobertura da entrevista: stakeholder/tópico | IDs das evidências | coberto/parcial/não informado.\n"
        "8. Declaração de saturação, indicando o que foi coberto e qualquer lacuna residual."
    ),
    agent=entrevistador,
    context=[t1]
)

t3 = Task(
    description=(
        "Conduza uma sessão estruturada dos Seis Chapéus sobre os achados das entrevistas. Analise cada objetivo, fluxo, regra, atributo de qualidade, "
        "questão em aberto e assunção relevante até atingir saturação de informação, sempre referenciando os IDs ENT e os IDs dos achados.\n\n"
        "Procedimento obrigatório:\n"
        "1. Branco — Evidências: consolide fatos, fontes, dados conhecidos, contradições e informações ausentes; não faça inferências nesta rodada.\n"
        "2. Vermelho — Percepções: registre expectativas, frustrações, receios e preferências somente quando atribuíveis a um stakeholder; quando simuladas, rotule-as como hipótese.\n"
        "3. Preto — Riscos: identifique falhas, abuso, exceções, impactos operacionais, segurança, privacidade, conformidade e condições que inviabilizam o fluxo.\n"
        "4. Amarelo — Valor: explicite benefícios esperados, critérios de sucesso, oportunidades e quem recebe cada valor, vinculando-os aos objetivos elicitados.\n"
        "5. Verde — Alternativas: proponha opções de regra ou processo para lacunas e conflitos sem escolher tecnologia. Rotule cada opção como CANDIDATA e não transforme hipótese criativa em fato.\n"
        "6. Azul — Síntese: consolide acordos, conflitos, decisões sustentadas, alternativas ainda abertas, prioridades e cobertura. Uma decisão sem evidência deve virar "
        "[ASSUNÇÃO DE PROJETO: AP-XX] com justificativa, impacto, risco e necessidade de confirmação.\n"
        "7. Não invente fala de stakeholder, tecnologia, arquitetura ou restrição numérica. Não considere AP, preferência ou alternativa como requisito aprovado.\n"
        "8. Continue as rodadas enquanto surgirem novos riscos, alternativas ou conflitos relevantes; encerre quando a matriz de cobertura não apresentar perspectiva aplicável sem análise."
    ),
    expected_output=(
        "Documento de análise contendo, nesta ordem:\n"
        "1. Matriz de síntese dos seis chapéus: ID | item analisado | chapéu | achado | classificação | IDs ENT/achados de origem.\n"
        "2. Catálogo de riscos: ID | cenário/causa | consequência | stakeholder afetado | prevenção/mitigação candidata | origem.\n"
        "3. Catálogo de valor: objetivo | benefício | stakeholder beneficiado | evidência | indicador de sucesso informado ou pendente.\n"
        "4. Matriz de conflitos e alternativas: ID | posições/evidências | opções | decisão sustentada ou AP | justificativa | risco residual.\n"
        "5. Necessidades candidatas consolidadas: ID | descrição atômica | tipo | prioridade MoSCoW quando sustentada | fontes | status fato/AP/aberta.\n"
        "6. Questões em aberto e Assunções de Projeto versionadas, sem transformá-las em fatos.\n"
        "7. Matriz de cobertura: objetivo/fluxo | Branco | Vermelho | Preto | Amarelo | Verde | Azul | lacuna residual.\n"
        "8. Declaração de saturação e pacote rastreável de entrada para a especificação de requisitos."
    ),
    agent=chapeus,
    context=[t1, t2]
)

t4 = Task(
    description=(
        "Transforme o contexto confirmado, o catálogo de achados das entrevistas e a síntese dos Seis Chapéus em requisitos funcionais e "
        "não funcionais. Use somente itens com IDs de origem presentes nas Tasks 1, 2 e 3; preserve o template Markdown definido no expected_output.\n\n"
        "Procedimento obrigatório de escrita:\n"
        "1. Selecione necessidades, regras, restrições e atributos de qualidade sustentados por [FATO DO CONTEXTO], [DECLARAÇÃO SIMULADA] ou "
        "[ASSUNÇÃO DE PROJETO: AP-XX]. Não use ideia CANDIDATA, questão aberta ou preferência como requisito aprovado sem uma AP explícita.\n"
        "2. Classifique como RF somente comportamento observável do sistema ou interação necessária de um ator. Escreva cada RF usando uma forma EARS adequada "
        "e a estrutura [Ator/Sistema] + DEVE + [uma ação] + [objeto/resultado] + [condição ou gatilho].\n"
        "3. Garanta atomicidade semântica: cada RF deve conter uma única obrigação verificável. Não agrupe ações, regras, transições, permissões, "
        "consultas, validações, registros, notificações ou exceções independentes. Não una, no mesmo ID, ações independentes de criação, consulta, "
        "alteração, exclusão, cálculo, validação, autorização, transição, notificação, armazenamento ou auditoria. Se puderem ser implementadas ou testadas separadamente, decomponha.\n"
        "4. Explicite regras de negócio e exceções como condições do RF correspondente ou como RF separado quando produzirem comportamento testável distinto. "
        "Não esconda regras necessárias apenas nos critérios de aceitação.\n"
        "5. Para cada RF, produza critérios de aceitação como cenários no formato Dado/Quando/Então: ao menos um cenário de sucesso e um cenário de exceção aplicável. "
        "O critério deve observar o mesmo e único comportamento do requisito.\n"
        "6. Classifique como RNF somente atributo de qualidade ou restrição mensurável. Estruture-o como cenário contendo fonte, estímulo, ambiente, artefato, resposta e medida; "
        "o texto publicado deve declarar condição, resposta e métrica verificável. Se a métrica não existir nas fontes, registre AP identificada em vez de inventá-la como fato.\n"
        "7. Não imponha tecnologia, arquitetura ou produto em RF/RNF, salvo quando a fonte os declarar como restrição obrigatória. Decisões de solução pertencem à etapa arquitetural.\n"
        "8. Use termos do glossário de forma uniforme. Evite pronomes sem referente e expressões como 'adequado', 'fácil', 'rápido', 'intuitivo', 'quando necessário', "
        "'conforme definido', 'entre outros' ou 'etc.' sem critério observável.\n"
        "9. Rastreabilidade: cada requisito deve indicar IDs exatos das evidências ENT/achados/AP e sua classificação. Uma AP justifica a origem, mas não substitui o texto completo do requisito.\n"
        "10. Cobertura: percorra cada necessidade e cada comportamento da matriz de elicitação. Não use quantidade fixa; continue até que todo item aplicável esteja coberto ou identificado como lacuna.\n"
        "11. NUNCA use uma quantidade-alvo arbitrária para encerrar o catálogo. Cada comportamento independente aplicável deve originar ao menos um requisito "
        "ou uma lacuna explicitamente justificada na matriz; não compacte comportamentos apenas para reduzir o total de requisitos.\n"
        "12. Autochecagem de completude obrigatória: antes de responder, compare cada linha da matriz de elicitação e dos Seis Chapéus com os IDs gerados. "
        "Se uma linha possuir cobertura parcial, decomponha os comportamentos restantes em requisitos antes de finalizar.\n"
        "13. CHECKLIST DE COBERTURA OBRIGATÓRIA para este contexto: gere requisitos atômicos distintos, quando aplicáveis, para (a) registrar solicitação com descrição, "
        "tamanho e características; (b) anexar imagens/arquivos de referência; (c) consultar solicitações recebidas; (d) analisar solicitação; (e) registrar orçamento; "
        "(f) registrar prazo de entrega; (g) registrar alterações técnicas propostas; (h) disponibilizar proposta ao cliente; (i) aprovar proposta; "
        "(j) encaminhar pedido aprovado à produção; (k) consultar dados do produto pelo cliente; (l) consultar status pelo cliente; "
        "(m) acompanhar o progresso pela empresa; (n) registrar e exibir os sete estados explicitamente fornecidos, sem inventar transições; "
        "(o) consultar histórico de pedidos, produtos, clientes, valores e STL internamente; (p) calcular o valor da peça pela fórmula de negócio e apresentá-lo ao cliente. "
        "Cada linha deve indicar o ID de requisito que a cobre; uma linha sem ID é falha de cobertura e exige novo requisito.\n"
        "14. Antes de responder, execute internamente uma Tabela de controle de qualidade por requisito: necessário, correto, atômico, não ambíguo, consistente, viável, verificável e rastreável. "
        "Reescreva os itens reprovados e não inclua essa tabela na saída, para preservar o template."
    ),
    expected_output=(
        "Um catálogo estruturado exatamente no template Markdown abaixo, sem introdução, conclusões ou seções adicionais:\n"
        "### 1. Requisitos Funcionais (RF)\n"
        "- [ID] | [Especificação] | [Origem: Stakeholder X / Chapéu Y]\n"
        "  - Evidência: [IDs ENT/achado/AP e classificação FATO DO CONTEXTO, DECLARAÇÃO SIMULADA ou ASSUNÇÃO DE PROJETO]\n"
        "  - Critérios de aceitação — sucesso: Dado ..., Quando ..., Então ...\n"
        "  - Critérios de aceitação — exceção aplicável: Dado ..., Quando ..., Então ...\n\n"
        "### 2. Requisitos Não Funcionais (RNF)\n"
        "- [ID] | [Categoria] | [Especificação] | [Origem]\n"
        "\n### 3. Matriz de decomposição\n"
        "- Necessidade/achado de origem | comportamento, regra ou cenário de qualidade decomposto | IDs dos requisitos gerados | cobertura completa/parcial/lacuna\n"
    ),
    agent=documentador,
    context=[t1, t2, t3]
)

t_ra = Task(
    description=(
        "Analise integralmente o catálogo produzido na Task 4 e atribua a cada requisito uma categoria primária exclusiva: RF, RNF ou RA. "
        "Não omita, duplique ou invente requisitos durante a classificação. Preserve texto, origem, evidência e critérios de aceitação, exceto "
        "quando uma alteração mínima for indispensável para tornar a obrigação e sua categoria inequívocas.\n\n"
        "Critérios obrigatórios de classificação:\n"
        "1. RF: comportamento observável que o sistema DEVE executar para um ator ou processo de negócio, incluindo regras, cálculos, consultas, "
        "validações, autorizações e transições. Ser importante ou complexo não transforma automaticamente um RF em RA.\n"
        "2. RNF: nível mensurável de qualidade ou condição operacional verificável — por exemplo, desempenho, disponibilidade, usabilidade, "
        "acessibilidade, confiabilidade, segurança ou manutenibilidade — cujo impacto permaneça localizado ou não atinja o limiar de significância arquitetural.\n"
        "3. RA: obrigação verificável cuja satisfação restringe ou dirige decisões arquiteturais relevantes. Classifique como RA apenas quando houver "
        "Justificativa de significância arquitetural baseada em alcance, impacto, dificuldade de mudança e risco, demonstrando efeito sobre uma ou mais "
        "dimensões: decomposição e responsabilidades; interfaces e integrações; comunicação e distribuição; persistência e fluxo de dados; isolamento "
        "e fronteiras de segurança; concorrência; implantação, operação ou evolução; ou trade-offs sistêmicos entre atributos de qualidade.\n"
        "4. A significância arquitetural é ortogonal ao tipo original: RF, atributos de qualidade e restrições podem ser arquiteturalmente significativos. "
        "Neste catálogo de categorias exclusivas, mantenha como RF o comportamento de negócio, mantenha como RNF a medida de qualidade e crie/classifique "
        "como RA somente a obrigação arquitetural distinta e rastreável que dirige a arquitetura; relacione os requisitos drivers na matriz, sem copiar o mesmo texto.\n"
        "5. Uma restrição tecnológica ou regulatória explicitamente imposta e com impacto arquitetural deve ser RA, identificando a fonte mandatória. "
        "Se não tiver impacto arquitetural, incorpore-a ao RF ou RNF cuja execução ela limita. Preferência, sugestão ou tecnologia inferida não é requisito: "
        "registre-a como candidato a ADR ou AP, sem promovê-la a RA.\n"
        "6. Não classifique como RA apenas por conter palavras como API, banco de dados, nuvem, microsserviço, criptografia ou integração. RA continua sendo "
        "uma necessidade ou restrição verificável, não uma decisão de solução. Reescreva solução prematura como efeito necessário e verificável quando a origem permitir.\n"
        "7. Para casos limítrofes, aplique o teste contrafactual: se arquiteturas substancialmente diferentes puderem satisfazer o requisito sem impacto "
        "estrutural relevante, ele não é RA. Registre a dúvida e a evidência; não force a categoria.\n"
        "8. Preserve IDs quando a categoria continuar correta. Ao reclassificar, atribua o prefixo RF-, RNF- ou RA- correspondente sem colisões e registre "
        "ID anterior -> ID final na matriz de classificação, mantendo todas as referências de origem.\n"
        "9. Faça uma auditoria final de completude: cada ID de entrada deve aparecer exatamente uma vez no catálogo ou em uma decomposição rastreada; "
        "todo RA deve possuir driver, evidência, cenário verificável e justificativa de significância."
    ),
    expected_output=(
        "Um catálogo classificado, completo e sem duplicações, contendo os três blocos de requisitos nesta ordem e, depois, os controles de classificação:\n"
        "## 1. Requisitos Funcionais (RF)\n"
        "- [RF-ID] | [Especificação completa] | [Origem e evidência]\n"
        "  - Critérios de aceitação preservados\n\n"
        "## 2. Requisitos Não Funcionais (RNF)\n"
        "- [RNF-ID] | [Categoria de qualidade] | [Cenário e medida verificável] | [Origem e evidência]\n\n"
        "## 3. Requisitos Arquiteturais (RA)\n"
        "- [RA-ID] | [Necessidade ou restrição arquitetural verificável] | [Origem e evidência]\n"
        "  - Drivers relacionados: [RF/RNF/objetivo]\n"
        "  - Dimensão arquitetural afetada: [estrutura/interface/dados/segurança/distribuição/implantação/evolução/trade-off]\n"
        "  - Justificativa de significância arquitetural: [alcance, impacto, dificuldade de mudança e risco]\n"
        "  - Critério de verificação: [evidência observável sem prescrever solução]\n\n"
        "## 4. Matriz de classificação\n"
        "- ID anterior | ID final | categoria primária | fundamento | driver arquitetural relacionado | decisão/tecnologia removida ou candidata a ADR\n\n"
        "## 5. Auditoria de completude\n"
        "- total de IDs de entrada | total classificado | reclassificados | decompostos | duplicados | não classificados; os dois últimos devem ser zero."
    ),
    agent=arquiteto_requisitos,
    context=[t4]
)

t5 = Task(
    description=(
        "Verifique integralmente o catálogo classificado em RF, RNF e RA. Para cada item, avalie necessidade, correção, atomicidade, "
        "singularidade, clareza, precisão, ausência de ambiguidade, completude, consistência, viabilidade, verificabilidade e rastreabilidade.\n\n"
        "Procedimento obrigatório:\n"
        "1. Todo problema identificado deve incluir diagnóstico, correção textual pronta para aplicação, justificativa e forma de verificar a correção. "
        "Nunca entregue apenas crítica, recomendação genérica ou indicação de correção futura.\n"
        "2. Compare cada requisito com sua evidência. Preserve a intenção sustentada; remova somente conteúdo sem lastro e reformule o restante de modo neutro e verificável.\n"
        "3. Atomicidade: conte obrigações testáveis. Quando houver mais de uma, proponha decomposição; preserve o ID no primeiro requisito e atribua novos IDs aos demais, todos com texto, origem e critérios aplicáveis.\n"
        "4. Ambiguidade: substitua pronomes sem referente, voz passiva sem responsável, comparativos incompletos, opções abertas e termos vagos como 'adequado', 'seguro', 'rápido', "
        "'intuitivo', 'quando necessário', 'conforme definido', 'entre outros' e 'etc.' por condições observáveis sustentadas pelas fontes.\n"
        "5. RF: confirme ator/sistema, uma ação normativa, objeto/resultado, gatilho/condição, regra de negócio necessária e critérios de aceitação coerentes.\n"
        "6. RNF: confirme categoria e cenário mensurável de qualidade. Não aceite métrica, protocolo ou tecnologia arbitrária; quando faltar medida, proponha AP explícita com justificativa e risco.\n"
        "7. RA: rejeite solução prematura ou tecnologia sem origem. Reescreva como necessidade arquitetural neutra quando possível; mantenha tecnologia somente quando houver restrição mandatória e rastreável incorporada ao RA.\n"
        "8. Verifique IDs, referências ENT/AP, duplicidades, contradições, cobertura dos critérios e coerência entre RF, RNF e RA.\n"
        "9. Não marque como corrigido aquilo que permaneça apenas explicado em AP, ADR, nota, matriz ou futuro SDD; a correção deve estar no texto proposto do requisito."
    ),
    expected_output=(
        "0. Linha obrigatória: ERROS_FORMAIS_ENCONTRADOS: SIM/NÃO.\n"
        "1. Matriz de verificação: ID | aprovado/reprovado | critérios avaliados | evidência do defeito | texto corrigido completo | verificação da correção.\n"
        "2. Plano de decomposição: ID original | obrigações encontradas | IDs resultantes | textos completos | origens preservadas.\n"
        "3. Assunções necessárias à correção: AP | decisão provisória | requisitos materializados | justificativa | risco.\n"
        "4. Matriz de consistência: IDs relacionados | contradição/duplicidade | correção textual proposta.\n"
        "5. Catálogo formal proposto após todas as correções, mantendo as seções: "
        "## 1. Requisitos Funcionais (RF), ## 2. Requisitos Não Funcionais (RNF), "
        "## 3. Requisitos Arquiteturais (RA)."
    ),
    agent=verificador,
    context=[t_ra]
)

t_correcao_verificacao = Task(
    description=(
        "Aplique no catálogo cada correção textual e decomposição prescrita pela verificação. Se a verificação não apontar erro, mantenha o catálogo "
        "inalterado e registre 'Nenhuma correção formal necessária'. A primeira seção da resposta deve ser o catálogo integral já corrigido.\n\n"
        "Para cada erro, substitua efetivamente o texto inválido sem perder seu ID ou sua origem; preserve FATO RASTREÁVEL e ASSUNÇÃO DE PROJETO. "
        "Priorize reescrever, reajustar, decompor ou reclassificar o requisito para torná-lo válido e preserve a necessidade original do stakeholder. "
        "Se a atomicidade exigir decomposição, mantenha o ID original no primeiro requisito resultante e crie novos IDs rastreáveis para os demais comportamentos. "
        "A exclusão é o último recurso: somente exclua duplicidade comprovada ou item totalmente fora do escopo que não possa ser reformulado; registre a justificativa e o requisito que preserva sua intenção, quando houver. "
        "Após aplicar as mudanças, percorra o catálogo completo para eliminar contradições introduzidas. Não deixe a correção apenas no log, AP, matriz ou plano."
    ),
    expected_output=(
        "1. Catálogo formal corrigido integral, nas seções RF, RNF e RA, com todos os requisitos por extenso.\n"
        "2. Log de materialização: ID original | problema | ação aplicada | IDs finais | texto anterior | texto final | origem preservada.\n"
        "3. Declaração de que nenhuma correção ficou apenas documentada fora do catálogo."
    ),
    agent=corretor,
    context=[t_ra, t5]
)

t_reverif = Task(
    description=(
        "Reverifique do zero todo o catálogo formal corrigido, usando os mesmos critérios da verificação inicial. Confirme no texto dos requisitos que "
        "cada defeito anterior foi removido e procure novos defeitos ou efeitos colaterais. Não aceite como correção expressões como 'será definido', "
        "'detalhado no SDD', 'conforme AP/ADR', 'direcionado para etapa futura' ou uma explicação existente somente no log. Para cada item reprovado, "
        "forneça novamente uma correção textual completa e verificável. Declare 'VERIFICAÇÃO FORMAL APROVADA' somente quando nenhum requisito do catálogo falhar."
    ),
    expected_output=(
        "0. Linha obrigatória: VERIFICAÇÃO FORMAL APROVADA: SIM/NÃO.\n"
        "1. Matriz de reverificação: ID | critérios | aprovado/reprovado | evidência no texto corrigido | nova correção completa se reprovado.\n"
        "2. Auditoria de materialização: erro anterior | ID corrigido | resolvido/não resolvido | trecho comprobatório.\n"
        "3. Lista de novos defeitos e correções textuais, se houver.\n"
        "4. Catálogo formalmente verificado integral para a etapa de validação."
    ),
    agent=verificador,
    context=[t_ra, t5, t_correcao_verificacao]
)

t6 = Task(
    description=(
        "Valide o catálogo formalmente verificado contra o contexto, objetivos, entrevistas e análise dos Seis Chapéus. Avalie se o catálogo correto "
        "está construindo o sistema certo para cada stakeholder, com cobertura suficiente para orientar o SDD.\n\n"
        "Procedimento obrigatório:\n"
        "1. Para cada requisito, confirme necessidade, valor, adequação ao uso, origem e ausência de solução não solicitada. Classifique a origem como FATO RASTREÁVEL, "
        "DECLARAÇÃO SIMULADA ou ASSUNÇÃO DE PROJETO, citando os IDs.\n"
        "2. Para cada objetivo, necessidade, fluxo, regra, dado, exceção, risco e cenário de qualidade elicitado, indique cobertura completa, parcial, ausente ou indevida. "
        "Só considere completa quando todos os comportamentos testáveis possuírem requisitos próprios e coerentes.\n"
        "3. Todo problema identificado deve incluir diagnóstico, correção textual pronta para aplicação, justificativa e impacto na cobertura. Para lacuna, escreva os novos RF/RNF/RA completos; "
        "para excesso ou contaminação, reescreva o requisito preservando a necessidade válida; para conflito, forneça a versão consolidada.\n"
        "4. Verifique explicitamente, quando aplicável ao contexto atual: cálculo de valor, envio de orçamento e alterações propostas, visualização pelo cliente dos próprios pedidos e status, "
        "histórico de pedidos, anexos e arquivos STL, e cada transição do ciclo de vida.\n"
        "5. Não promova tecnologia, arquitetura, protocolo, produto, métrica ou política inventada a fato. Quando uma decisão provisória for indispensável, crie DECISÃO INFERIDA e "
        "[ASSUNÇÃO DE PROJETO: AP-XX] com justificativa, impacto e risco, e materialize-a em requisito completo.\n"
        "6. Não considere uma lacuna resolvida por AP, nota, matriz, ADR ou indicação de detalhamento futuro; a solução deve existir no texto corretivo proposto.\n"
        "7. Como os stakeholders são simulados, diferencie validação por simulação de aceite humano e liste objetivamente o que exige homologação posterior, sem bloquear a geração do catálogo.\n"
        "8. Liste em uma única linha obrigatória: DECISÕES_INFERIDAS: AP-XX, ..."
    ),
    expected_output=(
        "0. Linha obrigatória: ERROS_DE_VALIDAÇÃO_ENCONTRADOS: SIM/NÃO.\n"
        "1. Matriz de validação por requisito: ID | necessidade/objetivo | origem | válido/não válido | problema | texto corrigido completo.\n"
        "2. Matriz de cobertura: Stakeholder/Necessidade | requisitos atuais | completa/parcial/ausente/indevida | correções ou novos IDs completos.\n"
        "3. Matriz de lacunas e excessos: ID | tipo | impacto | correção materializável | origem/AP | risco residual.\n"
        "4. Catálogo semântico proposto após as correções, com todos os RF/RNF/RA afetados escritos por extenso.\n"
        "5. DECISÕES_INFERIDAS: [lista de AP-XX].\n"
        "6. Itens que exigem homologação humana e declaração de prontidão para correção do catálogo."
    ),
    agent=validador,
    context=[t1, t2, t3, t_reverif]
)

t_correcao = Task(
    description=(
        "Aplique ao catálogo formalmente verificado todas as correções textuais, decomposições e novos requisitos prescritos pela validação.\n"
        "Regras:\n"
        "0. Se o relatório não apontar lacuna, contaminação ou inconsistência, mantenha o catálogo inalterado e registre 'Nenhuma correção necessária'.\n"
        "1. Para cada lacuna, excesso, contaminação ou conflito, aplique a redação corrigida no corpo do catálogo. Crie ou ajuste requisitos com ID, sintaxe "
        "'[Ator] + DEVE + [Verbo] + [Objeto] + [Condição]' e origem explícita.\n"
        "1.1 A primeira seção da sua resposta DEVE ser '## Catálogo Consolidado'. Nessa seção, reproduza o catálogo inteiro já corrigido; não apresente log, AP, matriz ou justificativa antes dele.\n"
        "2. Não considere uma lacuna resolvida por uma AP isolada: cada decisão inferida deve ser materializada em um ou mais RF, RNF ou RA atômicos, com novo ID e texto completo. A AP apenas justifica a origem; nunca substitui o requisito.\n"
        "3. Quando uma necessidade contiver mais de um comportamento, gere um requisito para cada comportamento testável, como cálculo, registro, consulta, validação, transição, notificação ou autorização.\n"
        "4. Para cada lacuna da validação, substitua a lacuna por requisitos textualmente completos no catálogo; não responda apenas com matriz, resumo, AP ou referência a outro requisito.\n"
        "5. Para cada lacuna ou item corrigido, aplique a DECISÃO INFERIDA correspondente quando necessária, marque a origem como ASSUNÇÃO DE PROJETO e materialize a decisão em requisitos atômicos.\n"
        "6. Lacuna que depende de decisão não tomada: escolha a alternativa mais simples, segura e reversível; registre justificativa e risco.\n"
        "7. Priorize reescrever, reajustar, decompor ou reclassificar cada requisito inválido para torná-lo válido e preserve a necessidade original do stakeholder. Quando houver premissa sem lastro, remova somente a premissa e reescreva o requisito de forma neutra e rastreável.\n"
        "8. A exclusão é o último recurso: somente exclua duplicidade comprovada ou item totalmente fora do escopo que não possa ser reformulado. Registre a justificativa e indique quais requisitos preservam a necessidade original.\n"
        "9. Mantenha os IDs existentes nos requisitos reajustados. Em decomposições, preserve o ID original no primeiro requisito e crie novos IDs rastreáveis para os comportamentos adicionais.\n"
        "10. Ao finalizar, compare o catálogo com cada linha das matrizes de validação. Não declare resolvido item cujo texto antigo ainda exista ou cuja correção esteja apenas no log, AP, ADR ou futuro SDD."
    ),
    expected_output=(
        "1. ## Catálogo Consolidado como primeira seção: catálogo consolidado integral. Ele deve ser o Catálogo semanticamente corrigido integral, contendo RF, RNF e RA; cada requisito aparece por extenso com ID, especificação, origem/evidência e critérios aplicáveis. É proibido responder apenas com APs, referências, matriz ou plano.\n"
        "2. Log de materialização: problema/lacuna | ação aplicada | IDs anteriores/finais | trecho final comprobatório | origem preservada.\n"
        "3. Assunções de Projeto e Riscos Residuais, vinculadas aos requisitos completos que as materializam.\n"
        "4. Matriz de cobertura atualizada, demonstrando que cada necessidade possuir cobertura completa: necessidade | IDs atômicos | cobertura após correção | evidência textual.\n"
        "5. Declaração de que todas as correções foram incorporadas ao catálogo, sem delegação a etapa futura."
    ),
    agent=corretor,
    context=[t_reverif, t6]
)

t_revalidacao = Task(
    description=(
        "Revalide o catálogo corrigido do zero contra contexto, elicitação e validação original. Confirme no texto de cada requisito "
        "que lacunas, excessos, contaminações e conflitos foram materialmente resolvidos e procure novos problemas. Não aceite como correção expressões como "
        "'será definido', 'detalhado no SDD', 'conforme AP/ADR', 'direcionado para etapa futura' ou resolução existente apenas em log, matriz ou assunção. "
        "Não considere uma lacuna resolvida por uma AP isolada: ela só está resolvida quando o catálogo contém requisitos completos, atômicos, coerentes e rastreáveis. "
        "Sem os requisitos textualmente consolidados, a revalidação deve ser NÃO aprovada. "
        "Para todo item ainda reprovado, forneça nova correção textual completa; nunca apenas aponte o problema. A aprovação global só pode ser SIM se cada item do catálogo e cada necessidade estiver aprovado."
    ),
    expected_output=(
        "0. Linha obrigatória: VALIDAÇÃO APROVADA: SIM/NÃO.\n"
        "1. Matriz de revalidação por requisito: ID | necessidade/origem | válido/não válido | evidência textual | nova correção completa se inválido.\n"
        "2. Auditoria de materialização: problema anterior | IDs corrigidos | resolvido/não resolvido | trecho comprobatório.\n"
        "3. Matriz final de cobertura por stakeholder e necessidade.\n"
        "4. Lista de novos problemas com correções textuais materializáveis, se houver.\n"
        "5. Lista de requisitos aprovados individualmente e itens que exigem homologação humana."
    ),
    agent=validador,
    context=[t1, t2, t3, t6, t_correcao]
)

t_catalogo_final = Task(
    description=(
        "Produza o catálogo final consolidado após a verificação e a validação. Use exclusivamente o catálogo corrigido como fonte e preserve todos "
        "os requisitos corrigidos; não rejeite, filtre ou remova requisitos por status de aprovação. Corrija defeitos no texto do requisito e mantenha "
        "pendências sem fonte como pendências rastreáveis, fora do catálogo.\n\n"
        "A saída deve conter SOMENTE requisitos finais, nas três seções abaixo e nesta ordem: "
        "## 1. Requisitos Funcionais (RF), ## 2. Requisitos Não Funcionais (RNF), ## 3. Requisitos Arquiteturais (RA). "
        "Não inclua título, introdução, log de alterações, relatório de validação, restrições do sistema, assunções, riscos, "
        "pendências, ADRs, blocos de código Markdown ou texto fora dessas seções. Preserve IDs, especificações, origem, evidência e critérios de aceitação aplicáveis. "
        "Cada requisito aprovado deve estar por extenso. Mantenha as três seções mesmo quando uma delas não possuir requisito aprovado."
    ),
    expected_output=(
        "Somente as seções ## 1. Requisitos Funcionais (RF), ## 2. Requisitos Não Funcionais (RNF) e "
        "## 3. Requisitos Arquiteturais (RA), contendo exclusivamente o catálogo final aprovado."
    ),
    agent=documentador,
    context=[t_correcao, t_revalidacao]
)

t_adr = Task(
    description=(
        "Para elaborar os Architecture Decision Records, use o catálogo final aprovado como única autoridade de requisitos. Considere conjuntamente "
        "os RF, RNF e RA: RF descrevem comportamentos que a solução deve viabilizar; RNF fornecem critérios mensuráveis; RA identificam drivers e "
        "limites arquiteturais. Ignore versões intermediárias, requisitos reprovados e detalhes não presentes no catálogo final.\n\n"
        "Procedimento obrigatório:\n"
        "1. Construa primeiro uma matriz de drivers relacionando cada RF, RNF e RA às preocupações arquiteturais que ele gera. Um requisito pode alimentar "
        "várias decisões e uma decisão pode atender vários requisitos. Não presuma que apenas RA fundamenta ADR.\n"
        "2. Agrupe requisitos que dependem da mesma escolha e formule uma pergunta decisória específica; não crie um ADR por requisito e não crie ADR "
        "quando não houver alternativa relevante, consequência duradoura ou impacto arquitetural.\n"
        "3. Delimite o contexto e as forças da decisão usando IDs exatos. Separe obrigação do requisito, assunção e preferência. Não altere nem complete requisitos.\n"
        "4. Defina Critérios de decisão derivados dos requisitos, incluindo medidas e prioridades presentes nos RNF/RA, cobertura dos RF, restrições, "
        "custo de mudança, risco e reversibilidade. Não invente pesos, métricas ou prioridades; quando ausentes, registre a incerteza.\n"
        "5. Compare pelo menos duas alternativas realmente viáveis, incluindo 'manter simples/adiar a especialização' quando aplicável. Avalie todas pelo "
        "mesmo conjunto de critérios e descarte explicitamente opções que violem requisitos, citando os IDs violados.\n"
        "6. Escolha uma alternativa e descreva precisamente o que foi decidido, seu escopo e o que ficou fora dele. A decisão deve explicar como será possível "
        "atender aos requisitos, sem prometer que a tecnologia, por si só, garante seu cumprimento.\n"
        "7. Registre consequências positivas, negativas, trade-offs, riscos residuais, custo de adoção/operação, dependências, impacto evolutivo e requisitos "
        "beneficiados ou tensionados. Não esconda conflitos entre RNF.\n"
        "8. Produza um Plano de verificação da decisão ligando cada requisito motivador a evidência futura — teste, medição, experimento, análise ou revisão — "
        "e ao critério objetivo que demonstrará que a escolha funciona.\n"
        "9. Quando dados essenciais estiverem ausentes, adote a alternativa mais simples, segura e reversível capaz de satisfazer o catálogo; marque "
        "'DECISÃO INFERIDA', associe [ASSUNÇÃO DE PROJETO: AP-XX], registre risco e defina gatilho de revisão. Não transforme a inferência em requisito.\n"
        "10. Numere os ADRs como ADR-001, ADR-002...; use status PROPOSTO para decisões ainda não homologadas. Cada ADR deve ser atômico, podendo "
        "referenciar decisões relacionadas, substituídas ou dependentes sem fundi-las. Ao final, audite a cobertura de todos os RA e dos RF/RNF que geram decisões."
    ),
    expected_output=(
        "Um documento Markdown sem introdução genérica, composto por:\n\n"
        "## Matriz de drivers e cobertura\n"
        "- Requisito (RF/RNF/RA) | força/preocupação | decisão necessária? | ADR relacionado ou justificativa para não gerar ADR\n\n"
        "## ADR-XXX — [Título como decisão]\n"
        "- Status: PROPOSTO | ACEITO | SUBSTITUÍDO\n"
        "- Tipo: DECISÃO FUNDAMENTADA | DECISÃO INFERIDA\n"
        "- Requisitos motivadores: [IDs RF/RNF/RA]\n"
        "- Decisões relacionadas/substituídas: [IDs ou nenhuma]\n\n"
        "### Contexto e problema decisório\n"
        "[problema, escopo, forças e pergunta que precisa ser decidida]\n\n"
        "### Critérios de decisão derivados dos requisitos\n"
        "- Critério | IDs de origem | medida/prioridade conhecida | incerteza\n\n"
        "### Alternativas consideradas\n"
        "- Alternativa | atendimento por critério | requisitos satisfeitos/tensionados/violados | vantagens | desvantagens | riscos | reversibilidade\n\n"
        "### Decisão\n"
        "[alternativa escolhida, limites e como ela contribui para atender aos requisitos]\n\n"
        "### Justificativa e trade-offs\n"
        "[comparação baseada nos critérios, sem alegações não sustentadas]\n\n"
        "### Consequências\n"
        "- Positivas:\n- Negativas:\n- Riscos residuais e mitigações:\n- Impacto operacional e evolutivo:\n\n"
        "### Assunções e gatilhos de revisão\n"
        "- AP vinculada ou nenhuma | evidência pendente | evento/limiar que exige revisar o ADR\n\n"
        "### Plano de verificação da decisão\n"
        "- ID do requisito | evidência a coletar | método de verificação | critério de aprovação\n\n"
        "## Matriz de cobertura da decisão\n"
        "- ADR | RF atendidos | RNF atendidos/tensionados | RA atendidos | lacunas | risco residual\n\n"
        "## Auditoria final\n"
        "- RA sem ADR ou justificativa | RF/RNF com decisão não coberta | decisões sem requisito de origem | conflitos não resolvidos; "
        "a terceira contagem deve ser zero."
    ),
    agent=criador_adr,
    context=[t_catalogo_final]
)


t_arquitetura = Task(
    description=(
        "Produza o Documento Oficial de Arquitetura de Software em Markdown usando o catálogo final de RF, RNF e RA e os ADRs como fontes normativas exclusivas. "
        "Os requisitos determinam o que deve ser atendido; ADRs não substituídos determinam as escolhas adotadas para atendê-los. Não recupere requisito "
        "reprovado, não invente comportamento e não introduza tecnologia ou decisão ausente dos ADRs. Use exatamente a organização de Visão Geral, Atores e Interações, "
        "Estrutura Arquitetural por blocos e Matriz de Rastreabilidade descrita no expected_output.\n\n"
        "Procedimento obrigatório:\n"
        "1. Identifique projeto, escopo, requisitos, ADRs vigentes e decisões inferidas. O status deve refletir as evidências: não escreva 'Aprovado' sem aceite humano explícito.\n"
        "2. Na Visão Geral, descreva o estilo arquitetural, a organização macro e a Stack Tecnológico Base somente quando decisões e tecnologias constarem dos ADRs ou "
        "das fontes. Para cada detalhe ausente, escreva 'NÃO DEFINIDO' e relacione a lacuna e os IDs afetados.\n"
        "3. Em Atores e Interações, separe Perfis de Usuários de Sistemas Externos. Para cada um, descreva somente responsabilidades, capacidades e integrações sustentadas "
        "por requisitos ou ADRs, incluindo IDs de origem quando necessário para esclarecer a rastreabilidade.\n"
        "4. Em Estrutura Arquitetural, agrupe elementos em blocos coesos. Cada bloco tem responsabilidade principal e componentes com responsabilidade específica. Um componente, "
        "serviço, banco, fila, armazenamento ou conector somente pode existir se houver RF/RNF/RA ou ADR identificado que o justifique.\n"
        "5. Para cada componente, explique como ele contribui para realizar requisitos e ADRs; não gere endpoints, protocolos, limites, tecnologias, métricas, políticas de "
        "retentativa, mecanismos de segurança ou integrações sem fonte. Decisão não confirmada deve aparecer como LACUNA ARQUITETURAL, e não como fato.\n"
        "6. Finalize a Matriz de Rastreabilidade ligando cada bloco/componente aos ADRs, RNF/métricas e RF/RA relacionados. Inclua todos os IDs aplicáveis, lacunas explícitas "
        "e 'N/A' quando uma coluna não se aplicar. Faça auditoria bidirecional: nenhum componente sem origem e nenhum requisito arquiteturalmente relevante sem bloco ou lacuna.\n"
        "7. Não inclua seções adicionais, diagramas em código, relatório de raciocínio ou texto genérico. Não invente tecnologias, métricas, integrações ou detalhes para imitar "
        "um exemplo de arquitetura; a estrutura deve ser estável, mas o conteúdo depende exclusivamente das fontes."
    ),
    expected_output=(
        "Um documento Markdown completo, sem introduções genéricas ou seções além das seguintes:\n\n"
        "# Documento Oficial de Arquitetura de Software\n\n"
        "**Projeto:** [nome do projeto extraído do contexto ou NÃO DEFINIDO]  \n"
        "**Autor:** Arquiteto de Sistemas Sênior  \n"
        "**Status:** [PROPOSTO, INFERIDO, ACEITO ou NÃO DEFINIDO conforme evidência]  \n\n"
        "---\n\n"
        "## 1. Visão Geral da Arquitetura\n\n"
        "[Estilo arquitetural, organização macro, fronteiras e justificativa rastreável.]\n\n"
        "### Stack Tecnológico Base\n"
        "- **[Camada ou capacidade]:** [tecnologia/decisão somente se sustentada por ADR ou fonte; caso contrário, NÃO DEFINIDO — lacuna e IDs afetados].\n\n"
        "---\n\n"
        "## 2. Atores e Interações\n\n"
        "### Perfis de Usuários\n"
        "- **[Ator]:**\n"
        "  - [responsabilidade ou interação sustentada por RF/RNF/RA].\n\n"
        "### Sistemas Externos\n"
        "- **[Sistema externo]:**\n"
        "  - [responsabilidade, fronteira e integração sustentadas por fonte].\n\n"
        "---\n\n"
        "## 3. Estrutura Arquitetural\n\n"
        "### [Bloco N: Nome do bloco]\n"
        "- **Responsabilidade Principal:** [uma responsabilidade coesa e seus IDs de origem].\n"
        "- **Principais Componentes:**\n"
        "  - **[Componente]:** [responsabilidade, requisitos/ADRs realizados e lacuna explícita quando aplicável].\n\n"
        "[Repita o bloco apenas para fronteiras arquiteturais justificadas pelas fontes.]\n\n"
        "---\n\n"
        "## 4. Matriz de Rastreabilidade\n\n"
        "| Bloco / Componente Arquitetural | ADR Associado | RNF / Métricas Atendidos | Requisitos Funcionais e Arquiteturais Relacionados |\n"
        "| :--- | :--- | :--- | :--- |\n"
        "| [Bloco/componente] | [ADR-XXX ou N/A] | [RNF-ID/métrica, N/A ou lacuna] | [RF/RA IDs e lacunas] |"
    ),
    agent=arquiteto_sistemas,
    context=[t_catalogo_final, t_adr]
)


MAX_RODADAS_DE_CORRECAO = 1


def executar_tarefa_llm(agent, description, expected_output):
    """Executa uma task isolada; a decisão de conteúdo permanece com o agente LLM."""
    task = Task(
        description=description,
        expected_output=expected_output,
        agent=agent,
    )
    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        cache=False,
        verbose=True,
    )
    return str(crew.kickoff())


def instrucoes_de_correcao(catalogo, diagnostico, etapa, fontes):
    return f"""
Você é o CORRETOR da rodada {etapa}. Reescreva o catálogo abaixo somente para resolver os erros bloqueantes apontados pelo avaliador.

REGRAS NÃO NEGOCIÁVEIS:
1. Preserve fatos confirmados e seus IDs de origem. Não transforme DECLARAÇÃO SIMULADA, AP, pergunta aberta ou alternativa em FATO RASTREÁVEL.
2. Uma AP não confirma uma necessidade. Se uma lacuna depender de regra, estado, métrica, canal, formato, prazo, política ou tecnologia não informado,
   mantenha-a como pendência/assunção fora do catálogo publicado; o conteúdo de uma AP não pode ser publicado como requisito aprovado; não invente o requisito para preencher a lacuna.
3. Todo RF, RNF e RA deve ter uma única obrigação testável. Decomponha comportamentos independentes em novos IDs rastreáveis.
4. Não altere enumerações, estados, transições ou regras explicitamente presentes nas fontes; registre a pendência no relatório quando faltar informação.
5. RA expressa necessidade arquitetural verificável; padrões, protocolos, serviços, produtos e tecnologias pertencem ao ADR, salvo restrição explicitamente imposta.
6. Entregue SOMENTE o catálogo corrigido nas seções RF, RNF e RA, com requisitos completos, origem e critérios aplicáveis. Não inclua relatório, log ou julgamento.

FONTES AUTORITATIVAS PARA PRESERVAR CONTEXTO:
{fontes}

CATÁLOGO A CORRIGIR:
{catalogo}

CORREÇÕES EXIGIDAS PELO AVALIADOR:
{diagnostico}
"""


def executar_ciclo_formal(catalogo, contexto_confirmado, entrevistas, chapeus):
    """Executa uma verificação formal e uma única correção completa do catálogo."""
    fontes = f"CONTEXTO:\n{contexto_confirmado}\n\nENTREVISTAS:\n{entrevistas}\n\nSEIS CHAPÉUS:\n{chapeus}"
    diagnostico = executar_tarefa_llm(
        verificador,
        f"""Verifique formalmente o catálogo abaixo contra as fontes. Identifique defeitos e correções exigidas; não rejeite, filtre ou aprove artefatos.
Todo problema deve indicar ID, critério violado, evidência, impacto e correção exigida. Marque como bloqueante: falta de atomicidade,
ambiguidade, requisito sem origem, tecnologia prematura, estado/regra/métrica sem fonte e inconsistência entre categorias.

FONTES:
{fontes}

CATÁLOGO:
{catalogo}""",
        "Relatório de verificação com IDs, correções completas, lacunas de cobertura e uma matriz requisito/origem/correção; não gere veredito de aprovação ou reprovação.",
    )

    corrigido = executar_tarefa_llm(
        corretor,
        instrucoes_de_correcao(catalogo, diagnostico, "formal", fontes),
        "Somente catálogo corrigido completo nas seções ## 1. Requisitos Funcionais (RF), ## 2. Requisitos Não Funcionais (RNF) e ## 3. Requisitos Arquiteturais (RA).",
    )
    return corrigido, diagnostico, [(1, diagnostico, corrigido)]


def executar_ciclo_semantico(catalogo, contexto, entrevistas, chapeus):
    """Executa uma validação semântica e uma única correção completa do catálogo."""
    fontes = f"CONTEXTO:\n{contexto}\n\nENTREVISTAS:\n{entrevistas}\n\nSEIS CHAPÉUS:\n{chapeus}"
    diagnostico = executar_tarefa_llm(
        validador,
        f"""Valide se o catálogo atende às necessidades das fontes abaixo. Não rejeite, filtre ou aprove artefatos; converta cada defeito em correção completa.
Para cada defeito, informe ID, fonte contradita/ausente, impacto e correção exigida. Uma necessidade ainda não confirmada deve virar pendência,
não requisito final. Exija cobertura para fatos explícitos, mas não converta hipóteses em fatos.

{fontes}

CATÁLOGO:
{catalogo}""",
        "Relatório de validação com lacunas, excessos, conflitos, cobertura por necessidade e correções completas; não gere veredito de aprovação ou reprovação.",
    )
    corrigido = executar_tarefa_llm(
        corretor,
        instrucoes_de_correcao(catalogo, diagnostico, "semântica", fontes),
        "Somente catálogo corrigido completo nas seções ## 1. Requisitos Funcionais (RF), ## 2. Requisitos Não Funcionais (RNF) e ## 3. Requisitos Arquiteturais (RA).",
    )
    return corrigido, diagnostico, [(1, diagnostico, corrigido)]


crew_elicitacao = Crew(
    agents=[contextualizador, entrevistador, chapeus, documentador, arquiteto_requisitos],
    tasks=[t1, t2, t3, t4, t_ra],
    process=Process.sequential,
    cache=False,
    verbose=True,
)

crew_elicitacao.kickoff()
diretorio_execucao = criar_diretorio_execucao()
salvar_artefato(diretorio_execucao, "01-contexto-confirmado.md", t1.output)
salvar_artefato(diretorio_execucao, "02-entrevistas.md", t2.output)
salvar_artefato(diretorio_execucao, "03-seis-chapeus.md", t3.output)
salvar_artefato(diretorio_execucao, "04-requisitos-iniciais.md", t4.output)
salvar_artefato(diretorio_execucao, "05-classificacao-ra.md", t_ra.output)

catalogo_inicial = str(t_ra.output)
catalogo_formal, relatorio_formal, historico_formal = executar_ciclo_formal(
    catalogo_inicial,
    str(t1.output),
    str(t2.output),
    str(t3.output),
)
diagnostico_formal, catalogo_pos_verificacao = historico_formal[0][1:]
salvar_artefato(diretorio_execucao, "06-verificacao-formal.md", diagnostico_formal)
salvar_artefato(diretorio_execucao, "07-catalogo-pos-verificacao.md", catalogo_pos_verificacao)

catalogo_semantico, relatorio_semantico, historico_semantico = executar_ciclo_semantico(
    catalogo_formal,
    str(t1.output),
    str(t2.output),
    str(t3.output),
)
diagnostico_semantico, catalogo_pos_validacao = historico_semantico[0][1:]
salvar_artefato(diretorio_execucao, "08-validacao-semantica.md", diagnostico_semantico)
salvar_artefato(diretorio_execucao, "09-catalogo-pos-validacao.md", catalogo_pos_validacao)

catalogo_final = catalogo_semantico
salvar_artefato(diretorio_execucao, "10-catalogo-final.md", catalogo_final)

adr_final = executar_tarefa_llm(
    criador_adr,
    f"{t_adr.description}\n\nCATÁLOGO FINAL APROVADO:\n{catalogo_final}",
    t_adr.expected_output,
)
salvar_artefato(diretorio_execucao, "11-adrs.md", adr_final)
arquitetura_final = executar_tarefa_llm(
    arquiteto_sistemas,
    f"{t_arquitetura.description}\n\nCATÁLOGO FINAL APROVADO:\n{catalogo_final}\n\nADRS:\n{adr_final}",
    t_arquitetura.expected_output,
)
salvar_artefato(diretorio_execucao, "12-arquitetura.md", arquitetura_final)
