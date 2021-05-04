FROM python:3-slim
# FROM python:2.7-slim
#ENV http_proxy web-proxy.boi.hp.com:8080
#ENV https_proxy web-proxy.boi.hp.com:8080
WORKDIR /app
COPY . /app
RUN pip install --trusted-host pypi.python.org -r requirements.txt
#RUN pip install --trusted-host pypi.python.org --proxy http://web-proxy.boi.hp.com:8080 -r requirements.txt
EXPOSE 80
CMD ["python", "app.py"]
