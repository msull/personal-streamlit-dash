source prod.env.sh
echo $DOMAIN
git pull && docker build . -t personal-streamlit-dash:latest && docker stack deploy -c docker-compose.prod.yaml personaldash && docker service update personaldash_dashboardui --force

docker ps
