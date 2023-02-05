FROM python
WORKDIR /Bert
VOLUME ["/data"]
RUN pip3 install discord
RUN pip3 install cinemagoer
RUN pip3 install mysql-connector-python
ADD ./bert.py ./bert.py
ADD ./movieList.py ./movieList.py
ADD ./movieDb.py ./movieDb.py
ENTRYPOINT ["python3", "/Bert/bert.py"]
