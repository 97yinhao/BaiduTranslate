## **百度翻译破解案例**

**目标**

```python
破解百度翻译接口，抓取翻译结果数据
```

**实现步骤**

- **1、F12抓包,找到json的地址,观察查询参数**

  ```python
  1、POST地址: https://fanyi.baidu.com/v2transapi
  2、Form表单数据（多次抓取在变的字段）
     from: zh
     to: en
     sign: 54706.276099  #这个是如何生成的？
     token: a927248ae7146c842bb4a94457ca35ee # 基本固定,但也想办法获取
  ```

- **2、抓取相关JS文件**

  ```python
  右上角 - 搜索 - sign: - 找到具体JS文件(index_c8a141d.js) - 格式化输出
  ```


**3、在JS中寻找sign的生成代码**

```python
1、在格式化输出的JS代码中搜索: sign: 找到如下JS代码：sign: m(a),
2、通过设置断点，找到m(a)函数的位置，即生成sign的具体函数
   # 1. a 为要翻译的单词
   # 2. 鼠标移动到 m(a) 位置处，点击可进入具体m(a)函数代码块
```

**4、生成sign的m(a)函数具体代码如下(在一个大的define中)**

```javascript
function a(r) {
        if (Array.isArray(r)) {
            for (var o = 0, t = Array(r.length); o < r.length; o++)
                t[o] = r[o];
            return t
        }
        return Array.from(r)
    }
function n(r, o) {
    for (var t = 0; t < o.length - 2; t += 3) {
        var a = o.charAt(t + 2);
        a = a >= "a" ? a.charCodeAt(0) - 87 : Number(a),
            a = "+" === o.charAt(t + 1) ? r >>> a : r << a,
            r = "+" === o.charAt(t) ? r + a & 4294967295 : r ^ a
    }
    return r
}
function e(r) {
    var o = r.match(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g);
    if (null === o) {
        var t = r.length;
        t > 30 && (r = "" + r.substr(0, 10) + r.substr(Math.floor(t / 2) - 5, 10) + r.substr(-10, 10))
    } else {
        for (var e = r.split(/[\uD800-\uDBFF][\uDC00-\uDFFF]/), C = 0, h = e.length, f = []; h > C; C++)
            "" !== e[C] && f.push.apply(f, a(e[C].split(""))),
                C !== h - 1 && f.push(o[C]);
        var g = f.length;
        g > 30 && (r = f.slice(0, 10).join("") + f.slice(Math.floor(g / 2) - 5, Math.floor(g / 2) + 5).join("") + f.slice(-10).join(""))
    }
//    var u = void 0
//    , l = "" + String.fromCharCode(103) + String.fromCharCode(116) + String.fromCharCode(107);
//    u = null !== i ? i : (i = window[l] || "") || "";
//  断点调试,然后从网页源码中找到 window.gtk的值    
    var u = '320305.131321201'
    
    for (var d = u.split("."), m = Number(d[0]) || 0, s = Number(d[1]) || 0, S = [], c = 0, v = 0; v < r.length; v++) {
        var A = r.charCodeAt(v);
        128 > A ? S[c++] = A : (2048 > A ? S[c++] = A >> 6 | 192 : (55296 === (64512 & A) && v + 1 < r.length && 56320 === (64512 & r.charCodeAt(v + 1)) ? (A = 65536 + ((1023 & A) << 10) + (1023 & r.charCodeAt(++v)),
            S[c++] = A >> 18 | 240,
            S[c++] = A >> 12 & 63 | 128) : S[c++] = A >> 12 | 224,
                                                                    S[c++] = A >> 6 & 63 | 128),
                                S[c++] = 63 & A | 128)
    }
    for (var p = m, F = "" + String.fromCharCode(43) + String.fromCharCode(45) + String.fromCharCode(97) + ("" + String.fromCharCode(94) + String.fromCharCode(43) + String.fromCharCode(54)), D = "" + String.fromCharCode(43) + String.fromCharCode(45) + String.fromCharCode(51) + ("" + String.fromCharCode(94) + String.fromCharCode(43) + String.fromCharCode(98)) + ("" + String.fromCharCode(43) + String.fromCharCode(45) + String.fromCharCode(102)), b = 0; b < S.length; b++)
        p += S[b],
            p = n(p, F);
    return p = n(p, D),
        p ^= s,
        0 > p && (p = (2147483647 & p) + 2147483648),
        p %= 1e6,
        p.toString() + "." + (p ^ m)
}
var i = null;
//此行报错，直接注释掉即可
//t.exports = e
```

- **5、直接将代码写入本地js文件,利用pyexecjs模块执行js代码进行调试**

  ```python
  import execjs
  
  with open('node.js','r') as f:
      js_data = f.read()
  # 创建对象
  exec_object = execjs.compile(js_data)
  sign = exec_object.eval('e("hello")')
  print(sign)
  ```


- **获取token**

  ```python
  # 在js中
  token: window.common.token
  # 在响应中想办法获取此值
  token_url = 'https://fanyi.baidu.com/?aldtype=16047'
  regex: "token: '(.*?)'"
  ```

- **具体代码实现**

  ```python
  import requests
  import re
  import execjs
  
  class BaiduTranslateSpider(object):
      def __init__(self):
          self.token_url = 'https://fanyi.baidu.com/?aldtype=16047'
          self.post_url = 'https://fanyi.baidu.com/v2transapi'
          self.headers = {
              'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
              # 'accept-encoding': 'gzip, deflate, br',
              'accept-language': 'zh-CN,zh;q=0.9',
              'cache-control': 'no-cache',
              'cookie': 'BAIDUID=52920E829C1F64EE98183B703F4E37A9:FG=1; BIDUPSID=52920E829C1F64EE98183B703F4E37A9; PSTM=1562657403; to_lang_often=%5B%7B%22value%22%3A%22en%22%2C%22text%22%3A%22%u82F1%u8BED%22%7D%2C%7B%22value%22%3A%22zh%22%2C%22text%22%3A%22%u4E2D%u6587%22%7D%5D; REALTIME_TRANS_SWITCH=1; FANYI_WORD_SWITCH=1; HISTORY_SWITCH=1; SOUND_SPD_SWITCH=1; SOUND_PREFER_SWITCH=1; delPer=0; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; BCLID=6890774803653935935; BDSFRCVID=4XAsJeCCxG3DLCbwbJrKDGwjNA0UN_I3KhXZ3J; H_BDCLCKID_SF=tRk8oIDaJCvSe6r1MtQ_M4F_qxby26nUQ5neaJ5n0-nnhnL4W46bqJKFLtozKMoI3C7fotJJ5nololIRy6CKjjb-jaDqJ5n3bTnjstcS2RREHJrg-trSMDCShGRGWlO9WDTm_D_KfxnkOnc6qJj0-jjXqqo8K5Ljaa5n-pPKKRAaqD04bPbZL4DdMa7HLtAO3mkjbnczfn02OP5P5lJ_e-4syPRG2xRnWIvrKfA-b4ncjRcTehoM3xI8LNj405OTt2LEoDPMJKIbMI_rMbbfhKC3hqJfaI62aKDs_RCMBhcqEIL4eJOIb6_w5gcq0T_HttjtXR0atn7ZSMbSj4Qo5pK95p38bxnDK2rQLb5zah5nhMJS3j7JDMP0-4rJhxby523i5J6vQpnJ8hQ3DRoWXPIqbN7P-p5Z5mAqKl0MLIOkbC_6j5DWDTvLeU7J-n8XbI60XRj85-ohHJrFMtQ_q4tehHRMBUo9WDTm_DoTttt5fUj6qJj855jXqqo8KMtHJaFf-pPKKRAashnzWjrkqqOQ5pj-WnQr3mkjbn5yfn02OpjPX6joht4syPRG2xRnWIvrKfA-b4ncjRcTehoM3xI8LNj405OTt2LEoC0XtIDhMDvPMCTSMt_HMxrKetJyaR0JhpjbWJ5TEPnjDUOdLPDW-46HBM3xbKQw5CJGBf7zhpvdWhC5y6ISKx-_J68Dtf5; ZD_ENTRY=baidu; PSINO=2; H_PS_PSSID=26525_1444_21095_29578_29521_28518_29098_29568_28830_29221_26350_29459; locale=zh; Hm_lvt_64ecd82404c51e03dc91cb9e8c025574=1563426293,1563996067; from_lang_often=%5B%7B%22value%22%3A%22zh%22%2C%22text%22%3A%22%u4E2D%u6587%22%7D%2C%7B%22value%22%3A%22en%22%2C%22text%22%3A%22%u82F1%u8BED%22%7D%5D; Hm_lpvt_64ecd82404c51e03dc91cb9e8c025574=1563999768; yjs_js_security_passport=2706b5b03983b8fa12fe756b8e4a08b98fb43022_1563999769_js',
              'pragma': 'no-cache',
              'upgrade-insecure-requests': '1',
              'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
          }
  
      # 获取token
      def get_token(self):
          token_url = 'https://fanyi.baidu.com/?aldtype=16047'
          # 定义请求头
          r = requests.get(self.token_url,headers=self.headers)
          token = re.findall(r"token: '(.*?)'",r.text)
          window_gtk = re.findall(r"window.*?gtk = '(.*?)';</script>",r.text)
          if token:
              return token[0],window_gtk[0]
  
      # 获取sign
      def get_sign(self,word):
          with open('百度翻译.js','r') as f:
              js_data = f.read()
  
          exec_object = execjs.compile(js_data)
          sign = exec_object.eval('e("{}")'.format(word))
  
          return sign
  
      # 主函数
      def main(self,word,fro,to):
          token,gtk = self.get_token()
          sign = self.get_sign(word)
          # 找到form表单数据如下,sign和token需要想办法获取
          form_data = {
              'from': fro,
              'to': to,
              'query': word,
              'transtype': 'realtime',
              'simple_means_flag': '3',
              'sign': sign,
              'token': token
          }
          r = requests.post(self.post_url,data=form_data,headers=self.headers)
          print(r.json()['trans_result']['data'][0]['dst'])
  
  if __name__ == '__main__':
      spider = BaiduTranslateSpider()
      menu = '1. 英译汉 2. 汉译英'
      choice = input('1. 英译汉 2. 汉译英 : ')
      word = input('请输入要翻译的单词:')
      if choice == '1':
          fro = 'en'
          to = 'zh'
      elif choice == '2':
          fro = 'zh'
          to = 'en'
  
      spider.main(word,fro,to)
  ```

testtest
