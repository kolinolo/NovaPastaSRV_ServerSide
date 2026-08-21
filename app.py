import json
import os
from pathlib  import Path 

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

        tributacao = "Simples Nacional"

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

    if nomeArquivo in os.listdir(f"{nivel}/{tributacao}/Clientes ativos"): raise pastaExistenteError(nomeArquivo)

    Path(f"{nivel}/{tributacao}/Clientes ativos/{nomeArquivo}").mkdir(parents=True)

    nivel = f"{nivel}/{tributacao}/Clientes ativos/{nomeArquivo}"

    for departamento in configs['departamentos'][:3]:

        for mes in meses:
            Path(f"{nivel}/{departamento}/Ano {anoAtual}/{mes}").mkdir(parents=True)
            f"{nivel}/{departamento}/Ano {anoAtual}/{mes}"

            if departamento == "Fiscal":
                for pastaFiscal in pastasFiscal:
                    Path(f"{nivel}/{departamento}/Ano {anoAtual}/{mes}/{pastaFiscal}").mkdir(parents=True)


            elif departamento == "Pessoal":
                for pastaPessoal in pastasPessoal:
                    Path(f"{nivel}/{departamento}/Ano {anoAtual}/{mes}/{pastaPessoal}").mkdir(parents=True)

        if departamento == "Contábil":

            if tributacao == "Simples Nacional":

                Path(f"{nivel}/{departamento}/Ano {anoAtual}/Livro Contábil Autenticado").mkdir(parents=True)


            else:

                Path(f"{nivel}/{departamento}/Ano {anoAtual}/Declarações Anuais").mkdir(parents=True)

            Path(f"{nivel}/{departamento}/Ano {anoAtual}/Fechamento Anual").mkdir(parents=True)

            if contAnterior: Path(f"{nivel}/{departamento}/Contabilidade Anterior").mkdir(parents=True)

            if tributacao != "Simples Nacional":
                Path(f"{nivel}/{departamento}/Ano {anoAtual}/Declarações Anuais/ECD").mkdir(parents=True)
                Path(f"{nivel}/{departamento}/Ano {anoAtual}/Declarações Anuais/ECF").mkdir(parents=True)


        elif departamento == "Fiscal":
            Path(f"{nivel}/{departamento}/Ano {anoAtual}/Declarações Anuais/DIMOB").mkdir(parents=True)
            Path(f"{nivel}/{departamento}/Ano {anoAtual}/Declarações Anuais/DIMED").mkdir(parents=True)
            if contAnterior: Path(f"{nivel}/{departamento}/Contabilidade Anterior").mkdir(parents=True)

            if tributacao == "Simples Nacional":
                Path(f"{nivel}/{departamento}/Ano {anoAtual}/Declarações Anuais/DEFIS").mkdir(parents=True)

        elif departamento == "Pessoal":
            Path(f"{nivel}/{departamento}/Ano {anoAtual}/Declarações Anuais/DIRF").mkdir(parents=True)
            Path(f"{nivel}/{departamento}/Ano {anoAtual}/Declarações Anuais/RAIS").mkdir(parents=True)
            if contAnterior: Path(f"{nivel}/{departamento}/Contabilidade Anterior").mkdir(parents=True)

    departamento = 'Societário'
    nivel = f"{configs['raizPastas']}/{tributacao}/Clientes ativos/{nomeArquivo}/Societário"

    Path(f"{nivel}/CND/{anoAtual}").mkdir(parents=True)
    for mes in meses:
        Path(f"{nivel}/CND/{anoAtual}/{mes}").mkdir(parents=True)
        for cnd in configs['cnds']:
            Path(f"{nivel}/CND/{anoAtual}/{mes}/{cnd}").mkdir(parents=True)

    Path(f"{nivel}/Docs Cadastrais").mkdir(parents=True)
    Path(f"{nivel}/Docs Cadastrais/Procuração").mkdir(parents=True)
    Path(f"{nivel}/Docs Cadastrais/Processos/Abertura").mkdir(parents=True)

    for alvara in configs['alvaras']:
        Path(f"{nivel}/Docs Cadastrais/Alvarás/{anoAtual}/{alvara}").mkdir(parents=True)

    for pastaSocietario in ["Cods e Acesso da Empresa", "Docs CNPJ", "Notificações multas", "Docs sócios",
                            "Termos de Responsabilidade"]:
        Path(f"{nivel}/Docs Cadastrais/{pastaSocietario}").mkdir(parents=True)

    Path(f"{configs['raizPastas']}/{tributacao}/Clientes ativos/{nomeArquivo}/Reuniões").mkdir(parents=True)

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
    uvicorn.run(app, host="0.0.0.0", port=81)
