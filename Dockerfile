FROM python
WORKDIR /Bert
VOLUME ["/data"]
RUN pip3 install discord
RUN pip3 install cinemagoer
ADD ./bert.py ./bert.py
ADD ./movieList.py ./movieList.py
ADD ./movieDb.py ./movieDb.py
# -u for unbuffered output
ENTRYPOINT ["python3", "-u", "/Bert/bert.py"]
