import json
import os
from os import makedirs

from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()

# Habilita CORS para permitir que JS no navegador acesse a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ou especifique a origem do front-end
    allow_credentials=False,
    allow_methods=["POST"],
    allow_headers=["*"],
)



meses = [f'0{m}'[-2:] for m in range(1, 13)]

with open("configs.json", "r", encoding="utf-8") as file: configs = json.load(file)



class npRequest (BaseModel):

    nome: str
    tributacao: str
    contabilidadeA: bool





@app.post('/novaPasta')
def NovaPasta (novaPasta:npRequest):

    """ Cria uma pasta no servidor conforme os parâmetros do endpoin  """

    if novaPasta.tributacao == "Lucro Real":

        tributacao = "Lucro Real"

        pastasFiscal = configs['fiscal']['presumidoReal']
        pastasContabil = configs['contabil']['simples']
        pastasPessoal = configs['pessoal']['simples']

    elif novaPasta.tributacao == "Lucro Presumido":

        tributacao = "Lucro Presumido"

        pastasFiscal = configs['fiscal']['presumidoReal']
        pastasContabil = configs['contabil']['simples']
        pastasPessoal = configs['pessoal']['simples']

    elif novaPasta.tributacao == 'Simples Nacional':

        tributacao = "Simplse Nacional"

        pastasFiscal = configs['fiscal']['simples']
        pastasContabil = configs['contabil']['simples']
        pastasPessoal = configs['pessoal']['simples']

    else:
        raise TributError(novaPasta.tributacao)

    #_______________________________________________________________

    nivel = configs['raizPastas']
    anoAtual = configs['ano']

    nomeArquivo = novaPasta.nome
    contAnterior = novaPasta.contabilidadeA

    if nomeArquivo in os.listdir(f"{nivel}\\{tributacao}\\Clientes ativos"): raise pastaExistenteError(nomeArquivo)

    makedirs(f"{nivel}\\{tributacao}\\Clientes ativos\\{nomeArquivo}")

    nivel = f"{nivel}\\{tributacao}\\Clientes ativos\\{nomeArquivo}"

    for departamento in configs['departamentos'][:3]:

        for mes in meses:
            makedirs(f"{nivel}\\{departamento}\\Ano {anoAtual}\\{mes}")
            f"{nivel}\\{departamento}\\Ano {anoAtual}\\{mes}"

            if departamento == "Fiscal":
                for pastaFiscal in pastasFiscal:
                    makedirs(f"{nivel}\\{departamento}\\Ano {anoAtual}\\{mes}\\{pastaFiscal}")


            elif departamento == "Pessoal":
                for pastaPessoal in pastasPessoal:
                    makedirs(f"{nivel}\\{departamento}\\Ano {anoAtual}\\{mes}\\{pastaPessoal}")

        if departamento == "Contábil":

            if tributacao == "Simples Nacional":

                makedirs(f"{nivel}\\{departamento}\\Ano {anoAtual}\\Livro Contábil Autenticado")


            else:

                makedirs(f"{nivel}\\{departamento}\\Ano {anoAtual}\\Declarações Anuais")

            makedirs(f"{nivel}\\{departamento}\\Ano {anoAtual}\\Fechamento Anual")

            if contAnterior: makedirs(f"{nivel}\\{departamento}\\Contabilidade Anterior")

            if tributacao != "Simples Nacional":
                makedirs(f"{nivel}\\{departamento}\\Ano {anoAtual}\\Declarações Anuais\\ECD")
                makedirs(f"{nivel}\\{departamento}\\Ano {anoAtual}\\Declarações Anuais\\ECF")


        elif departamento == "Fiscal":
            makedirs(f"{nivel}\\{departamento}\\Ano {anoAtual}\\Declarações Anuais\\DIMOB")
            makedirs(f"{nivel}\\{departamento}\\Ano {anoAtual}\\Declarações Anuais\\DIMED")
            if contAnterior: makedirs(f"{nivel}\\{departamento}\\Contabilidade Anterior")

            if tributacao == "Simples Nacional":
                makedirs(f"{nivel}\\{departamento}\\Ano {anoAtual}\\Declarações Anuais\\DEFIS")

        elif departamento == "Pessoal":
            makedirs(f"{nivel}\\{departamento}\\Ano {anoAtual}\\Declarações Anuais\\DIRF")
            makedirs(f"{nivel}\\{departamento}\\Ano {anoAtual}\\Declarações Anuais\\RAIS")
            if contAnterior: makedirs(f"{nivel}\\{departamento}\\Contabilidade Anterior")

    departamento = 'Societário'
    nivel = f"{configs['raizPastas']}\\{tributacao}\\Clientes ativos\\{nomeArquivo}\\Societário"

    makedirs(f"{nivel}\\CND\\{anoAtual}")
    for mes in meses:
        makedirs(f"{nivel}\\CND\\{anoAtual}\\{mes}")
        for cnd in configs['cnds']:
            makedirs(f"{nivel}\\CND\\{anoAtual}\\{mes}\\{cnd}")

    makedirs(f"{nivel}\\Docs Cadastrais")
    makedirs(f"{nivel}\\Docs Cadastrais\\Procuração")
    makedirs(f"{nivel}\\Docs Cadastrais\\Processos\\Abertura")

    for alvara in configs['alvaras']:
        makedirs(f"{nivel}\\Docs Cadastrais\\Alvarás\\{anoAtual}\\{alvara}")

    for pastaSocietario in ["Cods e Acesso da Empresa", "Docs CNPJ", "Notificações multas", "Docs sócios",
                            "Termos de Responsabilidade"]:
        makedirs(f"{nivel}\\Docs Cadastrais\\{pastaSocietario}")

    makedirs(f"{configs['raizPastas']}\\{tributacao}\\Clientes ativos\\{nomeArquivo}\\Reuniões")

    return 200

def acls():
    pass



class TributError(Exception):

    def __init__(self, tribut):


        self.tribut = tribut

        print(f'{tribut} Inválido')

    def __repr__(self):
        return f'{self.tribut} Inválido'

    pass

class pastaExistenteError(Exception):

    def __init__(self, pasta):


        self.pasta = pasta

        print(f'{pasta} Já Existe no servidor')

    def __repr__(self):
        return f'{self.pasta} Já Existe no servidor'

    pass




if __name__ == "__main__":  # Caso seja a primeira função chamada, executa o servidor com uvicorn na porta 80000
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
