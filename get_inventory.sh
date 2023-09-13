#! /bin/bash

# @cfbastarz (01/09/2023)

inctime=/opt/inctime/bin/inctime

datai=2023010100
dataf=2023091300

data=${datai}

mkdir txt csv

while [ ${data} -le ${dataf} ]
do

  echo ${data}

  dataobs=/extra2/XC50_EXTERNAL/${data}/dataout/NCEP

  ls -l --full-time ${dataobs} > ./txt/obs_${data}.txt

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

  data=$(${inctime} ${data} +6hr %y4%m2%d2%h2)

done

# Concatena todos os arquivos CSV
cat ./csv/*.csv > ./mon_rec_obs.csv

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
paste -d "," mon_rec_obs.csv ftype.txt hsin.txt otype.txt dates2.txt > mon_rec_obs_final.csv

# Insere na primeira linha
sed -i '1 i\Tamanho do Download (KB),Data do Download,Fuso Horário,Nome do Arquivo,Tipo de Arquivo,Horário Sinótico,Tipo de Observação,Data da Observação' ./mon_rec_obs_final.csv

exit 0
