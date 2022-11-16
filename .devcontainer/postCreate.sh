pip install --user --upgrade pip
pip install --user -r requirements-dev.txt
nohup bash -c 'gcloud beta emulators datastore start --host-port=127.0.0.1:9090 &'
pre-commit install --install-hooks
