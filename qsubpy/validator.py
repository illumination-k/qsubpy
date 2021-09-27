import re


class CommonVariableValidator:
    def __init__(self):
        # 初期化
        self.pattern = re.compile(r'^[a-z|A-Z]+=[0-9a-zA-Z]+')

    def __contains__(self, val):
        # マッチ処理を行う
        return re.match(self.pattern, val)

    def __iter__(self):
        # エラー時にコンソールに表示される(invalid choice: 値 (choose from なんとか)
        # print_help()のmetavarでも表示されるので、metaverオプションを使って隠す
        return iter(("str", self.pattern))
