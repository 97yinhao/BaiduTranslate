import requests
import re
import execjs


class BaiduTranslateSpider(object):
    def __init__(self):
        self.get_url = 'https://fanyi.baidu.com/?aldtype=16047'
        self.post_url = 'https://fanyi.baidu.com/v2transapi'
        self.headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "cookie": "BAIDUID=FCFC1FD52563D503DD6B7745214A99C0:FG=1; BIDUPSID=FCFC1FD52563D503DD6B7745214A99C0; PSTM=1559212227; BDUSS=X51Y2xZcHNjLWVQaFdNeE82SU9sUms2TDBYS2JqeUo3NVV1bC01aWZxbUZVUmhkSVFBQUFBJCQAAAAAAAAAAAEAAACSkkS-RnJpZW5kbHlZaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIXE8FyFxPBcd; MCITY=-282%3A280%3A297%3A; REALTIME_TRANS_SWITCH=1; FANYI_WORD_SWITCH=1; HISTORY_SWITCH=1; SOUND_SPD_SWITCH=1; SOUND_PREFER_SWITCH=1; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; to_lang_often=%5B%7B%22value%22%3A%22en%22%2C%22text%22%3A%22%u82F1%u8BED%22%7D%2C%7B%22value%22%3A%22zh%22%2C%22text%22%3A%22%u4E2D%u6587%22%7D%5D; from_lang_often=%5B%7B%22value%22%3A%22zh%22%2C%22text%22%3A%22%u4E2D%u6587%22%7D%2C%7B%22value%22%3A%22en%22%2C%22text%22%3A%22%u82F1%u8BED%22%7D%5D; BDRCVFR[feWj1Vr5u3D]=I67x6TjHwwYf0; delPer=0; PSINO=3; locale=zh; H_PS_PSSID=1459_21110_29578_29521_28518_29099_29568_28836_29221_26350_29461; Hm_lvt_64ecd82404c51e03dc91cb9e8c025574=1564019740,1564026900,1564027081,1564027086; Hm_lpvt_64ecd82404c51e03dc91cb9e8c025574=1564027086; yjs_js_security_passport=c17cca615710e7c62f9a2ceac8e4e71b465f9244_1564027087_js",
            "referer": "https://fanyi.baidu.com/?aldtype=16047",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }

    # 获取token
    def get_token(self):
        html = requests.get(self.get_url, headers=self.headers).text
        # 正则解析
        pattern = re.compile("token: '(.*?)'", re.S)
        token = pattern.findall(html)[0]
        return token

    # 获取sign
    def get_sign(self, word):
        with open('node.js', 'r') as f:
            js_data = f.read()
        execjs_obj = execjs.compile(js_data)
        sign = execjs_obj.eval('e("{}")'.format(word))

        return sign

    # 获取翻译结果
    def get_result(self, word, fro, to):
        token = self.get_token()
        sign = self.get_sign(word)
        form_data = {
            "from": fro,
            "to": to,
            "query": word,
            "transtype": "realtime",
            "simple_means_flag": "3",
            "sign": sign,
            "token": token,
        }
        html_json = requests.post(
            url='https://fanyi.baidu.com/v2transapi',
            data=form_data,
            headers=self.headers
        ).json()

        result = html_json['trans_result']['data'][0]['dst']
        return result


if __name__ == '__main__':
    spider = BaiduTranslateSpider()
    menu = """1) 英译汉
2) 汉译英
请选择:"""
    choice = input(menu)
    if choice == '1':
        fro = 'en'
        to = 'zh'
    else:
        fro = 'zh'
        to = 'en'
    word = input('请输入要翻译的单词:')
    result = spider.get_result(word, fro, to)
    print(result)
