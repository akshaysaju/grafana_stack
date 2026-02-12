docker compose down -v

docker compose up -d --remove-orphans

python ./generate_data.py -n 25 -i 1

echo "Data generation complete."
echo "Open Grafana at http://localhost:3000"
