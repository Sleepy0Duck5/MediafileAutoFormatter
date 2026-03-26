# MediafileAutoFormatter
파일 및 디렉토리 이름을 원하는 형태로 포매팅합니다.

- source_path : 원본 변환할 미디어 파일이 들어있는 디렉토리 경로
- target_path : 변환된 파일 및 디렉토리가 저장될 경로
- multiple : source_path 내 서로 다른 모든 미디어를 변환하고자 하는 경우 True로 설정 (optional)
- mkv_audio_language : mkv 파일의 기본 오디오 언어를 변경하고자 하는 경우 원하는 언어로 설정 [ISO 639-2] (e.g. kor) (optional)
(False라면 source_path가 단일 미디어라고 취급함)

# Environments
```
# Media
MEDIA_EXTENSIONS : 설정된 확장자를 미디어 파일로 인식합니다.

# Localization
SUBTITLE_SUFFIX : 자막 파일의 접미사를 설정합니다.
MKV_SUBTITLE_EXTRACTION_LANGUAGE : MKV 파일에서 자막을 추출할 때, 어떤 언어의 자막을 추출할지 결정합니다. ISO 639-2 언어 코드로 설정이 필요하고, mkvtoolnix가 설치되어 있어야 합니다.

# Subtitle
CONVERT_SMI : SMI 파일을 다른 확장자로 변환합니다.
CONVERT_SMI_EXTENSION : SMI 파일을 어떤 확장자로 변환할지 결정합니다. CONVERT_SMI 옵션이 True 일 때 동작합니다. (ex. srt, ass)
SUBTITLE_EXTENSIONS : 설정된 확장자를 자막 파일로 인식합니다.

# Translation (llm-subtrans 기반 LLM 번역)
MKV_SUBTITLE_FALLBACK_LANGUAGE : 추출을 시도할 대체 언어를 리스트 형식으로 순서대로 설정합니다 (예: '["jpn", "eng"]').
ENABLE_SUBTITLE_TRANSLATION : 폴백 언어로 추출된 자막을 자동으로 번역할지 여부를 설정합니다 (True/False).
TRANSLATION_SERVER_ADDRESS : OpenAI API와 규격이 호환되는 LLM 서버 주소를 입력합니다 (ex. http://localhost:11434).
TRANSLATION_ENDPOINT : API 엔드포인트 경로입니다 (ex. /v1/chat/completions).
TRANSLATION_API_KEY : LLM 서버 API 호출에 필요한 키입니다. 로컬 서버일 경우 빈 값일 수 있습니다.
TRANSLATION_MODEL : 번역에 사용할 LLM 모델의 이름입니다 (ex. gpt-4o-mini).

# Season File format
FILENAME_FORMAT : 파일 이름의 포맷을 설정합니다. {{ title }}, {{ season_number }}, {{ episode_number }} 는 반드시 포함되어야 합니다.
SEASON_NUMBER_DIGIT : 시즌 숫자를 포맷할 때 몇자리 수로 할 것인지를 설정합니다. (ex. 2 -> 01, 02, 03, ...)
EPISODE_NUMBER_DIGIT : 에피소드 숫자를 포맷할 때 몇자리 수로 할 것인지를 설정합니다. (ex. 3 -> 001, 002, 003, ...)

# Debug
EXPORT_DEBUG_LOG_FILE : 프로그램 실행 경로에 로그 파일을 남깁니다.
```

## 자막 개별 추출 및 번역 (Fallback 지원)
미디어 폴더 내에 이미 외부 자막 파일이 일부 존재하더라도, 매칭되는 자막이 없는 **각 개별 영상(MKV)마다 누락 여부를 확인하여 내부 자막을 추출**합니다.
1. `MKV_SUBTITLE_EXTRACTION_LANGUAGE`로 설정된 주 언어(예: 한국어) 트랙을 우선적으로 찾아 추출합니다.
2. 발견되지 않을 경우, `MKV_SUBTITLE_FALLBACK_LANGUAGE`로 설정된 백업 언어(예: 영어) 트랙을 찾아 추출합니다.
3. `ENABLE_SUBTITLE_TRANSLATION`이 `True`일 경우, 추출된 폴백 자막을 지정된 LLM 모델(`llm-subtrans` 사용)을 거쳐 주 언어로 자동 번역하여 함께 저장합니다.

# How to run

```
# install uv if not installed
python -m pip install uv

# install requirements
uv sync

# (optional) install mkvtoolnix for mkv subtitle extraction
sudo apt install mkvtoolnix

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
