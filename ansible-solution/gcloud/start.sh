gcloud auth activate-service-account --key-file ~/.gcp.json
gcloud compute instances start node2 --zone us-central1-c
gcloud compute instances start node1 --zone us-central1-c
