FROM python:3.13-bookworm

RUN apt-get update && \
    apt-get dist-upgrade -y && \
    apt-get install -y tini

COPY dist/*.whl /tmp/mrfc/
RUN pip install /tmp/mrfc/*.whl

ENTRYPOINT ["/usr/bin/tini", "--"]

CMD [ "uvicorn", "--port", "8000", "--host", "0.0.0.0", "mr_fat_controller.server:app" ]
