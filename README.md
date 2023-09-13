# SMNA-Dashboard-ArmObs

<a target="_blank" href="https://colab.research.google.com/github/GAD-DIMNT-CPTEC/SMNA-Dashboard-ArmObs/blob/main/SMNA-Dashboard-ArmObs.ipynb">
  <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
</a>

Dashboard para a visualização do espaço utilizado pelos arquivos de observações disponíveis para a utilização com o SMNA. São fornecidos os seguintes artefatos:

1. `get_inventory.sh`: script Bash para construir um arquivo CSV para exploração no dashboard;
2. `SMNA-Dashboard-ArmObs.ipynb`: notebook com a implementação do dashboard.

## Uso

Para a utilização local dos notebooks, recomenda-se a utilização do arquivo de ambiente `environment.yml` para a criação do ambiente `SMNA` com os pacotes necessários para a utilização do dashboard. Para criar o ambiente, utilize o comando a seguir:

```
conda env create -f environment.yml
```

Os notebooks fornecidos são utilizados na ordem apresentada acima. Se o repositório for baixado para teste, então pode-se utilizar apenas o notebook `SMNA-Dashboard.ipynb`, da seguinte forma:

```
panel serve SMNA-Dashboard-ArmObs.ipynb --autoreload --show
```

O comando acima, abre diretamente a interface do dashboard no navegador. Para abrir o conteúdo do notebook (incluindo o notebook `SMNA-Dashboard_load_files_create_dataframe_save.ipynb`), execute o comando:

```
jupyter-notebook SMNA-Dashboard-ArmObs.ipynb
```

## Informações

As informações apresentadas não representam quantidades ou tipos de dados envolvidos ou utiizados no processo de assimilação de dados, mas apenas o espaço em disco utilizado por estes. As informações mais importantes que podem ser obtidas com este dashboard são o espaço em disco total utilizado por diferentes tipos de observações, separadas por horário sinótico, período e tipo de dados.
 
**Nota:** Se o slider que permite ajustar o período a ser visualizado não atualizar a tabela por completo (e.g., o slider está ajustado até a data 13 de Setembro, mas a tabela mostra resultados apenas até o dia 4 de Setembro), pode ser um indicativo de que os arquivos de observação não se encontram no disco verificado. 
