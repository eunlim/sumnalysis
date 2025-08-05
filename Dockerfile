# 간단하고 효율적인 단일 스테이지 Dockerfile
FROM python:3.12-slim

WORKDIR /app

# 1. uv 설치에 필요한 기본 도구들을 먼저 설치합니다.
# 'slim' 이미지는 최소한의 도구만 포함하므로, curl, unzip 등이 없을 수 있습니다.
RUN apt-get update && apt-get install -y curl unzip && rm -rf /var/lib/apt/lists/*

# 의존성 파일을 먼저 복사하여 Docker 레이어 캐시를 활용합니다.
COPY pyproject.toml uv.lock ./

# 2. uv 설치와 의존성 동기화를 하나의 RUN 명령어로 합칩니다.
# 이렇게 하면 PATH 문제 없이 설치된 uv를 즉시 사용할 수 있습니다.
# uv의 전체 경로를 명시하여 "command not found" 오류를 확실하게 방지합니다.
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    /root/.local/bin/uv pip install --system --no-cache .

# 3. uv가 설치된 경로를 환경 변수 PATH에 추가합니다.
# 이 ENV 명령어는 이후에 실행될 CMD 명령어에 영향을 줍니다.
ENV PATH="/root/.local/bin:$PATH"

# 4. 나머지 소스 코드를 복사합니다.
COPY . .

CMD ["uv", "run", "app.py"]