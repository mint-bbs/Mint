import base64
import hashlib
import re

from passlib.hash import des_crypt


class TripService:
    @classmethod
    def tripper(cls, name: str):
        # 正規表現パターンを定義
        pattern = r"^(.*?)#(.*)$"

        # パターンにマッチする部分を抜き出す
        result: re.Match[str] = re.match(pattern, name)

        if result:
            name2 = (
                result.group(1).replace("◆", "◇").replace("★", "☆").replace("●", "○")
            )
            trip_key = result.group(2)
            if len(trip_key) <= 10:
                tripkey = trip_key.encode("shift_jis", "replace")
                salt = (tripkey + b"H.")[1:3]
                salt = re.sub(rb"[^\.-z]", b".", salt)
                salt = salt.translate(
                    bytes.maketrans(b":;<=>?@[\\]^_`", b"ABCDEFGabcdef")
                )
                trip = des_crypt.hash(tripkey, salt=salt.decode("shift-jis"))
                trip = trip[-10:]
            else:
                trip_key = trip_key.encode("shift_jis")
                code = hashlib.sha1(trip_key).digest()
                code = base64.b64encode(code, b"./")
                code = code[:12]
                trip = code.decode("utf8")
            return f"{name2} </b>◆{trip}<b>"
        else:
            return name.replace("◆", "◇").replace("★", "☆").replace("●", "○")
