# Module audio_uploader.py


bilibili_api.audio_uploader

音频上传


``` python
from bilibili_api import audio_uploader
```

- [class AudioUploader()](#class-AudioUploader)
  - [def \_\_init\_\_()](#def-\_\_init\_\_)
  - [async def abort()](#async-def-abort)
  - [async def start()](#async-def-start)
- [class AudioUploaderEvents()](#class-AudioUploaderEvents)
- [class AuthorInfo()](#class-AuthorInfo)
- [class CompilationCategories()](#class-CompilationCategories)
  - [class AudioType()](#class-AudioType)
  - [class ContentType()](#class-ContentType)
  - [class CreationType()](#class-CreationType)
  - [class Language()](#class-Language)
  - [class SongType()](#class-SongType)
  - [class Style()](#class-Style)
  - [class Theme()](#class-Theme)
- [class SongCategories()](#class-SongCategories)
  - [class AudioType()](#class-AudioType)
  - [class ContentType()](#class-ContentType)
  - [class CreationType()](#class-CreationType)
  - [class Language()](#class-Language)
  - [class SongType()](#class-SongType)
  - [class Style()](#class-Style)
  - [class Theme()](#class-Theme)
- [class SongMeta()](#class-SongMeta)
- [async def get\_upinfo()](#async-def-get\_upinfo)
- [async def upload\_cover()](#async-def-upload\_cover)
- [async def upload\_lrc()](#async-def-upload\_lrc)

---

## class AudioUploader()

**Extend: bilibili_api.utils.AsyncEvent.AsyncEvent**

音频上传




### def \_\_init\_\_()

初始化


| name | type | description |
| - | - | - |
| `path` | `str` | 文件路径 |
| `meta` | `AudioMeta` | 元数据 |
| `credential` | `Credential` | 账号信息 |


### async def abort()

中断更改






### async def start()

开始上传






---

## class AudioUploaderEvents()

**Extend: enum.Enum**

上传事件枚举

Events:
+ PREUPLOAD  获取上传信息
+ PREUPLOAD_FAILED  获取上传信息失败
+ PRE_CHUNK  上传分块前
+ AFTER_CHUNK  上传分块后
+ CHUNK_FAILED  区块上传失败
+ PRE_COVER  上传封面前
+ AFTER_COVER  上传封面后
+ COVER_FAILED  上传封面失败
+ PRE_SUBMIT  提交音频前
+ SUBMIT_FAILED  提交音频失败
+ AFTER_SUBMIT  提交音频后
+ COMPLETED  完成上传
+ ABORTED  用户中止
+ FAILED  上传失败




---

**@dataclasses.dataclass** 

## class AuthorInfo()

AuthorInfo(name: str, uid: int = 0)



---

## class CompilationCategories()

专辑分类




### class AudioType()

**Extend: enum.Enum**

声音类型

+ RADIO_DRAMA: 广播剧
+ AUDIO_STORY: 有声故事
+ ASMR: ASMR
+ OTHER: 其他




### class ContentType()

**Extend: enum.Enum**

内容类型

+ MUSIC: 音乐
+ AUDIO_PROGRAM: 有声节目




### class CreationType()

**Extend: enum.Enum**

创作类型

+ ORIGINAL: 原创
+ COVER: 翻唱/翻奏
+ REMIX: 改编/remix




### class Language()

**Extend: enum.Enum**

语种

+ CHINESE: 中文
+ JAPANESE: 日语
+ ENGLISH: 英语
+ KOREAN: 韩语
+ CANTONESE: 粤语
+ OTHER_LANGUAGES: 其他语种




### class SongType()

**Extend: enum.Enum**

声音类型

+ HUMAN_SINGING: 人声演唱
+ VOCALOID_SINGER: VOCALOID歌手
+ HUMAN_KICHUKU: 人力鬼畜
+ PURE_MUSIC: 纯音乐




### class Style()

**Extend: enum.Enum**

风格

+ POP: 流行
+ ANCIENT_STYLE: 古风
+ ROCK: 摇滚
+ FOLK_SONG: 民谣
+ ELECTRONIC: 电子
+ DANCE_MUSIC: 舞曲
+ RAP: 说唱
+ LIGHT_MUSIC: 轻音乐
+ A_CAPPELLA: 阿卡贝拉
+ JAZZ: 爵士
+ COUNTRY_MUSIC: 乡村
+ R_AND_B: R&B/Soul
+ CLASSICAL: 古典
+ CLASSICAL: 古典
+ ETHNIC: 民族
+ BRITISH: 英伦
+ METAL: 金属
+ PUNK: 朋克
+ BLUES: 蓝调
+ REGGAE: 雷鬼
+ WORLD_MUSIC: 世界音乐
+ LATIN: 拉丁
+ ALTERNATIVE: 另类/独立
+ NEW_AGE: New Age
+ POST_ROCK: 后摇
+ BOSSA_NOVA: Bossa Nova




### class Theme()

**Extend: enum.Enum**

主题来源

+ GAME: 游戏
+ ANIMATION: 动画
+ FILM_AND_TELEVISION: 影视
+ NETWORK_SONG: 网络歌曲
+ DERIVATIVE_WORK: 同人
+ IDOL: 偶像




---

## class SongCategories()

歌曲分类




### class AudioType()

**Extend: enum.Enum**

有声节目类型

+ RADIO_DRAMA: 广播剧
+ AUDIO_STORY: 有声故事
+ OTHER: 其他




### class ContentType()

**Extend: enum.Enum**

内容类型

+ MUSIC: 音乐
+ AUDIO_PROGRAM: 有声节目




### class CreationType()

**Extend: enum.Enum**

创作类型

+ ORIGINAL: 原创
+ COVER: 翻唱/翻奏
+ REMIX: 改编/remix




### class Language()

**Extend: enum.Enum**

语言

+ CHINESE: 华语
+ JAPANESE: 日语
+ ENGLISH: 英语
+ KOREAN: 韩语
+ CANTONESE: 粤语
+ OTHER_LANGUAGES: 其他语种




### class SongType()

**Extend: enum.Enum**

声音类型

+ HUMAN_SINGING: 人声演唱
+ VOCALOID: VOCALOID歌手
+ HUMAN_GHOST: 人力鬼畜
+ PURE_MUSIC: 纯音乐/演奏




### class Style()

**Extend: enum.Enum**

音乐风格

+ POP: 流行
+ ANCIENT: 古风
+ ROCK: 摇滚
+ FOLK: 民谣
+ ELECTRONIC: 电子
+ DANCE: 舞曲
+ RAP: 说唱
+ LIGHT_MUSIC: 轻音乐
+ ACAPELLA: 阿卡贝拉
+ JAZZ: 爵士
+ COUNTRY: 乡村
+ RNB_SOUL: R&B/Soul
+ CLASSICAL: 古典
+ ETHNIC: 民族
+ BRITISH: 英伦
+ METAL: 金属
+ PUNK: 朋克
+ BLUES: 蓝调
+ REGGAE: 雷鬼
+ WORLD_MUSIC: 世界音乐
+ LATIN: 拉丁
+ ALTERNATIVE_INDEPENDENT: 另类/独立
+ NEW_AGE: New Age
+ POST_ROCK: 后摇
+ BOSSA_NOVA: Bossa Nova




### class Theme()

**Extend: enum.Enum**

主题

+ ANIMATION: 动画
+ GAME: 游戏
+ FILM_AND_TELEVISION: 影视
+ INTERNET_SONG: 网络歌曲
+ SECOND_CREATION: 同人
+ IDOL: 偶像




---

**@dataclasses.dataclass** 

## class SongMeta()

content_type (SongCategories.ContentType): 内容类型

song_type (Union[SongCategories.SongType, SongCategories.AudioType]): 歌曲类型

creation_type (SongCategories.CreationType): 创作类型

language (Optional[SongCategories.Language]): 语言类型

theme (Optional[SongCategories.Theme]): 主题来源

style (Optional[SongCategories.Style]): 风格类型

singer (List[AuthorInfo]): 歌手

player (Optional[List[AuthorInfo]]): 演奏

sound_source (Optional[List[AuthorInfo]]): 音源

tuning (Optional[List[AuthorInfo]]): 调音

lyricist (Optional[List[AuthorInfo]]): 作词

arranger (List[AuthorInfo]): 编曲

composer (Optional[List[AuthorInfo]]): 作曲

mixer (Optional[str]): 混音

cover_maker (Optional[List[AuthorInfo]]): 封面制作者

instrument (Optional[List[str]]): 乐器

origin_url (Optional[str]): 原曲链接

origin_title (Optional[str]): 原曲标题

title (str): 标题

cover (Optional[Picture]): 封面

description (Optional[str]): 描述

tags (Union[List[str], str]): 标签

aid (Optional[int]): 视频 aid

cid (Optional[int]): 视频 cid

tid (Optional[int]): 视频 tid

compilation_id (Optional[int]): 合辑 ID

lrc (Optional[str]): 歌词




---

## async def get_upinfo()

获取 UP 信息


| name | type | description |
| - | - | - |
| `param` | `Union[int, str]` | UP 主 ID 或者用户名 |
| `credential` | `Credential` | 凭据 |




---

## async def upload_cover()

上传封面


| name | type | description |
| - | - | - |
| `cover` | `Picture` | 封面 |
| `credential` | `Credential` | 凭据类 |

**Returns:** `str`:  封面链接




---

## async def upload_lrc()

上传 LRC 歌词


| name | type | description |
| - | - | - |
| `lrc` | `str` | 歌词 |
| `credential` | `Credential` | 凭据 |




