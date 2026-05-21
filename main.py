import PySimpleGUI as sg
from connection.init_db import inicializar_banco
import os

os.makedirs("database", exist_ok=True)
os.makedirs("relatorios", exist_ok=True)

inicializar_banco()

from services.estoque_service import (
    cadastrar_novo_produto,
    exibir_produtos,
    exibir_produto,
    alterar_estoque,
    excluir_produto
)
from services.auditoria_service import realizar_auditoria
from services.relatorio_service import gerar_relatorio_xlsx
from connection.auditoria_repository import listar_auditorias
from connection.produto_repository import buscar_produto_por_id

sg.theme('DarkBlue3')
sg.set_options(font=('Arial', 10))

def criar_layout_principal():
    layout = [
        [sg.Text('SISTEMA DE GERENCIAMENTO DE ESTOQUE', font=('Arial', 16, 'bold'), text_color='white', justification='center', expand_x=True)],
        [sg.Text('', size=(50, 1))],
        [sg.Button('Cadastrar Produto', size=(20, 2), font=('Arial', 11, 'bold')), 
         sg.Button('Listar Produtos', size=(20, 2), font=('Arial', 11, 'bold'))],
        [sg.Button('Buscar Produto', size=(20, 2), font=('Arial', 11, 'bold')), 
         sg.Button('Atualizar Estoque', size=(20, 2), font=('Arial', 11, 'bold'))],
        [sg.Button('Remover Produto', size=(20, 2), font=('Arial', 11, 'bold')), 
         sg.Button('Realizar Auditoria', size=(20, 2), font=('Arial', 11, 'bold'))],
        [sg.Button('Histórico de Auditorias', size=(20, 2), font=('Arial', 11, 'bold')), 
         sg.Button('Gerar Relatório Excel', size=(20, 2), font=('Arial', 11, 'bold'))],
        [sg.Button('Sair', size=(20, 2), font=('Arial', 11, 'bold'), button_color=('white', 'darkred'))],
    ]
    return layout

def criar_layout_cadastro():
    layout = [
        [sg.Text('CADASTRAR NOVO PRODUTO', font=('Arial', 14, 'bold'))],
        [sg.Text('Nome do Produto:'), sg.InputText(key='nome_produto', size=(30, 1))],
        [sg.Text('SKU:'), sg.InputText(key='sku_produto', size=(30, 1))],
        [sg.Text('Categoria:'), sg.InputText(key='categoria_produto', size=(30, 1))],
        [sg.Button('Cadastrar', size=(15, 1)), sg.Button('Cancelar', size=(15, 1))],
        [sg.Multiline(size=(50, 10), key='output', disabled=True)],
    ]
    return layout

def criar_layout_busca():
    layout = [
        [sg.Text('BUSCAR PRODUTO', font=('Arial', 14, 'bold'))],
        [sg.Text('ID do Produto:'), sg.InputText(key='id_busca', size=(30, 1))],
        [sg.Button('Buscar', size=(15, 1)), sg.Button('Cancelar', size=(15, 1))],
        [sg.Multiline(size=(50, 10), key='output', disabled=True)],
    ]
    return layout

def criar_layout_atualizar():
    layout = [
        [sg.Text('ATUALIZAR ESTOQUE', font=('Arial', 14, 'bold'))],
        [sg.Text('ID do Produto:'), sg.InputText(key='id_atualizar', size=(30, 1))],
        [sg.Text('Novo Estoque:'), sg.InputText(key='novo_estoque', size=(30, 1))],
        [sg.Button('Atualizar', size=(15, 1)), sg.Button('Cancelar', size=(15, 1))],
        [sg.Multiline(size=(50, 10), key='output', disabled=True)],
    ]
    return layout

def criar_layout_remover():
    layout = [
        [sg.Text('REMOVER PRODUTO', font=('Arial', 14, 'bold'))],
        [sg.Text('ID do Produto:'), sg.InputText(key='id_remover', size=(30, 1))],
        [sg.Button('Remover', size=(15, 1)), sg.Button('Cancelar', size=(15, 1))],
        [sg.Multiline(size=(50, 10), key='output', disabled=True)],
    ]
    return layout

def criar_layout_auditoria():
    layout = [
        [sg.Text('REALIZAR AUDITORIA', font=('Arial', 14, 'bold'))],
        [sg.Text('ID do Produto:'), sg.InputText(key='id_auditoria', size=(30, 1))],
        [sg.Text('Estoque Shopee:'), sg.InputText(key='shopee', size=(30, 1))],
        [sg.Text('Estoque Mercado Livre:'), sg.InputText(key='mercado_livre', size=(30, 1))],
        [sg.Text('Estoque Amazon:'), sg.InputText(key='amazon', size=(30, 1))],
        [sg.Button('Realizar Auditoria', size=(15, 1)), sg.Button('Cancelar', size=(15, 1))],
        [sg.Multiline(size=(50, 10), key='output', disabled=True)],
    ]
    return layout

def validar_inteiro(valor):
    try:
        return int(valor)
    except:
        return None

def validar_estoque(valor):
    try:
        val = int(valor)
        return val if val >= 0 else None
    except:
        return None

def main():
    while True:
        window = sg.Window('Sistema de Estoque', criar_layout_principal(), finalize=True, size=(550, 400))
        
        event, values = window.read()
        window.close()
        
        if event == sg.WINDOW_CLOSED or event == 'Sair':
            break
        
        elif event == 'Cadastrar Produto':
            window = sg.Window('Cadastrar Produto', criar_layout_cadastro(), finalize=True, size=(550, 400))
            while True:
                event, values = window.read()
                
                if event == sg.WINDOW_CLOSED or event == 'Cancelar':
                    break
                
                if event == 'Cadastrar':
                    nome = values['nome_produto'].strip()
                    sku = values['sku_produto'].strip()
                    categoria = values['categoria_produto'].strip()
                    
                    output = ""
                    if not nome:
                        output = "❌ Nome inválido."
                    elif not sku:
                        output = "❌ SKU inválido."
                    else:
                        cadastrar_novo_produto(nome, sku, categoria)
                        output = "✅ Produto cadastrado com sucesso!"
                        window['nome_produto'].update('')
                        window['sku_produto'].update('')
                        window['categoria_produto'].update('')
                    
                    window['output'].update(output)
            
            window.close()
        
        elif event == 'Listar Produtos':
            from connection.produto_repository import listar_produtos

            def atualizar_tabela(window, produtos):
                dados = []
                for p in produtos:
                    dados.append([
                        p[0],  # ID
                        p[1],  # Nome
                        p[2],  # SKU
                        p[3],  # Categoria
                        p[4]   # Estoque
                    ])
                window['tabela_produtos'].update(values=dados)

            produtos_list = listar_produtos()
            layout_lista = [
                [sg.Text('LISTA DE PRODUTOS', font=('Arial', 14, 'bold'))],
                [sg.Text('Pesquisar:')],
                [sg.Input(key='pesquisa_produto', size=(40, 1), enable_events=True)],
                [sg.Table(
                    values=[],
                    headings=['ID', 'Nome', 'SKU', 'Categoria', 'Estoque'],
                    auto_size_columns=False,
                    col_widths=[5, 20, 15, 20, 10],
                    justification='center',
                    num_rows=15,
                    key='tabela_produtos',
                    enable_events=True,
                    alternating_row_color='#1e1e1e',
                    selected_row_colors=('white', '#0078D7')
                )],
                [sg.Button('Voltar', size=(15, 1))]
            ]

            window = sg.Window('Listar Produtos', layout_lista, finalize=True, size=(850, 500))
            atualizar_tabela(window, produtos_list)

            while True:
                event, values = window.read()

                if event == sg.WINDOW_CLOSED or event == 'Voltar':
                    break

                if event == 'pesquisa_produto':
                    termo = values['pesquisa_produto'].lower()
                    produtos_filtrados = []
                    for p in produtos_list:
                        nome = str(p[1]).lower()
                        sku = str(p[2]).lower()
                        categoria = str(p[3]).lower()
                        if termo in nome or termo in sku or termo in categoria:
                            produtos_filtrados.append(p)
                    atualizar_tabela(window, produtos_filtrados)

            window.close()

        elif event == 'Buscar Produto':
            window = sg.Window('Buscar Produto', criar_layout_busca(), finalize=True, size=(550, 400))
            while True:
                event, values = window.read()
                
                if event == sg.WINDOW_CLOSED or event == 'Cancelar':
                    break
                
                if event == 'Buscar':
                    id_produto = validar_inteiro(values['id_busca'])
                    
                    if id_produto is None:
                        window['output'].update("❌ ID inválido.")
                    else:
                        produto = buscar_produto_por_id(id_produto)
                        if not produto:
                            window['output'].update("⚠ Produto não encontrado.")
                        else:
                            info = f"""ID: {produto[0]}
Nome: {produto[1]}
SKU: {produto[2]}
Categoria: {produto[3]}
Estoque Oficial: {produto[4]}"""
                            window['output'].update(info)
            
            window.close()
        
        elif event == 'Atualizar Estoque':
            window = sg.Window('Atualizar Estoque', criar_layout_atualizar(), finalize=True, size=(550, 400))
            while True:
                event, values = window.read()
                
                if event == sg.WINDOW_CLOSED or event == 'Cancelar':
                    break
                
                if event == 'Atualizar':
                    id_produto = validar_inteiro(values['id_atualizar'])
                    estoque = validar_estoque(values['novo_estoque'])
                    
                    output = ""
                    if id_produto is None:
                        output = "❌ ID inválido."
                    elif estoque is None:
                        output = "❌ Estoque inválido."
                    else:
                        alterar_estoque(id_produto, estoque)
                        output = "✅ Estoque atualizado com sucesso!"
                        window['id_atualizar'].update('')
                        window['novo_estoque'].update('')
                    
                    window['output'].update(output)
            
            window.close()
        
        elif event == 'Remover Produto':
            window = sg.Window('Remover Produto', criar_layout_remover(), finalize=True, size=(550, 400))
            while True:
                event, values = window.read()
                
                if event == sg.WINDOW_CLOSED or event == 'Cancelar':
                    break
                
                if event == 'Remover':
                    id_produto = validar_inteiro(values['id_remover'])
                    
                    if id_produto is None:
                        window['output'].update("❌ ID inválido.")
                    else:
                        excluir_produto(id_produto)
                        window['output'].update("✅ Produto removido com sucesso!")
                        window['id_remover'].update('')
            
            window.close()
        
        elif event == 'Realizar Auditoria':
            window = sg.Window('Realizar Auditoria', criar_layout_auditoria(), finalize=True, size=(550, 450))
            while True:
                event, values = window.read()
                
                if event == sg.WINDOW_CLOSED or event == 'Cancelar':
                    break
                
                if event == 'Realizar Auditoria':
                    id_produto = validar_inteiro(values['id_auditoria'])
                    shopee = validar_estoque(values['shopee'])
                    ml = validar_estoque(values['mercado_livre'])
                    amazon = validar_estoque(values['amazon'])
                    
                    output = ""
                    if id_produto is None:
                        output = "❌ ID do produto inválido."
                    elif shopee is None or ml is None or amazon is None:
                        output = "❌ Um ou mais estoques inválidos."
                    else:
                        realizar_auditoria(id_produto, shopee, ml, amazon)
                        output = "✅ Auditoria realizada com sucesso!"
                        window['id_auditoria'].update('')
                        window['shopee'].update('')
                        window['mercado_livre'].update('')
                        window['amazon'].update('')
                    
                    window['output'].update(output)
            
            window.close()
        
        elif event == 'Histórico de Auditorias':
            auditorias = listar_auditorias()

            def atualizar_tabela_auditoria(window, auditorias):
                dados = []
                for a in auditorias:
                    dados.append([
                        a[0],  # ID
                        a[1],  # Produto
                        a[2],  # Est. Consolidado
                        a[3],  # Status
                        a[4]   # Data
                    ])
                window['tabela_auditorias'].update(values=dados)

            layout_historico = [
                [sg.Text('HISTÓRICO DE AUDITORIAS', font=('Arial', 14, 'bold'))],
                [sg.Text('Pesquisar:')],
                [sg.Input(key='pesquisa_auditoria', size=(40, 1), enable_events=True)],
                [sg.Table(
                    values=[],
                    headings=['ID', 'Produto', 'Est. Consolidado', 'Status', 'Data'],
                    auto_size_columns=False,
                    col_widths=[5, 20, 15, 15, 15],
                    justification='center',
                    num_rows=15,
                    key='tabela_auditorias',
                    enable_events=True,
                    alternating_row_color='#1e1e1e',
                    selected_row_colors=('white', '#0078D7')
                )],
                [sg.Button('Voltar', size=(15, 1))]
            ]

            window = sg.Window('Histórico de Auditorias', layout_historico, finalize=True, size=(900, 500))
            atualizar_tabela_auditoria(window, auditorias)

            while True:
                event, values = window.read()

                if event == sg.WINDOW_CLOSED or event == 'Voltar':
                    break

                if event == 'pesquisa_auditoria':
                    termo = values['pesquisa_auditoria'].lower()
                    auditorias_filtradas = []
                    for a in auditorias:
                        produto = str(a[1]).lower()
                        status = str(a[3]).lower()
                        data = str(a[4]).lower()
                        if termo in produto or termo in status or termo in data:
                            auditorias_filtradas.append(a)
                    atualizar_tabela_auditoria(window, auditorias_filtradas)

            window.close()
        
        elif event == 'Gerar Relatório Excel':
            layout_relatorio = [
                [sg.Text('GERAR RELATÓRIO EXCEL', font=('Arial', 14, 'bold'))],
                [sg.Multiline(size=(60, 15), key='output_relatorio', disabled=True)],
                [sg.Button('Gerar', size=(15, 1)), sg.Button('Cancelar', size=(15, 1))],
            ]

            window = sg.Window('Gerar Relatório', layout_relatorio, finalize=True, size=(650, 350))

            while True:
                event, values = window.read()

                if event == sg.WINDOW_CLOSED or event == 'Cancelar':
                    break

                if event == 'Gerar':
                    auditorias = listar_auditorias()

                    if not auditorias:
                        window['output_relatorio'].update("⚠ Nenhuma auditoria encontrada!\n\nPara gerar um relatório, você precisa:\n\n1. Cadastrar produtos\n2. Realizar auditorias dos produtos\n\nClique em 'Realizar Auditoria' no menu principal para começar.")
                    else:
                        window['output_relatorio'].update("Gerando relatório...\n")
                        gerar_relatorio_xlsx()
                        window['output_relatorio'].update("✅ Relatório gerado com sucesso!\n\nArquivo salvo em: relatorios/relatorio_auditoria.xlsx")

            window.close()

if __name__ == '__main__':
    main()
