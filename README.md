# MediafileAutoFormatter
파일 및 디렉토리 이름을 원하는 형태로 포매팅합니다.

## Directory structure

### Movie & TV
```
─ media root folder
    └ media files
    └ subtitle.zip or subtitle folder

─ media root folder
    └ media folder
        └ media files
        └ subtitle.zip or subtitle folder

─ media root folder
    └ media folder
        └ media files
    └ subtitle.zip or subtitle folder
```


### TV (when contains season)

```
─ media root folder
    └ season folder
        └ media files
        └ subtitle.zip or subtitle folder

─ media root folder
    └ season folder
        └ media folder
            └ media files
            └ subtitle.zip or subtitle folder

─ media root folder
    └ season folder
        └ media folder
            └ media files
        └ subtitle.zip or subtitle folder
```

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
2. 제목을 TheMovieDB와 비교해서 정확도 향상
