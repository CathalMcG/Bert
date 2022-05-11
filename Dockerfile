FROM python
WORKDIR /Bert
VOLUME ["/data"]
RUN pip3 install discord
RUN pip3 install IMDbPY
ADD ./bert.py ./bert.py
ADD ./movieList.py ./movieList.py
ENTRYPOINT ["python3", "/Bert/karl.py"]
