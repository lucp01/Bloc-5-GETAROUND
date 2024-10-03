docker run -it\
 -v "$(pwd):/home/app"\
 -e MLFLOW_TRACKING_URI=https://image-luc-getaround-mlflow-ttt-9788c6e43ce7.herokuapp.com/\
 -e AWS_ACCESS_KEY_ID=\
 -e AWS_SECRET_ACCESS_KEY=\
 -e BACKEND_STORE_URI=\
 -e ARTIFACT_ROOT=s3://mlflow-bucket-luc/mlflow-demo-artefact-luc/\
 pricing_luc python train.py