#! /bin/bash

# Script para recuperar e organizar as informações sobre os dados de
# observaçao armazenadas e disponíveis para a assimilação de dados

# @cfbastarz (01/09/2023)

inctime=/opt/inctime/bin/inctime

datai=2023010100
dataf=2023092500

#datai=2023010800
#dataf=2023010800

data=${datai}

mkdir txt csv

while [ ${data} -le ${dataf} ]
do

  echo ${data}

  dataobs=/extra2/XC50_EXTERNAL/${data}/dataout/NCEP
  dataloggsi=/extra2/XC50_SMNA_GSI_dataout_preOper/${data}

  ls -l --full-time ${dataobs} > ./txt/obs_${data}.txt

  if [ -d ${dataloggsi} ]
  then
    if ls ${dataloggsi}/gsiStdout_${data}.runTime-*.log 1> /dev/null 2>&1
    then
      loggsi=$(ls -t1 ${dataloggsi}/gsiStdout_${data}.runTime-*.log | head -1)
    #else
    #  loggsi=${dataloggsi}/gsiStdout_${data}.runTime-NaT.log
    fi
  #else
  #  loggsi=${dataloggsi}/gsiStdout_${data}.runTime-NaT.log
  fi

  # Recupera a hora em que o programa principal do GSI iniciou
  if [ -s ${loggsi} ]
  then
    cat ${loggsi} | grep "STARTING DATE-TIME" | awk -F " " '{print $5}' | awk -F "." '{print $1}' > ./txt/gsilog_${data}.txt
  else
    echo "NaT" > ./txt/gsilog_${data}.txt
  fi

  # Adiciona a data ao horário de início do ciclo
  datafmt=${data:0:4}-${data:4:2}-${data:6:2}
  cat ./txt/gsilog_${data}.txt | awk -v var="${datafmt}" -F " " '{print var" "$0}' > ./csv/gsilog_${data}.csv

  # Remove a primeira linha
  sed -i '1d' ./txt/obs_${data}.txt

  # Formata o arquivo CSV
  cat ./txt/obs_${data}.txt | awk -F ' ' '{print $5","$6" "$7","sprintf("%1.3s", $8)","$9}' > ./csv/obs_${data}.csv
  
  # Remove a primeira linha
  sed -i '1d' ./csv/obs_${data}.csv

  # Remove as linhas com as palavras "OK, index, atmanl, sfcanl, rtgsst, oisst, tmp"
  sed -i '/OK/d' ./csv/obs_${data}.csv
  sed -i '/index/d' ./csv/obs_${data}.csv
  sed -i '/atmanl/d' ./csv/obs_${data}.csv
  sed -i '/sfcanl/d' ./csv/obs_${data}.csv
  sed -i '/rtgsst/d' ./csv/obs_${data}.csv
  sed -i '/oisst/d' ./csv/obs_${data}.csv
  sed -i '/tmp/d' ./csv/obs_${data}.csv
  sed -i '/lftp-pget-status/d' ./csv/obs_${data}.csv
  sed -i '/GDAS_/d' ./csv/obs_${data}.csv
  sed -i '/GBLAV_/d' ./csv/obs_${data}.csv

  # Adiciona uma coluna com a data de início do ciclo de assimilação de dados
  gsi_start=$(cat ./csv/gsilog_${data}.csv)
  cat ./csv/obs_${data}.csv | awk -v var="${gsi_start}" -F " " '{print $0","var}' > ./csv/obs_${data}-2.csv

  data=$(${inctime} ${data} +6hr %y4%m2%d2%h2)

done

# Concatena todos os arquivos CSV
cat ./csv/obs_*-2.csv > ./mon_rec_obs.csv

# Inclui uma coluna para o tipo de arquivo (gdas, gfs)
cat ./mon_rec_obs.csv | awk -F "," '{print $4}' | awk -F "." '{printf ("%s\n", $1)}' > ftype.txt

# Inclui uma coluna para o horário sinótico
cat ./mon_rec_obs.csv | awk -F "," '{print $4}' | awk -F "." '{printf ("%s\n", $2)}' | sed 's/^.\(.*\).$/\1/' > hsin.txt

# Inclui uma coluna para o tipo de observação
cat ./mon_rec_obs.csv | awk -F "," '{print $4}' | awk -F "." '{printf ("%s\n", $3)}' > otype.txt

# Inclui uma coluna para as datas dos arquivos
cat ./mon_rec_obs.csv | awk -F "," '{print $4}' | awk -F "." '{print $NF}' | sed 's/^\(.\{4\}\)\(.\{2\}\)/\1-\2-/' > dates.txt

# Inclui uma coluna com o horário sinótico formatado (será anexado à data no formato YYYY-HH-DD HH:00:00)
cat ./mon_rec_obs.csv | awk -F "," '{print $4}' | awk -F "." '{print $2}' | sed 's/t\([0-9][0-9]\)z/\1:00:00/' > hsin2.txt

# Monta o arquivo dates2.txt colando os arquivos dates.txt e hsin2.txt
paste -d " " dates.txt hsin2.txt > dates2.txt

# Adiciona as colunas ao arquivo final
#paste -d "," mon_rec_obs.csv ftype.txt hsin.txt otype.txt dates2.txt gsilog.csv > mon_rec_obs_final.csv
paste -d "," mon_rec_obs.csv ftype.txt hsin.txt otype.txt dates2.txt > mon_rec_obs_final.csv

# Insere na primeira linha
sed -i '1 i\Tamanho do Download (KB),Data do Download,Fuso Horário,Nome do Arquivo,Início do Ciclo AD,Tipo de Arquivo,Horário Sinótico,Tipo de Observação,Data da Observação' ./mon_rec_obs_final.csv

exit 0
