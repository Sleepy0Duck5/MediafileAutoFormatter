# MediafileAutoFormatter
파일 및 디렉토리 이름을 원하는 형태로 포매팅합니다.

## Metadata (WIP)
미디어 파일의 루트 디렉토리에 metadata.txt 파일을 두어 원하는 형태로 포매팅 할 수 있습니다.

```
{
    "Title": "Titanic",
    "MediaType": "Movie",
    "TMDB_ID": 597
}
```

## Requirements

```
python -m pip install -r .\requirements.txt
```

## TODO
1. 원하는 형태로 파일 및 디렉토리 이름 포매팅
2. 원본 파일 및 디렉토리 이름 백업
3. 특정 경로 감시 후 자동 실행
4. smi -> srt 변환
5. 디렉토리 이동
6. 시즌별 구분
7. 제목을 TheMovieDB와 비교해서 정확도 향상
