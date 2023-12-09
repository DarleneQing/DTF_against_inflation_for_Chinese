FROM jupyter/scipy-notebook

COPY requirements.txt /tmp/

RUN pip install --requirement /tmp/requirements.txt

COPY ./src/Hedge_Against_inflation_Tool.ipynb /home/jovyan/work/