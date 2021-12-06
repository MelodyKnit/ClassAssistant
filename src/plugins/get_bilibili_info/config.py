from pydantic import BaseSettings


class Config(BaseSettings):
    # 视频信息地址
    video_info_url = "https://api.bilibili.com/x/web-interface/view"
    # 用户信息地址
    user_info_url = "http://api.bilibili.com/x/space/acc/info"
    # 视频链接
    video_url = "https://www.bilibili.com/video/"
    # 用户链接
    user_url = "https://space.bilibili.com/"
    # 用户名搜索
    user_name_search_url = "https://api.bilibili.com/x/web-interface/search/type"
    # bili直播地址
    bili_live_url = "https://live.bilibili.com/"
