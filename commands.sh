gcloud init
gcloud info
gcloud auth login
glcoud auth list
gcloud components install app-engine-python-extras
gcloud config configurations list
gcloud config set project [PROJECT]
gcloud config list
pip install -t lib -r requirements.txt
dev_appserver.py app.yaml
gcloud app deploy
gcloud app logs tail -s default
python lib/endpoints/endpointscfg.py get_openapi_spec main.EchoApi --hostname project20180407.appspot.com
gcloud endpoints deploy echov1openapi.json
gcloud endpoints configs list --service=project20180407.appspot.com
