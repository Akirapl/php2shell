FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt app.py ./
RUN pip install --no-cache-dir -r requirements.txt
ENV CHECKER_RESOLVER=system
EXPOSE 8080
# Behind the platform's proxy: trust its X-Forwarded-For (rightmost hop is used for rate limiting)
CMD ["sh","-c","uvicorn app:app --host 0.0.0.0 --port ${PORT:-8080} --no-access-log"]
