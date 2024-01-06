# MediafileAutoFormatter
파일 및 디렉토리 이름을 원하는 형태로 포매팅합니다.

- source_path : 원본 변환할 미디어 파일이 들어있는 디렉토리 경로
- target_path : 변환된 파일 및 디렉토리가 저장될 경로
- multiple : source_path 내 서로 다른 모든 미디어를 변환하고자 하는 경우 True로 설정
(False라면 source_path가 단일 미디어라고 취급함)

# Environments
```
# Media
MEDIA_EXTENSIONS : 설정된 확장자를 미디어 파일로 인식합니다.

# Localization
SUBTITLE_SUFFIX : 자막 파일의 접미사를 설정합니다.

# Subtitle
CONVERT_SMI_TO_SRT : SMI 파일을 SRT 파일로 변환합니다.
SUBTITLE_EXTENSIONS : 설정된 확장자를 자막 파일로 인식합니다.
SYNC_SUBTITLE_AUTOMATICALLY : 자막 파일의 싱크를 미디어 파일에 맞게 자동으로 조정합니다.

# Season File format
FILENAME_FORMAT : 파일 이름의 포맷을 설정합니다. {{ title }}, {{ season_number }}, {{ episode_number }} 는 반드시 포함되어야 합니다.
SEASON_NUMBER_DIGIT : 시즌 숫자를 포맷할 때 몇자리 수로 할 것인지를 설정합니다. (ex. 2 -> 01, 02, 03, ...)
EPISODE_NUMBER_DIGIT : 에피소드 숫자를 포맷할 때 몇자리 수로 할 것인지를 설정합니다. (ex. 3 -> 001, 002, 003, ...)

# Debug
EXPORT_DEBUG_LOG_FILE : 프로그램 실행 경로에 로그 파일을 남깁니다.
```


# How to run

```
# install requirements
python -m pip install -r .\requirements.txt

# create .env file before run
cp .\env.example .\env

# run
python .\main.py --target_path="YOUR_TARGET_PATH" --multiple=True "YOUR_SOURCE_PATH"
```


## Formating example

### TV Example 1
```
# Before
─ Some title(media folder)
    └ Some media file 1.mp4
    └ Some media file 1.srt
    └ Some media file 2.mp4
    └ Some media file 2.srt
    └ Some media file 3.mp4
    └ Some media file 3.srt

# After
─ Some title(media folder)
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
─ Some title(media folder)
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
─ Some title(media folder)
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

## Metadata (WIP)
미디어 파일의 루트 디렉토리에 metadata.txt 파일을 두어 원하는 형태로 포매팅 할 수 있습니다.

```
{
    "Title": "Titanic",
    "MediaType": "Movie",
    "TMDB_ID": 597
}
```

## TODO
- 원하는 형태로 파일 및 디렉토리 이름 포매팅
- 제목을 TheMovieDB와 비교해서 정확도 향상
- 한 폴더 내에 여러 시즌 미디어가 존재하는 경우, 자동 정리
- mkv 자막 추출 기능 추가 (이미 자막 존재 시 스킵)
