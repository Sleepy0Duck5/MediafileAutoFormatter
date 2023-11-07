# MediafileAutoFormatter
파일 및 디렉토리 이름을 원하는 형태로 포매팅합니다.

- source_path : 원본 변환할 미디어 파일이 들어있는 디렉토리 경로
- target_path : 변환된 파일 및 디렉토리가 저장될 경로
- multiple : source_path 내 서로 다른 모든 미디어를 변환하고자 하는 경우 True로 설정
(False라면 source_path가 단일 미디어라고 취급함)

```
# Create .env file before run
python .\main.py --target_path="YOUR_TARGET_PATH" --multiple=True "YOUR_SOURCE_PATH"
```

## Directory structure

### Movie & TV
```
# Set multiple option to True
─ source folder (= source_path)
    └ media folder 1
        └ media files
        └ subtitle.zip or subtitle folder

    └ media folder 2
        └ folder
            └ media files
            └ subtitle.zip or subtitle folder

    └ media folder 3
        └ folder
            └ media files
        └ subtitle.zip or subtitle folder

# Set multiple option to False
- media folder 1 (= source_path)
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


## Formating example

### TV Example 1
```
# Before
─ Some title(root folder)
    └ Some media file 1.mp4
    └ Some media file 1.srt
    └ Some media file 2.mp4
    └ Some media file 2.srt
    └ Some media file 3.mp4
    └ Some media file 3.srt

# After
─ Some title(root folder)
    └ Season 1
        └ Some title - S01E01.mp4
        └ Some title - S01E01.ko.srt
        └ Some title - S01E02.mp4
        └ Some title - S01E02.ko.srt
        └ Some title - S01E03.mp4
        └ Some title - S01E03.ko.srt
```

### TV Example 2 : Multiple season
```
# Before
─ Some title(root folder)
    └ Season 1
        └ Some media file 1.mp4
        └ Some media file 1.srt
        └ Some media file 2.mp4
        └ Some media file 2.srt
    └ Season 2
        └ Some media file 3.mp4
        └ Some media file 3.srt
        └ Some media file 4.mp4
        └ Some media file 4.srt

# After
─ Some title(root folder)
    └ Season 1
        └ Some title - S01E01.mp4
        └ Some title - S01E01.ko.srt
        └ Some title - S01E02.mp4
        └ Some title - S01E02.ko.srt
    └ Season 2
        └ Some title - S01E03.mp4
        └ Some title - S01E03.ko.srt
        └ Some title - S01E04.mp4
        └ Some title - S01E04.ko.srt
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
