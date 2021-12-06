from pydantic import BaseSettings


class Config(BaseSettings):
    class_cadre = ["组织委员", "心理委员", "宣传委员", "体育委员", "男生委员",
                   "女生委员", "治保委员", "副班长", "学习委员", "生卫委员",
                   "权益委员", "班长", "团支书"]
