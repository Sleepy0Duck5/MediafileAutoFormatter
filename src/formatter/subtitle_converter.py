import os
import re
import codecs
import chardet
import tempfile
from abc import ABCMeta
from typing import List

from src.model.file import File
from src.constants import FileType
from src.env_configs import EnvConfigs

# Source code based on ncianeo/smi2srt (https://github.com/ncianeo/smi2srt)
# License of this code inherits the original repo's license. (g6123, ncianeo)


def trunc_suffix_from_file_name(file_name: str) -> str:
    splited = file_name.split(".")

    if len(splited) <= 1:
        return file_name

    suffix = splited[-1]

    if len(suffix) == 2 and re.compile("[^0-9]+").match(suffix):
        return file_name[:-3]
    return file_name


class SubtitleConverter(metaclass=ABCMeta):
    def __init__(self, env_configs: EnvConfigs) -> None:
        self._env_configs = env_configs

    def convert_smi_to_srt(self, file: File) -> List[File]:
        raise NotImplementedError


class GeneralSubtitleConverter(SubtitleConverter):
    def convert_smi_to_srt(self, file: File) -> List[File]:
        with open(file.get_absolute_path(), "rb") as smi_file:
            smi_raw = smi_file.read()
            encoding = chardet.detect(smi_raw[: min(len(smi_raw), 40000)])
            encoding = encoding["encoding"]

        if not encoding:
            encoding = "utf-8"
        smi = smi_raw.decode(encoding)

        langs, data = self._parse(smi)

        converted_files = []

        for lang in langs:
            if len(langs) > 1:
                lang_code = lang.replace("CC", "")
            else:
                lang_code = self._env_configs._SUBTITLE_SUFFIX

            lang_suffix = "." + (
                lang_code.lower()
                if len(lang_code) == 2
                else lang_code[:2].lower() + "_" + lang_code[2:].upper()
            )

            file_name = trunc_suffix_from_file_name(file_name=file.get_title())

            converted_file_name = file_name + lang_suffix + ".srt"
            converted_file_path = os.path.join(tempfile.mkdtemp(), converted_file_name)

            with codecs.open(
                converted_file_path,
                "w",
                encoding="utf-8",
            ) as srt_file:
                srt_file.write(self._convert(data, lang))

            converted_files.append(
                File(absolute_path=converted_file_path, file_type=FileType.SUBTITLE)
            )

        if len(converted_files) <= 0:
            raise Exception(
                "Failed to convert smi subtitle into srt : no converted_files"
            )

        return converted_files

    def _parse(self, smi):
        def get_languages():
            pattern = re.compile(r"<p class=(\w+)>", flags=re.I)
            langs = list(sorted(set(pattern.findall(smi))))
            return langs

        def remove_tag(matchobj):
            matchtag = matchobj.group().lower()
            keep_tags = ["font", "b", "i", "u"]
            for keep_tag in keep_tags:
                if keep_tag in matchtag:
                    return matchtag
            return ""

        def parse_p(item: str):
            pattern = re.compile(r"<p class=(\w+)>(.+)", flags=re.I | re.DOTALL)
            parsed = {}
            for match in pattern.finditer(item):
                lang = match.group(1)
                content = match.group(2)
                content = content.replace("\r", "")
                content = content.replace("\n", "")
                content = re.sub("<br ?/?>", "\n", content, flags=re.I)
                content = re.sub("<[^>]+>", remove_tag, content)
                parsed[lang] = content
            return parsed

        data = []
        try:
            pattern = re.compile(r"<sync (start=\d+)\s?(end=\d+)?>", flags=re.I | re.S)
            start_end_content = pattern.split(smi)[1:]
            start = start_end_content[::3]
            end = start_end_content[1::3]
            content = start_end_content[2::3]
            for s, e, c in zip(start, end, content):
                datum = {}
                datum["start"] = int(s.split("=")[1])
                datum["end"] = int(e.split("=")[1]) if e is not None else None
                datum["content"] = parse_p(c)

                # remove &nbsp;
                for key in datum["content"].keys():
                    datum["content"][key] = datum["content"][key].replace("&nbsp;", " ")
                data.append(datum)
            return get_languages(), data
        except Exception as e:
            print("Conversion ERROR: maybe this file is not supported.")

        return get_languages(), data

    def _convert(self, data, lang):  # written by ncianeo
        def ms_to_ts(time):
            time = int(time)
            ms = time % 1000
            s = int(time / 1000) % 60
            m = int(time / 1000 / 60) % 60
            h = int(time / 1000 / 60 / 60)
            return (h, m, s, ms)

        srt = ""
        sub_nb = 1
        for i in range(len(data) - 1):
            try:
                if i > 0:
                    if data[i]["start"] < data[i - 1]["start"]:
                        continue
                if data[i]["content"][lang] != "&nbsp;":
                    srt += str(sub_nb) + "\n"
                    sub_nb += 1
                    if data[i]["end"] is not None:
                        srt += (
                            "%02d:%02d:%02d,%03d" % ms_to_ts(data[i]["start"])
                            + " --> "
                            + "%02d:%02d:%02d,%03d\n" % ms_to_ts(data[i]["end"])
                        )
                    else:
                        if int(data[i + 1]["start"]) > int(data[i]["start"]):
                            srt += (
                                "%02d:%02d:%02d,%03d" % ms_to_ts(data[i]["start"])
                                + " --> "
                                + "%02d:%02d:%02d,%03d\n"
                                % ms_to_ts(data[i + 1]["start"])
                            )
                        else:
                            srt += (
                                "%02d:%02d:%02d,%03d" % ms_to_ts(data[i]["start"])
                                + " --> "
                                + "%02d:%02d:%02d,%03d\n"
                                % ms_to_ts(int(data[i]["start"]) + 1000)
                            )
                    srt += data[i]["content"][lang] + "\n\n"
            except:
                continue
        return srt
