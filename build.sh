#!/bin/bash
docker stop bert
docker rm bert
docker build ./ -t bert
source ./bert_env.sh
docker run -v bert-data:/data --name bert -d bert -t $BERT_DISCORD_KEY
