# RUN
you can run directed:
```shell
pip install rasa==3.0.3
pip install -r requirements.txt
rasa run actions
```
or simple way by docker:
```shell
docker build -t rasa_action_ep .
docker run -d -p 5055:5055 --mount type=bind,source=$(pwd)/actions,target=/app/actions rasa_action_ep
```

# action_endpoint
```shell
http://127.0.0.1:5055/webhook
```
