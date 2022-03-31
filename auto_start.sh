docker rm -f super-binance
docker rmi -f binance_project
docker build -t binance_project .
docker run --name super-binance -dp 12000:12000 binance_project