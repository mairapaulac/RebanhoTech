import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#6c757d"))
        
        # Don't draw header/footer on page 1 (cover)
        if self._pageNumber > 1:
            # Header
            self.drawString(54, 750, "RebanhoTech — Manual do Projeto & Roteiro de Apresentação (UNIVASF)")
            self.setStrokeColor(colors.HexColor("#dee2e6"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)
            
            # Footer
            self.line(54, 45, 558, 45)
            self.drawString(54, 32, "Sistemas Distribuídos (CCMP0054) • Engenharia da Computação")
            page_text = f"Página {self._pageNumber} de {page_count}"
            self.drawRightString(558, 32, page_text)
            
        self.restoreState()


def build_pdf(filename="Guia_Apresentacao_RebanhoTech.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    primary_color = colors.HexColor("#146c43")
    secondary_color = colors.HexColor("#198754")
    dark_color = colors.HexColor("#212529")
    text_color = colors.HexColor("#2b2f33")

    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=26,
        leading=32,
        textColor=primary_color,
        alignment=1, # Center
        spaceAfter=10
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=18,
        textColor=colors.HexColor("#495057"),
        alignment=1,
        spaceAfter=25
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=primary_color,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=secondary_color,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=text_color,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=text_color,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=3
    )

    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#212529")
    )

    box_text_style = ParagraphStyle(
        'BoxText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1e4620")
    )

    story = []

    # ====================================================
    # CAPA DO DOCUMENTO
    # ====================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("UNIVERSIDADE FEDERAL DO VALE DO SÃO FRANCISCO", ParagraphStyle('Uni', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, alignment=1, textColor=colors.HexColor("#6c757d"), spaceAfter=4)))
    story.append(Paragraph("Colegiado de Engenharia da Computação &bull; Sistemas Distribuídos (CCMP0054)", ParagraphStyle('Course', parent=styles['Normal'], fontName='Helvetica', fontSize=10, alignment=1, textColor=colors.HexColor("#6c757d"), spaceAfter=30)))
    
    story.append(HRFlowable(width="100%", thickness=3, color=primary_color, spaceAfter=25, spaceBefore=0))
    
    story.append(Paragraph("REBANHOTECH", title_style))
    story.append(Paragraph("Sistema Web para Gestão Pecuária Inteligente, Rastreabilidade e Marketplace Agro", subtitle_style))
    
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#dee2e6"), spaceAfter=20, spaceBefore=0))

    info_card_data = [
        [Paragraph("<b>Documento:</b>", body_style), Paragraph("Manual Completo de Execução, Arquitetura e Roteiro de Defesa Oral", body_style)],
        [Paragraph("<b>Entregas Cobertas:</b>", body_style), Paragraph("Entrega I (Ideia), Entrega II (Modelos/Admin), Entrega III (Views/Forms) e Entrega IV (Final Cloud + Apresentação)", body_style)],
        [Paragraph("<b>Tecnologias:</b>", body_style), Paragraph("Python 3, Django, PostgreSQL / SQLite, Bootstrap 5, WhiteNoise, REST APIs", body_style)],
        [Paragraph("<b>Status do Projeto:</b>", body_style), Paragraph("<font color='#146c43'><b>100% Concluído &bull; 13 Testes Automatizados Aprovados</b></font>", body_style)],
    ]
    info_table = Table(info_card_data, colWidths=[120, 384])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8f9fa")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#dee2e6")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e9ecef")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(info_table)
    
    story.append(Spacer(1, 30))
    
    resumo_box = [
        [Paragraph("<b>Resumo Executivo do Sistema</b>", ParagraphStyle('RHead', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=primary_color))],
        [Paragraph(
            "O <b>RebanhoTech</b> é uma plataforma moderna desenvolvida para resolver as dores reais da gestão do rebanho e comercialização de animais no Vale do São Francisco. "
            "O sistema unifica a rastreabilidade individual zootécnica (genealogia, pesagens, calendário sanitário e reprodução), o controle logístico de transferências entre fazendas, "
            "e um marketplace integrado com sistema de contrapropostas P2P e notificações em tempo real. "
            "Além disso, integra-se com serviços externos de cotação via API REST e expõe seus próprios serviços REST para a comunidade acadêmica.",
            body_style
        )]
    ]
    resumo_table = Table(resumo_box, colWidths=[504])
    resumo_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#e8f5e9")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#a5d6a7")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(resumo_table)
    
    story.append(PageBreak())

    # ====================================================
    # SEÇÃO 1: COMO RODAR O PROJETO PASSO A PASSO
    # ====================================================
    story.append(Paragraph("1. Guia Prático: Como Rodar o Projeto", h1_style))
    story.append(Paragraph("Siga o passo a passo abaixo para rodar e testar o sistema localmente em qualquer computador com Python instalado:", body_style))
    
    step1 = [
        [Paragraph("<b>Passo 1: Acessar a pasta do projeto no Terminal / PowerShell</b>", h2_style)],
        [Paragraph("Abra o terminal e navegue até a pasta raiz:", body_style)],
        [Table([[Paragraph("cd \"C:\\Users\\henri\\OneDrive\\Área de Trabalho\\Henrique\\Univasf\\SD1\\RebanhoTech-main\\RebanhoTech-main\"", code_style)]], colWidths=[480], style=[('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f3f5")), ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#ced4da"))])]
    ]
    story.append(Table(step1, colWidths=[504], style=[('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#e9ecef")), ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(Spacer(1, 5))

    step2 = [
        [Paragraph("<b>Passo 2: Instalar as Dependências</b>", h2_style)],
        [Paragraph("Instale os pacotes listados no <code>requirements.txt</code>:", body_style)],
        [Table([[Paragraph("pip install -r requirements.txt", code_style)]], colWidths=[480], style=[('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f3f5")), ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#ced4da"))])],
    ]
    story.append(Table(step2, colWidths=[504], style=[('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#e9ecef")), ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(Spacer(1, 5))

    step3 = [
        [Paragraph("<b>Passo 3: Migrar o Banco de Dados</b>", h2_style)],
        [Paragraph("Para aplicar migrações na base de dados relacional:", body_style)],
        [Table([[Paragraph("python manage.py migrate", code_style)]], colWidths=[480], style=[('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f3f5")), ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#ced4da"))])]
    ]
    story.append(Table(step3, colWidths=[504], style=[('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#e9ecef")), ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(Spacer(1, 5))

    step4 = [
        [Paragraph("<b>Passo 4: Popular a Base de Dados (Carga Inicial Fictícia)</b>", h2_style)],
        [Paragraph("Comando customizado para popular a base com animais, fazendas, pesagens e anúncios:", body_style)],
        [Table([[Paragraph("python manage.py popular_banco", code_style)]], colWidths=[480], style=[('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f3f5")), ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#ced4da"))])],
    ]
    story.append(Table(step4, colWidths=[504], style=[('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#e9ecef")), ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(Spacer(1, 5))

    step5 = [
        [Paragraph("<b>Passo 5: Executar a Suíte de Testes Automatizados</b>", h2_style)],
        [Paragraph("Para comprovar a estabilidade e qualidade do código ao professor:", body_style)],
        [Table([[Paragraph("python manage.py test", code_style)]], colWidths=[480], style=[('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f3f5")), ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#ced4da"))])]
    ]
    story.append(Table(step5, colWidths=[504], style=[('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#e9ecef")), ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(Spacer(1, 5))

    step6 = [
        [Paragraph("<b>Passo 6: Iniciar o Servidor Web de Desenvolvimento</b>", h2_style)],
        [Paragraph("Inicie a aplicação e acesse em <b>http://127.0.0.1:8000/</b> no navegador:", body_style)],
        [Table([[Paragraph("python manage.py runserver", code_style)]], colWidths=[480], style=[('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f3f5")), ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#ced4da"))])]
    ]
    story.append(Table(step6, colWidths=[504], style=[('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#e9ecef")), ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    
    story.append(Spacer(1, 8))

    # Tabela de Credenciais
    cred_heading = Paragraph("<b>Contas de Acesso Já Cadastradas no Banco (Seed Data):</b>", h2_style)
    cred_data = [
        [Paragraph("<b>Usuário</b>", body_style), Paragraph("<b>Senha</b>", body_style), Paragraph("<b>Perfil de Acesso</b>", body_style), Paragraph("<b>Finalidade</b>", body_style)],
        [Paragraph("<code>admin</code>", code_style), Paragraph("<code>admin123</code>", code_style), Paragraph("Superusuário / Staff", body_style), Paragraph("Painel Admin e visão total", body_style)],
        [Paragraph("<code>mouraisaque</code>", code_style), Paragraph("<code>senha123</code>", code_style), Paragraph("Criador (Vendedor)", body_style), Paragraph("Manejo, propostas e anúncios", body_style)],
        [Paragraph("<code>oliviacamargo</code>", code_style), Paragraph("<code>senha123</code>", code_style), Paragraph("Criadora (Compradora)", body_style), Paragraph("Negociação P2P entre criadores", body_style)],
    ]
    cred_table = Table(cred_data, colWidths=[90, 80, 134, 200])
    cred_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e2e3e5")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#ced4da")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(KeepTogether([cred_heading, cred_table]))

    story.append(PageBreak())

    # ====================================================
    # SEÇÃO 2: ARQUITETURA E MODELAGEM DE DADOS
    # ====================================================
    story.append(Paragraph("2. Arquitetura do Sistema e Modelagem de Dados", h1_style))
    story.append(Paragraph(
        "O RebanhoTech foi estruturado rigorosamente seguindo o padrão arquitetural <b>MVT (Model-View-Template)</b> do Django. "
        "O sistema é composto por duas aplicações desacopladas, atendendo ao requisito de modularização do projeto:",
        body_style
    ))
    story.append(Paragraph("&bull; <b>App <code>rebanho</code>:</b> Responsável pela gestão zootécnica, propriedades rurais, dados sanitários, árvore genealógica e manejo reprodutivo.", bullet_style))
    story.append(Paragraph("&bull; <b>App <code>core</code>:</b> Responsável pelas regras de negócio centrais, autenticação de criadores, transferências logísticas, marketplace P2P, notificações e APIs REST.", bullet_style))
    
    story.append(Spacer(1, 8))
    story.append(Paragraph("Detalhamento das 9 Tabelas (Modelos Relacionais)", h2_style))
    story.append(Paragraph("O sistema atende plenamente ao intervalo obrigatório de 7 a 10 modelos relacionais:", body_style))

    models_data = [
        [Paragraph("<b>App</b>", body_style), Paragraph("<b>Modelo</b>", body_style), Paragraph("<b>Campos Principais</b>", body_style), Paragraph("<b>Relacionamentos & Descrição</b>", body_style)],
        [Paragraph("<code>rebanho</code>", code_style), Paragraph("<b>Propriedade</b>", body_style), Paragraph("nome, area_hectares, cidade, estado", body_style), Paragraph("FK para <code>User</code> (Criador). Representa a fazenda/sítio.", body_style)],
        [Paragraph("<code>rebanho</code>", code_style), Paragraph("<b>Animal</b>", body_style), Paragraph("brinco, raca, sexo, data_nascimento", body_style), Paragraph("FK para <code>Propriedade</code>. <b>Auto-relacionamento</b> para pai e mãe (genealogia).", body_style)],
        [Paragraph("<code>rebanho</code>", code_style), Paragraph("<b>Pesagem</b>", body_style), Paragraph("peso_kg, data_pesagem", body_style), Paragraph("FK para <code>Animal</code>. Histórico de evolução e ganho de peso.", body_style)],
        [Paragraph("<code>rebanho</code>", code_style), Paragraph("<b>Vacinacao</b>", body_style), Paragraph("vacina, data_aplicacao, proxima_dose", body_style), Paragraph("FK para <code>Animal</code>. Calendário profilático e sanitário.", body_style)],
        [Paragraph("<code>rebanho</code>", code_style), Paragraph("<b>Reproducao</b>", body_style), Paragraph("data_cobertura, data_parto, qtd_crias", body_style), Paragraph("FK para <code>Animal</code> (fêmea matriz). Coberturas, partos e crias.", body_style)],
        [Paragraph("<code>core</code>", code_style), Paragraph("<b>Movimentacao</b>", body_style), Paragraph("data_movimentacao, motivo", body_style), Paragraph("FKs para <code>Animal</code>, <code>Origem</code> e <code>Destino</code>. Rastreabilidade.", body_style)],
        [Paragraph("<code>core</code>", code_style), Paragraph("<b>Anuncio</b>", body_style), Paragraph("titulo, preco, descricao, ativo", body_style), Paragraph("FKs para <code>User</code> (Vendedor) e <code>Animal</code>. Vitrine de venda.", body_style)],
        [Paragraph("<code>core</code>", code_style), Paragraph("<b>Negociacao</b>", body_style), Paragraph("valor_proposto, status, data_proposta", body_style), Paragraph("FKs para <code>Anuncio</code> e <code>User</code> (Comprador). Propostas P2P.", body_style)],
        [Paragraph("<code>core</code>", code_style), Paragraph("<b>Notificacao</b>", body_style), Paragraph("titulo, mensagem, lida, data_criacao", body_style), Paragraph("FK para <code>User</code>. Avisos de propostas e movimentações.", body_style)],
    ]
    models_table = Table(models_data, colWidths=[65, 85, 160, 194])
    models_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#146c43")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#ced4da")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8f9fa")]),
    ]))
    story.append(models_table)

    story.append(Spacer(1, 10))
    story.append(Paragraph("Destaques de Engenharia de Dados:", h2_style))
    story.append(Paragraph("&bull; <b>Auto-relacionamento Genealógico:</b> O modelo <code>Animal</code> possui duas chaves estrangeiras reflexivas para si mesmo (<code>pai</code> e <code>mae</code> com <code>related_name='filhos_pai'</code> e <code>'filhos_mae'</code>), permitindo navegar bidirecionalmente na árvore de parentesco.", bullet_style))
    story.append(Paragraph("&bull; <b>Integridade e Multi-Inquilino (Multi-Tenancy):</b> Cada criador só gerencia e visualiza seus próprios animais e propriedades. A integridade referencial garante que animais não possam ter datas de vacinação anteriores ao seu nascimento ou pais mais jovens que seus filhos.", bullet_style))

    story.append(PageBreak())

    # ====================================================
    # SEÇÃO 3: FUNCIONALIDADES E REGRAS DE NEGÓCIO
    # ====================================================
    story.append(Paragraph("3. Funcionalidades e Regras de Negócio", h1_style))
    
    story.append(Paragraph("A. Ficha Zootécnica e Genealogia (App Rebanho)", h2_style))
    story.append(Paragraph(
        "A tela de detalhes do animal (<code>/rebanho/animais/&lt;id&gt;/</code>) funciona como o prontuário eletrônico completo do exemplar. "
        "Além dos dados biométricos, ela renderiza os pais com links clicáveis, a lista completa de crias/descendentes, "
        "e organiza o histórico em abas dinâmicas com Bootstrap: evolução de pesagens, histórico sanitário de vacinas com alerta de próximas doses, "
        "registros reprodutivos (se for fêmea) e histórico de transferências.",
        body_style
    ))

    story.append(Paragraph("B. Movimentações com Atualização Transacional (App Core)", h2_style))
    story.append(Paragraph(
        "Ao cadastrar uma transferência de animal entre fazendas (<code>/movimentacoes/nova/</code>), o formulário valida obrigatoriamente que a fazenda de origem "
        "seja a localização atual do animal e que o destino seja distinto. O salvamento é executado dentro de uma transação atômica "
        "(<code>transaction.atomic()</code>), que registra o histórico de movimentação e <b>atualiza imediatamente a propriedade atual do animal</b>.",
        body_style
    ))

    story.append(Paragraph("C. Marketplace P2P e Negociações", h2_style))
    story.append(Paragraph(
        "O Marketplace (<code>/marketplace/</code>) é uma vitrine pública de animais disponíveis para venda com filtros por título, raça e valor máximo. "
        "As regras de negociação implementadas incluem:",
        body_style
    ))
    story.append(Paragraph("&bull; Qualquer criador cadastrado (que não seja o vendedor) pode enviar uma contraproposta financeira pelo animal.", bullet_style))
    story.append(Paragraph("&bull; O envio de uma proposta dispara automaticamente uma <b>Notificação</b> no painel do vendedor.", bullet_style))
    story.append(Paragraph("&bull; O vendedor possui botões diretos para <b>Aceitar</b> ou <b>Recusar</b> propostas.", bullet_style))
    story.append(Paragraph("&bull; Ao aceitar uma proposta, o anúncio é automaticamente finalizado (<code>ativo = False</code>), a proposta é marcada como <code>CONCLUIDA</code> e o comprador recebe uma notificação de sucesso.", bullet_style))

    story.append(Paragraph("D. Central de Notificações", h2_style))
    story.append(Paragraph(
        "A navbar superior possui um ícone de sino com contador badge que atualiza em tempo real a quantidade de avisos não lidos através de um <i>Context Processor</i> global. "
        "Na central (<code>/notificacoes/</code>), o criador pode ler os avisos e marcá-los como lidos individualmente ou em lote.",
        body_style
    ))

    story.append(Spacer(1, 10))

    # ====================================================
    # SEÇÃO 4: INTEGRAÇÃO E RECURSOS DE SISTEMAS DISTRIBUÍDOS
    # ====================================================
    story.append(Paragraph("4. Recursos Obrigatórios e Desejáveis de Sistemas Distribuídos", h1_style))
    
    req_box = [
        [Paragraph("<b>Atendimento aos Requisitos da Disciplina (Conforme Ementa)</b>", ParagraphStyle('BH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=primary_color))],
        [Paragraph("<b>1. Autenticação e Recuperação de Senha:</b> Telas de login, cadastro, logout e fluxo completo de reset de senha com geração de token seguro do Django.", body_style)],
        [Paragraph("<b>2. Envio de E-mails (SMTP):</b> Configurado com suporte a servidores SMTP reais e fallback inteligente para depuração via console.", body_style)],
        [Paragraph("<b>3. Banco de Dados Relacional:</b> Suporte nativo e testado para PostgreSQL (via <code>DATABASE_URL</code>) e SQLite para testes locais.", body_style)],
        [Paragraph("<b>4. Validação em Múltiplas Camadas:</b> Validações nos Models e métodos <code>clean()</code> nos ModelForms impedindo pesos negativos, áreas zeradas, datas futuras e duplicidades.", body_style)],
        [Paragraph("<b>5. Humanização:</b> Uso de <code>django.contrib.humanize</code> com filtros <code>intcomma</code> (preços/áreas) e <code>naturaltime</code> (tempos relativos de anúncios e avisos).", body_style)],
        [Paragraph("<b>6. Paginação:</b> Aplicação de <code>Paginator</code> com controles visuais Bootstrap e preservação de querystrings de busca.", body_style)],
        [Paragraph("<b>7. Framework de Mensagens:</b> Alertas dismissíveis do Bootstrap integrados com <code>messages.success</code> e <code>messages.error</code> em todas as ações de escrita.", body_style)],
        [Paragraph("<b>8. [DESEJÁVEL] Consumo de API REST Externa:</b> Widget no Dashboard que consome a API da <i>AwesomeAPI</i> trazendo a cotação ao vivo do Dólar (USD) e Euro (EUR) com variação diária para o agronegócio.", body_style)],
        [Paragraph("<b>9. [DESEJÁVEL] Fornecimento de API REST (Servidor):</b> Três endpoints públicos em JSON expostos para consumo por sistemas externos de outros colegas de turma:<br/>"
                   "&bull; <code>/api/anuncios/</code>: Lista anúncios ativos do marketplace.<br/>"
                   "&bull; <code>/api/animais/</code>: Lista animais cadastrados com raça e localização.<br/>"
                   "&bull; <code>/api/estatisticas/</code>: Totais do plantel e distribuição de raças.", body_style)],
    ]
    req_table = Table(req_box, colWidths=[504])
    req_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8f9fa")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#ced4da")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(req_table)

    story.append(PageBreak())

    # ====================================================
    # SEÇÃO 5: ROTEIRO DE APRESENTAÇÃO ORAL (30 MINUTOS)
    # ====================================================
    story.append(Paragraph("5. Roteiro Sugerido para a Apresentação Oral (Entrega IV)", h1_style))
    story.append(Paragraph(
        "A Entrega IV consiste em uma apresentação com slides (cerca de 30 minutos) e demonstração prática ao vivo (live demo). "
        "Abaixo está o roteiro estruturado para garantir a nota máxima com a banca examinadora:",
        body_style
    ))

    script_data = [
        [Paragraph("<b>Tempo</b>", body_style), Paragraph("<b>Etapa da Apresentação</b>", body_style), Paragraph("<b>O que Falar / Demonstrar</b>", body_style)],
        [
            Paragraph("00 a 05 min", body_style),
            Paragraph("<b>1. Introdução & Contexto</b>", body_style),
            Paragraph("Apresentar a equipe e a motivação: a importância da ovinocultura e caprinocultura no Semiárido e as dificuldades de controle em cadernos de papel e comercialização informal.", body_style)
        ],
        [
            Paragraph("05 a 10 min", body_style),
            Paragraph("<b>2. Arquitetura & Banco de Dados</b>", body_style),
            Paragraph("Mostrar o diagrama dos 9 modelos relacionais. Destacar o auto-relacionamento em <code>Animal</code> para genealogia e a separação modular em <code>rebanho</code> e <code>core</code>.", body_style)
        ],
        [
            Paragraph("10 a 22 min", body_style),
            Paragraph("<b>3. Demonstração Prática (Live Demo)</b>", body_style),
            Paragraph(
                "1. Login com o criador <code>mouraisaque</code>.<br/>"
                "2. Mostrar o <b>Dashboard</b> com os contadores e o widget de cotação do Dólar/Euro (API REST externa).<br/>"
                "3. Abrir a <b>Ficha de um Animal</b>: mostrar genealogia, pesagens e vacinas.<br/>"
                "4. Realizar uma <b>Transferência de Fazenda</b> e mostrar o animal mudando de propriedade.<br/>"
                "5. Abrir uma aba anônima com outro usuário (<code>oliviacamargo</code>), entrar no <b>Marketplace</b> e enviar uma proposta de compra.<br/>"
                "6. Voltar ao vendedor, mostrar o sino de <b>Notificação</b> apitando, abrir a proposta e clicar em <b>Aceitar</b>.<br/>"
                "7. Mostrar o anúncio sendo concluído e a notificação de retorno.",
                body_style
            )
        ],
        [
            Paragraph("22 a 26 min", body_style),
            Paragraph("<b>4. Integrações REST & Deploy</b>", body_style),
            Paragraph("Abrir no navegador os endpoints JSON <code>/api/anuncios/</code> e <code>/api/estatisticas/</code>, explicando como outros sistemas de colegas podem consumir dados do RebanhoTech. Mostrar a configuração para PostgreSQL e WhiteNoise.", body_style)
        ],
        [
            Paragraph("26 a 30 min", body_style),
            Paragraph("<b>5. Conclusão & Perguntas</b>", body_style),
            Paragraph("Resumir os requisitos atendidos (100% dos obrigatórios + desejáveis), destacar os 13 testes unitários aprovados e abrir para perguntas do professor.", body_style)
        ],
    ]
    script_table = Table(script_data, colWidths=[65, 140, 299])
    script_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#146c43")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#ced4da")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8f9fa")]),
    ]))
    story.append(script_table)

    story.append(Spacer(1, 15))
    story.append(Paragraph("Dica de Ouro para a Apresentação:", h2_style))
    story.append(Paragraph(
        "Durante a live demo, mostre o terminal rodando <code>python manage.py test</code> para exibir o resultado <b>OK (13 tests)</b>. "
        "Isso demonstra rigor técnico e qualidade de código, impressionando positivamente o professor!",
        body_style
    ))

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF gerado com sucesso: {filename}")

if __name__ == '__main__':
    build_pdf()
