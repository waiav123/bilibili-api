"""
bilibili_api.cheese

有关 bilibili 课程的 api。

注意，注意！课程中的视频和其他视频几乎没有任何相通的 API！

不能将 CheeseVideo 换成 Video 类。(CheeseVideo 类保留了所有的通用的 API)

获取下载链接需要使用 bilibili_api.cheese.get_download_url，video.get_download_url 不适用。

还有，课程的 season_id 和 ep_id 不与番剧相通，井水不犯河水，请不要错用!
"""

import json
import datetime
from typing import Any, List, Union

from .utils.utils import get_api
from .utils.danmaku import Danmaku
from .utils.BytesReader import BytesReader
from .exceptions.ArgsException import ArgsException
from .utils.network import Api, Credential
from .exceptions import NetworkException, ResponseException, DanmakuClosedException

API = get_api("cheese")
API_video = get_api("video")


cheese_video_meta_cache = {}


class CheeseList:
    """
    课程类

    Attributes:
        credential (Credential): 凭据类
    """

    def __init__(
        self,
        season_id: int = -1,
        ep_id: int = -1,
        credential: Union[Credential, None] = None,
    ):
        """
        Args:
            season_id  (int)       : ssid

            ep_id      (int)       : 单集 ep_id

            credential (Credential): 凭据类

        注意：season_id 和 ep_id 任选一个即可，两个都选的话
        以 season_id 为主
        """
        if (season_id == -1) and (ep_id == -1):
            raise ValueError("season id 和 ep id 必须选一个")
        self.__season_id = season_id
        self.__ep_id = ep_id
        self.credential: Credential = credential if credential else Credential()

    async def __fetch_season_id(self) -> None:
        # self.season_id = str(sync(self.get_meta())["season_id"])
        api = API["info"]["meta"]
        params = {"ep_id": self.__ep_id}
        meta = await (
            Api(**api, credential=self.credential).update_params(**params).result
        )
        self.__season_id = int(meta["season_id"])

    async def set_season_id(self, season_id: int) -> None:
        """
        设置季度 id

        Args:
            season_id (int): 季度 id
        """
        self.__init__(season_id=season_id)

    async def set_ep_id(self, ep_id: int) -> None:
        """
        设置 epid 并通过 epid 找到课程

        Args:
            ep_id (int): epid
        """
        self.__init__(ep_id=ep_id)
        await self.__fetch_season_id()

    async def get_season_id(self) -> int:
        """
        获取季度 id

        Returns:
            int: 季度 id
        """
        if self.__season_id == -1:
            await self.__fetch_season_id()
        return self.__season_id

    async def get_meta(self) -> dict:
        """
        获取教程元数据

        Returns:
            dict: 调用 API 返回的结果
        """
        api = API["info"]["meta"]
        params = {"season_id": await self.get_season_id()}
        return (
            await Api(**api, credential=self.credential).update_params(**params).result
        )

    async def get_list_raw(self):
        """
        获取教程所有视频 (返回原始数据)

        Returns:
            dict: 调用 API 返回的结果
        """
        api = API["info"]["list"]
        params = {"season_id": await self.get_season_id(), "pn": 1, "ps": 1000}
        return (
            await Api(**api, credential=self.credential).update_params(**params).result
        )

    async def get_list(self) -> List["CheeseVideo"]:
        """
        获取教程所有视频

        Returns:
            List[CheeseVideo]: 课程视频列表
        """
        global cheese_video_meta_cache
        api = API["info"]["list"]
        params = {"season_id": await self.get_season_id(), "pn": 1, "ps": 1000}
        lists = (
            await Api(**api, credential=self.credential).update_params(**params).result
        )
        cheese_videos = []
        for c in lists["items"]:
            c["ssid"] = await self.get_season_id()
            cheese_video_meta_cache[c["id"]] = c
            cheese_videos.append(CheeseVideo(c["id"], self.credential))
        return cheese_videos


class CheeseVideo:
    """
    教程视频类
    因为不和其他视频相通，所以这里是一个新的类，无继承

    Attributes:
        credential (Credential): 凭据类

        cheese     (CheeseList): 所属的课程
    """

    def __init__(self, epid, credential: Union[Credential, None] = None):
        """
        Args:
            epid      (int)       : 单集 ep_id

            credential (Credential): 凭据类
        """
        global cheese_video_meta_cache
        self.__epid = epid
        self.cheese = None
        self.__aid = None
        self.__cid = None
        self.__meta = None
        meta = cheese_video_meta_cache.get(epid)
        if meta:
            self.cheese = CheeseList(season_id=meta["ssid"])
            self.__meta = meta
            self.__aid = meta["aid"]
            self.__cid = meta["cid"]
        self.credential: Credential = credential if credential else Credential()

    async def __fetch_meta(self) -> int:
        api = API["info"]["meta"]
        params = {"ep_id": self.__epid}
        metadata = await Api(**api).update_params(**params).result
        for v in metadata["episodes"]:
            if v["id"] == self.__epid:
                self.__aid = v["aid"]
                self.__cid = v["cid"]
                self.__meta = v
                self.cheese = CheeseList(season_id=metadata["season_id"])

    async def get_aid(self) -> int:
        """
        获取 aid

        Returns:
            int: aid
        """
        if not self.__aid:
            await self.__fetch_meta()
        return self.__aid

    async def get_cid(self) -> int:
        """
        获取 cid

        Returns:
            int: cid
        """
        if not self.__cid:
            await self.__fetch_meta()
        return self.__cid

    async def get_meta(self) -> dict:
        """
        获取课程元数据

        Returns:
            dict: 视频元数据
        """
        if not self.__meta:
            await self.__fetch_meta()
        return self.__meta

    async def get_cheese(self) -> "CheeseList":
        """
        获取所属课程

        Returns:
            CheeseList: 所属课程
        """
        if not self.cheese:
            await self.__fetch_meta()
        return self.cheese

    async def set_epid(self, epid: int) -> None:
        """
        设置 epid

        Args:
            epid (int): epid
        """
        self.__init__(epid, self.credential)
        await self.__fetch_meta()

    def get_epid(self) -> int:
        """
        获取 epid

        Returns:
            int: epid
        """
        return self.__epid

    async def get_download_url(self) -> dict:
        """
        获取下载链接

        Returns:
            dict: 调用 API 返回的结果。
        """
        api = API["info"]["playurl"]
        params = {
            "avid": await self.get_aid(),
            "ep_id": self.get_epid(),
            "cid": await self.get_cid(),
            "qn": 127,
            "fnval": 4048,
            "fourk": 1,
        }
        return (
            await Api(**api, credential=self.credential).update_params(**params).result
        )

    async def get_stat(self) -> dict:
        """
        获取视频统计数据（播放量，点赞数等）。

        Returns:
            dict: 调用 API 返回的结果。
        """
        api = API_video["info"]["stat"]
        params = {"aid": await self.get_aid()}
        return (
            await Api(**api, credential=self.credential).update_params(**params).result
        )

    async def get_pages(self) -> dict:
        """
        获取分 P 信息。

        Returns:
            dict: 调用 API 返回的结果。
        """
        api = API_video["info"]["pages"]
        params = {"aid": await self.get_aid()}
        return (
            await Api(**api, credential=self.credential).update_params(**params).result
        )

    async def get_danmaku_view(self) -> dict:
        """
        获取弹幕设置、特殊弹幕、弹幕数量、弹幕分段等信息。

        Returns:
            dict: 调用 API 返回的结果。
        """
        cid = await self.get_cid()
        api = API_video["danmaku"]["view"]
        params = {"type": 1, "oid": cid, "pid": await self.get_aid()}

        try:
            resp_data = (
                await Api(**api, credential=self.credential)
                .update_params(**params)
                .request(byte=True)
            )
        except Exception as e:
            raise NetworkException(-1, str(e))

        json_data = {}
        reader = BytesReader(resp_data)
        # 解析二进制数据流

        def read_dm_seg(stream: bytes):
            reader_ = BytesReader(stream)
            data = {}
            while not reader_.has_end():
                t = reader_.varint() >> 3
                if t == 1:
                    data["page_size"] = reader_.varint()
                elif t == 2:
                    data["total"] = reader_.varint()
                else:
                    continue
            return data

        def read_flag(stream: bytes):
            reader_ = BytesReader(stream)
            data = {}
            while not reader_.has_end():
                t = reader_.varint() >> 3
                if t == 1:
                    data["rec_flag"] = reader_.varint()
                elif t == 2:
                    data["rec_text"] = reader_.string()
                elif t == 3:
                    data["rec_switch"] = reader_.varint()
                else:
                    continue
            return data

        def read_command_danmakus(stream: bytes):
            reader_ = BytesReader(stream)
            data = {}
            while not reader_.has_end():
                t = reader_.varint() >> 3
                if t == 1:
                    data["id"] = reader_.varint()
                elif t == 2:
                    data["oid"] = reader_.varint()
                elif t == 3:
                    data["mid"] = reader_.varint()
                elif t == 4:
                    data["commend"] = reader_.string()
                elif t == 5:
                    data["content"] = reader_.string()
                elif t == 6:
                    data["progress"] = reader_.varint()
                elif t == 7:
                    data["ctime"] = reader_.string()
                elif t == 8:
                    data["mtime"] = reader_.string()
                elif t == 9:
                    data["extra"] = json.loads(reader_.string())

                elif t == 10:
                    data["id_str"] = reader_.string()
                else:
                    continue
            return data

        def read_settings(stream: bytes):
            reader_ = BytesReader(stream)
            data = {}
            while not reader_.has_end():
                t = reader_.varint() >> 3

                if t == 1:
                    data["dm_switch"] = reader_.bool()
                elif t == 2:
                    data["ai_switch"] = reader_.bool()
                elif t == 3:
                    data["ai_level"] = reader_.varint()
                elif t == 4:
                    data["enable_top"] = reader_.bool()
                elif t == 5:
                    data["enable_scroll"] = reader_.bool()
                elif t == 6:
                    data["enable_bottom"] = reader_.bool()
                elif t == 7:
                    data["enable_color"] = reader_.bool()
                elif t == 8:
                    data["enable_special"] = reader_.bool()
                elif t == 9:
                    data["prevent_shade"] = reader_.bool()
                elif t == 10:
                    data["dmask"] = reader_.bool()
                elif t == 11:
                    data["opacity"] = reader_.float(True)
                elif t == 12:
                    data["dm_area"] = reader_.varint()
                elif t == 13:
                    data["speed_plus"] = reader_.float(True)
                elif t == 14:
                    data["font_size"] = reader_.float(True)
                elif t == 15:
                    data["screen_sync"] = reader_.bool()
                elif t == 16:
                    data["speed_sync"] = reader_.bool()
                elif t == 17:
                    data["font_family"] = reader_.string()
                elif t == 18:
                    data["bold"] = reader_.bool()
                elif t == 19:
                    data["font_border"] = reader_.varint()
                elif t == 20:
                    data["draw_type"] = reader_.string()
                else:
                    continue
            return data

        def read_image_danmakus(string: bytes):
            image_list = []
            reader_ = BytesReader(string)
            while not reader_.has_end():
                type_ = reader_.varint() >> 3
                if type_ == 1:
                    details_dict = {}
                    details_dict["texts"] = []
                    img_details = reader_.bytes_string()
                    reader_details = BytesReader(img_details)
                    while not reader_details.has_end():
                        type_details = reader_details.varint() >> 3
                        if type_details == 1:
                            details_dict["texts"].append(reader_details.string())
                        elif type_details == 2:
                            details_dict["image"] = reader_details.string()
                        elif type_details == 3:
                            id_string = reader_details.bytes_string()
                            id_reader = BytesReader(id_string)
                            while not id_reader.has_end():
                                type_id = id_reader.varint() >> 3
                                if type_id == 2:
                                    details_dict["id"] = id_reader.varint()
                                else:
                                    raise ResponseException("解析响应数据错误")
                    image_list.append(details_dict)
                else:
                    raise ResponseException("解析响应数据错误")
            return image_list

        while not reader.has_end():
            type_ = reader.varint() >> 3

            if type_ == 1:
                json_data["state"] = reader.varint()
            elif type_ == 2:
                json_data["text"] = reader.string()
            elif type_ == 3:
                json_data["text_side"] = reader.string()
            elif type_ == 4:
                json_data["dm_seg"] = read_dm_seg(reader.bytes_string())
            elif type_ == 5:
                json_data["flag"] = read_flag(reader.bytes_string())
            elif type_ == 6:
                if "special_dms" not in json_data:
                    json_data["special_dms"] = []
                json_data["special_dms"].append(reader.string())
            elif type_ == 7:
                json_data["check_box"] = reader.bool()
            elif type_ == 8:
                json_data["count"] = reader.varint()
            elif type_ == 9:
                if "command_dms" not in json_data:
                    json_data["command_dms"] = []
                json_data["command_dms"].append(
                    read_command_danmakus(reader.bytes_string())
                )
            elif type_ == 10:
                json_data["dm_setting"] = read_settings(reader.bytes_string())
            elif type_ == 12:
                json_data["image_dms"] = read_image_danmakus(reader.bytes_string())
            else:
                continue
        return json_data

    async def get_danmakus(
        self,
        date: Union[datetime.date, None] = None,
        from_seg: Union[int, None] = None,
        to_seg: Union[int, None] = None,
    ) -> List[Danmaku]:
        """
        获取弹幕。

        Args:
            date       (datetime.Date | None, optional): 指定日期后为获取历史弹幕，精确到年月日。Defaults to None.

            from_seg (int, optional): 从第几段开始(0 开始编号，None 为从第一段开始，一段 6 分钟). Defaults to None.

            to_seg (int, optional): 到第几段结束(0 开始编号，None 为到最后一段，包含编号的段，一段 6 分钟). Defaults to None.

        Returns:
            List[Danmaku]: Danmaku 类的列表。

        注意：
            - 1. 段数可以通过视频时长计算。6分钟为一段。
            - 2. `from_seg` 和 `to_seg` 仅对 `date == None` 的时候有效果。
            - 3. 例：取前 `12` 分钟的弹幕：`from_seg=0, to_seg=1`
        """
        if date is not None:
            self.credential.raise_for_no_sessdata()

        cid = await self.get_cid()
        aid = await self.get_aid()
        params: dict[str, Any] = {"oid": cid, "type": 1, "pid": aid}
        if date is not None:
            # 获取历史弹幕
            api = API_video["danmaku"]["get_history_danmaku"]
            params["date"] = date.strftime("%Y-%m-%d")
            params["type"] = 1
            from_seg = to_seg = 0
        else:
            api = API_video["danmaku"]["get_danmaku"]
            if from_seg == None:
                from_seg = 0
            if to_seg == None:
                to_seg = self.get_meta()["duration"] // 360 + 1

        danmakus = []

        for seg in range(from_seg, to_seg + 1):
            if date is None:
                # 仅当获取当前弹幕时需要该参数
                params["segment_index"] = seg + 1
            try:
                data = (
                    await Api(**api, credential=self.credential)
                    .update_params(**params)
                    .request(byte=True)
                )
            except Exception as e:
                raise NetworkException(-1, str(e))

            if data == b"\x10\x01":
                # 视频弹幕被关闭
                raise DanmakuClosedException()

            reader = BytesReader(data)
            while not reader.has_end():
                type_ = reader.varint() >> 3
                if type_ != 1:
                    if type_ == 4:
                        reader.bytes_string()
                        # 什么鬼？我用 protoc 解析出乱码！
                    elif type_ == 5:
                        # 大会员专属颜色
                        reader.varint()
                        reader.varint()
                        reader.varint()
                        reader.bytes_string()
                    elif type_ == 13:
                        # ???
                        continue
                    else:
                        raise ResponseException("解析响应数据错误")

                dm = Danmaku("")
                dm_pack_data = reader.bytes_string()
                dm_reader = BytesReader(dm_pack_data)

                while not dm_reader.has_end():
                    data_type = dm_reader.varint() >> 3

                    if data_type == 1:
                        dm.id_ = dm_reader.varint()
                    elif data_type == 2:
                        dm.dm_time = dm_reader.varint() / 1000
                    elif data_type == 3:
                        dm.mode = dm_reader.varint()
                    elif data_type == 4:
                        dm.font_size = dm_reader.varint()
                    elif data_type == 5:
                        color = dm_reader.varint()
                        if color != 60001:
                            color = hex(color)[2:]
                        else:
                            color = "special"
                        dm.color = color
                    elif data_type == 6:
                        dm.crc32_id = dm_reader.string()
                    elif data_type == 7:
                        dm.text = dm_reader.string()
                    elif data_type == 8:
                        dm.send_time = dm_reader.varint()
                    elif data_type == 9:
                        dm.weight = dm_reader.varint()
                    elif data_type == 10:
                        dm.action = str(dm_reader.string())
                    elif data_type == 11:
                        dm.pool = dm_reader.varint()
                    elif data_type == 12:
                        dm.id_str = dm_reader.string()
                    elif data_type == 13:
                        dm.attr = dm_reader.varint()
                    elif data_type == 14:
                        dm.uid = dm_reader.varint()
                    elif data_type == 15:
                        dm_reader.varint()
                    elif data_type == 20:
                        dm_reader.bytes_string()
                    elif data_type == 21:
                        dm_reader.bytes_string()
                    elif data_type == 22:
                        dm_reader.bytes_string()
                    elif data_type == 25:
                        dm_reader.varint()
                    elif data_type == 26:
                        dm_reader.varint()
                    else:
                        break
                danmakus.append(dm)
        return danmakus

    async def get_pbp(self) -> dict:
        """
        获取高能进度条

        Returns:
            dict: 调用 API 返回的结果
        """
        cid = await self.get_cid()
        api = API_video["info"]["pbp"]
        params = {"cid": cid}
        return (
            await Api(**api, credential=self.credential)
            .update_params(**params)
            .request(raw=True)
        )

    async def send_danmaku(self, danmaku: Union[Danmaku, None] = None):
        """
        发送弹幕。

        Args:
            danmaku (Danmaku | None): Danmaku 类。Defaults to None.

        Returns:
            dict: 调用 API 返回的结果。
        """

        danmaku = danmaku if danmaku else Danmaku("")

        self.credential.raise_for_no_sessdata()
        self.credential.raise_for_no_bili_jct()

        api = API_video["danmaku"]["send_danmaku"]

        if danmaku.is_sub:
            pool = 1
        else:
            pool = 0
        data = {
            "type": 1,
            "oid": await self.get_cid(),
            "msg": danmaku.text,
            "aid": await self.get_aid(),
            "progress": int(danmaku.dm_time * 1000),
            "color": int(danmaku.color, 16),
            "fontsize": danmaku.font_size,
            "pool": pool,
            "mode": danmaku.mode,
            "plat": 1,
        }
        return await Api(**api, credential=self.credential).update_data(**data).result

    async def has_liked(self):
        """
        视频是否点赞过。

        Returns:
            bool: 视频是否点赞过。
        """
        self.credential.raise_for_no_sessdata()

        api = API_video["info"]["has_liked"]
        params = {"aid": await self.get_aid()}
        return (
            await Api(**api, credential=self.credential).update_params(**params).result
            == 1
        )

    async def get_pay_coins(self):
        """
        获取视频已投币数量。

        Returns:
            int: 视频已投币数量。
        """
        self.credential.raise_for_no_sessdata()

        api = API_video["info"]["get_pay_coins"]
        params = {"aid": await self.get_aid()}
        return (
            await Api(**api, credential=self.credential).update_params(**params).result
        )["multiply"]

    async def has_favoured(self):
        """
        是否已收藏。

        Returns:
            bool: 视频是否已收藏。
        """
        self.credential.raise_for_no_sessdata()

        api = API_video["info"]["has_favoured"]
        params = {"aid": await self.get_aid()}
        return (
            await Api(**api, credential=self.credential).update_params(**params).result
        )["favoured"]

    async def like(self, status: bool = True):
        """
        点赞视频。

        Args:
            status (bool, optional): 点赞状态。Defaults to True.

        Returns:
            dict: 调用 API 返回的结果。
        """
        self.credential.raise_for_no_sessdata()
        self.credential.raise_for_no_bili_jct()

        api = API_video["operate"]["like"]
        data = {"aid": await self.get_aid(), "like": 1 if status else 2}
        return await Api(**api, credential=self.credential).update_data(**data).result

    async def pay_coin(self, num: int = 1, like: bool = False):
        """
        投币。

        Args:
            num  (int, optional) : 硬币数量，为 1 ~ 2 个。Defaults to 1.

            like (bool, optional): 是否同时点赞。Defaults to False.

        Returns:
            dict: 调用 API 返回的结果。
        """
        self.credential.raise_for_no_sessdata()
        self.credential.raise_for_no_bili_jct()

        if num not in (1, 2):
            raise ArgsException("投币数量只能是 1 ~ 2 个。")

        api = API_video["operate"]["coin"]
        data = {
            "aid": await self.get_aid(),
            "multiply": num,
            "like": 1 if like else 0,
        }
        return await Api(**api, credential=self.credential).update_data(**data).result

    async def set_favorite(
        self, add_media_ids: List[int] = [], del_media_ids: List[int] = []
    ):
        """
        设置视频收藏状况。

        Args:
            add_media_ids (List[int], optional): 要添加到的收藏夹 ID. Defaults to [].

            del_media_ids (List[int], optional): 要移出的收藏夹 ID. Defaults to [].

        Returns:
            dict: 调用 API 返回结果。
        """
        if len(add_media_ids) + len(del_media_ids) == 0:
            raise ArgsException(
                "对收藏夹无修改。请至少提供 add_media_ids 和 del_media_ids 中的其中一个。"
            )

        self.credential.raise_for_no_sessdata()
        self.credential.raise_for_no_bili_jct()

        api = API_video["operate"]["favorite"]
        data = {
            "rid": await self.get_aid(),
            "type": 2,
            "add_media_ids": ",".join(map(lambda x: str(x), add_media_ids)),
            "del_media_ids": ",".join(map(lambda x: str(x), del_media_ids)),
        }
        return await Api(**api, credential=self.credential).update_data(**data).result

    async def get_danmaku_xml(self) -> str:
        """
        获取所有弹幕的 xml 源文件（非装填）

        Returns:
            str: 文件源
        """
        cid = await self.get_cid()
        url = f"https://comment.bilibili.com/{cid}.xml"
        return (await Api(url=url, method="GET").request(byte=True)).decode("utf-8")
