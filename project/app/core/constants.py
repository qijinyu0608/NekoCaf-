from app.auth import DEFAULT_TENANT_ID


DEFAULT_MEMBER_ID = "member-1001"
DEFAULT_CITY = "上海"
DEFAULT_STORE_ID = "store-shanghai-jingan"
DEFAULT_DATE = "2026-05-20"
CHECK_IN_POINTS_PER_GUEST = 50
STORE_STATUS_LABELS = {
    "OPEN": "营业中",
    "PAUSED": "暂停预约",
}
_BASE_CAT_AVATAR_URLS = {
    "cat-001": "/static/assets/cats/pudding.jpg",
    "cat-002": "/static/assets/cats/latte.jpg",
    "cat-003": "/static/assets/cats/chestnut.jpg",
}
CAT_AVATAR_URLS = {
    **_BASE_CAT_AVATAR_URLS,
    **{
        f"cat-{index:03d}": f"/static/assets/cats/cat-{index:03d}.jpg"
        for index in range(4, 102)
    },
}
STORE_COMMERCIAL_INFO = {
    "store-shanghai-jingan": ("静安区愚园路 108 号", "10:00-22:00", "021-6000-0101"),
    "store-shanghai-pudong": ("浦东新区滨江大道 168 号", "10:00-22:30", "021-6000-0102"),
    "store-shanghai-xuhui": ("徐汇区衡山路 88 号", "10:00-22:00", "021-6000-0103"),
    "store-hangzhou-xihu": ("西湖区南山路 77 号", "10:00-22:00", "0571-6000-0201"),
    "store-hangzhou-binjiang": ("滨江区江南大道 588 号", "10:30-22:30", "0571-6000-0202"),
    "store-nanjing-xinjiekou": ("秦淮区中山南路 18 号", "10:00-22:00", "025-6000-0301"),
    "store-nanjing-hexi": ("建邺区江东中路 99 号", "10:00-22:30", "025-6000-0302"),
    "store-beijing-sanlitun": ("朝阳区三里屯太古里北区 12 号", "10:30-23:00", "010-6000-0401"),
    "store-beijing-wudaokou": ("海淀区成府路 35 号", "09:30-22:00", "010-6000-0402"),
    "store-chengdu-taikooli": ("锦江区中纱帽街 8 号", "10:30-22:30", "028-6000-0501"),
}
EXPANDED_STORE_CITIES = [
    ("guangzhou", "广州", "020", [("tianhe", "天河", "天河城店"), ("yuexiu", "越秀", "东山口店"), ("haizhu", "海珠", "琶洲店"), ("panyu", "番禺", "万博店"), ("liwan", "荔湾", "永庆坊店")]),
    ("shenzhen", "深圳", "0755", [("nanshan", "南山", "科技园店"), ("futian", "福田", "中心区店"), ("luohu", "罗湖", "万象城店"), ("baoan", "宝安", "壹方城店"), ("longgang", "龙岗", "坂田店")]),
    ("suzhou", "苏州", "0512", [("gongyeyuan", "工业园", "金鸡湖店"), ("gusu", "姑苏", "平江路店"), ("huqiu", "虎丘", "狮山店"), ("wuzhong", "吴中", "木渎店"), ("xiangcheng", "相城", "活力岛店")]),
    ("wuhan", "武汉", "027", [("jianghan", "江汉", "江汉路店"), ("wuchang", "武昌", "楚河汉街店"), ("hongshan", "洪山", "光谷店"), ("hanyang", "汉阳", "钟家村店"), ("qiaokou", "硚口", "汉正街店")]),
    ("xian", "西安", "029", [("beilin", "碑林", "南门店"), ("yanta", "雁塔", "小寨店"), ("lianhu", "莲湖", "钟楼店"), ("weiyang", "未央", "大明宫店"), ("changan", "长安", "大学城店")]),
    ("tianjin", "天津", "022", [("heping", "和平", "五大道店"), ("nankai", "南开", "鼓楼店"), ("hexi", "河西", "文化中心店"), ("hedong", "河东", "爱琴海店"), ("binhai", "滨海", "于家堡店")]),
    ("chongqing", "重庆", "023", [("yuzhong", "渝中", "解放碑店"), ("jiangbei", "江北", "观音桥店"), ("nanan", "南岸", "南滨路店"), ("shapingba", "沙坪坝", "三峡广场店"), ("jiulongpo", "九龙坡", "杨家坪店")]),
    ("qingdao", "青岛", "0532", [("shinan", "市南", "万象城店"), ("shibei", "市北", "台东店"), ("laoshan", "崂山", "金家岭店"), ("licang", "李沧", "乐客城店"), ("huangdao", "黄岛", "金沙滩店")]),
    ("xiamen", "厦门", "0592", [("siming", "思明", "中山路店"), ("huli", "湖里", "五缘湾店"), ("jimei", "集美", "杏林湾店"), ("haicang", "海沧", "阿罗海店"), ("tongan", "同安", "银湖店")]),
    ("changsha", "长沙", "0731", [("furong", "芙蓉", "五一广场店"), ("yuelu", "岳麓", "梅溪湖店"), ("tianxin", "天心", "坡子街店"), ("kaifu", "开福", "北辰店"), ("yuhua", "雨花", "高桥店")]),
    ("hefei", "合肥", "0551", [("shushan", "蜀山", "天鹅湖店"), ("luyang", "庐阳", "淮河路店"), ("baohe", "包河", "滨湖店"), ("yaohai", "瑶海", "龙湖店"), ("gaoxin", "高新", "科学城店")]),
    ("zhengzhou", "郑州", "0371", [("jinshui", "金水", "花园路店"), ("erqi", "二七", "德化街店"), ("zhengdong", "郑东", "如意湖店"), ("zhongyuan", "中原", "万达店"), ("guancheng", "管城", "商都路店")]),
    ("ningbo", "宁波", "0574", [("haishu", "海曙", "天一广场店"), ("yinzhou", "鄞州", "南部商务区店"), ("jiangbei", "江北", "来福士店"), ("beilun", "北仑", "银泰店"), ("zhenhai", "镇海", "骆驼店")]),
    ("fuzhou", "福州", "0591", [("gulou", "鼓楼", "三坊七巷店"), ("taijiang", "台江", "上下杭店"), ("cangshan", "仓山", "金山店"), ("jinan", "晋安", "东二环店"), ("mawei", "马尾", "船政店")]),
    ("jinan", "济南", "0531", [("lixia", "历下", "泉城路店"), ("shizhong", "市中", "大观园店"), ("huaiyin", "槐荫", "西客站店"), ("tianqiao", "天桥", "北园店"), ("licheng", "历城", "唐冶店")]),
    ("wuxi", "无锡", "0510", [("liangxi", "梁溪", "南长街店"), ("binhu", "滨湖", "蠡湖店"), ("xinwu", "新吴", "新地假日店"), ("huishan", "惠山", "万达店"), ("xishan", "锡山", "荟聚店")]),
    ("kunming", "昆明", "0871", [("wuhua", "五华", "翠湖店"), ("panlong", "盘龙", "同德店"), ("guandu", "官渡", "世纪城店"), ("xishan", "西山", "滇池店"), ("chenggong", "呈贡", "大学城店")]),
    ("shenyang", "沈阳", "024", [("heping", "和平", "太原街店"), ("shenhe", "沈河", "中街店"), ("dadong", "大东", "龙之梦店"), ("huanggu", "皇姑", "北陵店"), ("hunnan", "浑南", "奥体店")]),
]
