# paper_summary_with_llama

해당 프로젝트는 Llama 3.1 모델을 이용하여 arxiv의 논문을 요약 후, 결과를 슬랙에 전송하는 프로젝트입니다.


## 준비
해당 프로젝트를 실행시키기 위해서는, 아래와 같은 준비가 먼저 필요합니다.

### Llama 3.1 모델 다운로드 
Llama 3.1모델을 클론하여 로컬 머신에 다운로드 합니다. 자세한 사항은 [링크](https://github.com/Debapriya-source/llama-3.1-8B-Instruct) 참고하시면 됩니다. 프로젝트를 Clone하는 것까지만 진행하면 되며, conda 혹은 pip를 이용한 requirements.txt 설치는 생략해도 됩니다.

### Conda 환경 설치
먼저 새로운 conda 환경을 만들고 실행합니다.

해당 문서에서는 python 3.9 버전으로 환경을 만들고 pytorch 2.3.1-cuda 11.8 버전을 설치하였습니다.

```
conda install pytorch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1 pytorch-cuda=11.8 -c pytorch -c nvidia
```

그 이후, 아래의 명령어를 통해 모든 패키지 설치
```
pip install transformers Flask lxml bs4 pandas pre-commit requests slack-sdk
```

그리고 Llama 3.1 문서에 소개되어있던 requirements.txt를 설치(경로는 본인의 디렉토리 구조에 맞게!)
```
conda install --yes --file Meta-Llama-3.1-8B-Instruct/requirements.txt
```
해당 패키지 설치 도중 `huggingface-hub==0.24.2, setuptools==72.0.0, torch==2.4.0`이 없다고 오류를 뱉을 수도 있는데, 이때 requirements.txt를 열어 세 개의 패키지를 주석처리해도 됨. 그 전 단계까지 잘 수행했다면, 세 개는 이미 모두 깔렸을 것이기 때문임.

