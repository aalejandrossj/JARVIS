run:
	uvicorn main:app --host 0.0.0.0 --port 8443 --ssl-certfile cert.pem --ssl-keyfile key.pem
