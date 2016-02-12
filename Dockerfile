FROM python:3.4

COPY requirements.txt /fmtasks/
COPY fmtasks.py /fmtasks/

WORKDIR /fmtasks

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "fmtasks.py"]
