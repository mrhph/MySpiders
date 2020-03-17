import requests
import os, re, sys, json, shutil, logging

from typing import List
from io import BytesIO
from retrying import retry
from fontTools.ttLib import TTFont

base_font_char = [
    '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '店', '中', '美', '家', '馆', '小', '车', '大', '市', '公', '酒',
    '行', '国', '品', '发', '电', '金', '心', '业', '商', '司', '超', '生', '装', '园', '场', '食', '有', '新', '限', '天', '面',
    '工', '服', '海', '华', '水', '房', '饰', '城', '乐', '汽', '香', '部', '利', '子', '老', '艺', '花', '专', '东', '肉', '菜',
    '学', '福', '饭', '人', '百', '餐', '茶', '务', '通', '味', '所', '山', '区', '门', '药', '银', '农', '龙', '停', '尚', '安',
    '广', '鑫', '一', '容', '动', '南', '具', '源', '兴', '鲜', '记', '时', '机', '烤', '文', '康', '信', '果', '阳', '理', '锅',
    '宝', '达', '地', '儿', '衣', '特', '产', '西', '批', '坊', '州', '牛', '佳', '化', '五', '米', '修', '爱', '北', '养', '卖',
    '建', '材', '三', '会', '鸡', '室', '红', '站', '德', '王', '光', '名', '丽', '油', '院', '堂', '烧', '江', '社', '合', '星',
    '货', '型', '村', '自', '科', '快', '便', '日', '民', '营', '和', '活', '童', '明', '器', '烟', '育', '宾', '精', '屋', '经',
    '居', '庄', '石', '顺', '林', '尔', '县', '手', '厅', '销', '用', '好', '客', '火', '雅', '盛', '体', '旅', '之', '鞋', '辣',
    '作', '粉', '包', '楼', '校', '鱼', '平', '彩', '上', '吧', '保', '永', '万', '物', '教', '吃', '设', '医', '正', '造', '丰',
    '健', '点', '汤', '网', '庆', '技', '斯', '洗', '料', '配', '汇', '木', '缘', '加', '麻', '联', '卫', '川', '泰', '色', '世',
    '方', '寓', '风', '幼', '羊', '烫', '来', '高', '厂', '兰', '阿', '贝', '皮', '全', '女', '拉', '成', '云', '维', '贸', '道',
    '术', '运', '都', '口', '博', '河', '瑞', '宏', '京', '际', '路', '祥', '青', '镇', '厨', '培', '力', '惠', '连', '马', '鸿',
    '钢', '训', '影', '甲', '助', '窗', '布', '富', '牌', '头', '四', '多', '妆', '吉', '苑', '沙', '恒', '隆', '春', '干', '饼',
    '氏', '里', '二', '管', '诚', '制', '售', '嘉', '长', '轩', '杂', '副', '清', '计', '黄', '讯', '太', '鸭', '号', '街', '交',
    '与', '叉', '附', '近', '层', '旁', '对', '巷', '栋', '环', '省', '桥', '湖', '段', '乡', '厦', '府', '铺', '内', '侧', '元',
    '购', '前', '幢', '滨', '处', '向', '座', '下', '県', '凤', '港', '开', '关', '景', '泉', '塘', '放', '昌', '线', '湾', '政',
    '步', '宁', '解', '白', '田', '町', '溪', '十', '八', '古', '双', '胜', '本', '单', '同', '九', '迎', '第', '台', '玉', '锦',
    '底', '后', '七', '斜', '期', '武', '岭', '松', '角', '纪', '朝', '峰', '六', '振', '珠', '局', '岗', '洲', '横', '边', '济',
    '井', '办', '汉', '代', '临', '弄', '团', '外', '塔', '杨', '铁', '浦', '字', '年', '岛', '陵', '原', '梅', '进', '荣', '友',
    '虹', '央', '桂', '沿', '事', '津', '凯', '莲', '丁', '秀', '柳', '集', '紫', '旗', '张', '谷', '的', '是', '不', '了', '很',
    '还', '个', '也', '这', '我', '就', '在', '以', '可', '到', '错', '没', '去', '过', '感', '次', '要', '比', '觉', '看', '得',
    '说', '常', '真', '们', '但', '最', '喜', '哈', '么', '别', '位', '能', '较', '境', '非', '为', '欢', '然', '他', '挺', '着',
    '价', '那', '意', '种', '想', '出', '员', '两', '推', '做', '排', '实', '分', '间', '甜', '度', '起', '满', '给', '热', '完',
    '格', '荐', '喝', '等', '其', '再', '几', '只', '现', '朋', '候', '样', '直', '而', '买', '于', '般', '豆', '量', '选', '奶',
    '打', '每', '评', '少', '算', '又', '因', '情', '找', '些', '份', '置', '适', '什', '蛋', '师', '气', '你', '姐', '棒', '试',
    '总', '定', '啊', '足', '级', '整', '带', '虾', '如', '态', '且', '尝', '主', '话', '强', '当', '更', '板', '知', '己', '无',
    '酸', '让', '入', '啦', '式', '笑', '赞', '片', '酱', '差', '像', '提', '队', '走', '嫩', '才', '刚', '午', '接', '重', '串',
    '回', '晚', '微', '周', '值', '费', '性', '桌', '拍', '跟', '块', '调', '糕'
]

base_font_dict = {'uniedf6': '1', 'unif299': '2', 'unieab9': '3', 'uniebdc': '4', 'unie97e': '5', 'unif7b7': '6',
                  'unie019': '7', 'unied27': '8', 'unieb7a': '9', 'unie0ba': '0', 'unif2ea': '店', 'unie62b': '中',
                  'unif7e1': '美', 'unif3ff': '家', 'unif0ac': '馆', 'unif1aa': '小', 'unie15b': '车', 'uniec41': '大',
                  'uniee2c': '市', 'unif1ae': '公', 'uniee1b': '酒', 'unie0f2': '行', 'unieef2': '国', 'unie3d7': '品',
                  'unif327': '发', 'unif5d1': '电', 'uniecbd': '金', 'unie03a': '心', 'unif549': '业', 'unied43': '商',
                  'uniec0b': '司', 'uniebf1': '超', 'unieec1': '生', 'unif14f': '装', 'unif436': '园', 'unieaa7': '场',
                  'unie4e9': '食', 'unif305': '有', 'unif773': '新', 'unie332': '限', 'unif43c': '天', 'unie486': '面',
                  'unie6bb': '工', 'unie4c5': '服', 'uniee65': '海', 'unif20b': '华', 'uniee12': '水', 'uniead5': '房',
                  'unif4b1': '饰', 'unieb20': '城', 'unif778': '乐', 'unie689': '汽', 'unif54e': '香', 'unie880': '部',
                  'unie2a9': '利', 'unif655': '子', 'unie81e': '老', 'unie8eb': '艺', 'unif5a3': '花', 'uniec90': '专',
                  'unief3f': '东', 'unif7d2': '肉', 'unie754': '菜', 'unief80': '学', 'unif4c7': '福', 'unie862': '饭',
                  'unie079': '人', 'unie45d': '百', 'unie44d': '餐', 'unieee9': '茶', 'uniebbd': '务', 'unif6fc': '通',
                  'unie4d8': '味', 'unif898': '所', 'unie449': '山', 'unif73d': '区', 'uniebaf': '门', 'uniecd6': '药',
                  'unie723': '银', 'unif475': '农', 'uniee94': '龙', 'unie7a3': '停', 'unie084': '尚', 'unif037': '安',
                  'unieb9c': '广', 'unif3f0': '鑫', 'unie2e8': '一', 'unif3cb': '容', 'uniec98': '动', 'unieada': '南',
                  'unif5be': '具', 'unif292': '源', 'uniea41': '兴', 'uniee7f': '鲜', 'unie882': '记', 'uniefa0': '时',
                  'unie8a7': '机', 'uniebec': '烤', 'unif72a': '文', 'unif03d': '康', 'unie928': '信', 'unie355': '果',
                  'unif460': '阳', 'unieb3d': '理', 'unie662': '锅', 'unie98d': '宝', 'unif1f0': '达', 'unie00b': '地',
                  'unie871': '儿', 'unie317': '衣', 'unif7ba': '特', 'unie129': '产', 'unieb52': '西', 'unif0ed': '批',
                  'unie737': '坊', 'unie848': '州', 'unie9b8': '牛', 'unif391': '佳', 'unie576': '化', 'unieeb8': '五',
                  'uniedd5': '米', 'unif44c': '修', 'unif8d7': '爱', 'unif6f7': '北', 'unif36c': '养', 'uniea67': '卖',
                  'unie212': '建', 'unie04c': '材', 'unieba4': '三', 'unif89d': '会', 'unieea9': '鸡', 'unif866': '室',
                  'unif1d4': '红', 'unie359': '站', 'unif573': '德', 'unieece': '王', 'uniebf6': '光', 'unie348': '名',
                  'unie6ff': '丽', 'unie9a6': '油', 'unie2dc': '院', 'unif7ec': '堂', 'unif59b': '烧', 'unie832': '江',
                  'unif4a5': '社', 'unie695': '合', 'unif84e': '星', 'unie5bd': '货', 'unif493': '型', 'unief73': '村',
                  'unie85f': '自', 'unieabf': '科', 'unif28a': '快', 'unie6a0': '便', 'unied53': '日', 'unie66f': '民',
                  'unie613': '营', 'unif59a': '和', 'unie5bf': '活', 'unieeb0': '童', 'unif4aa': '明', 'unieec7': '器',
                  'unie747': '烟', 'unif8de': '育', 'uniecfa': '宾', 'unie6a4': '精', 'unif806': '屋', 'unif41d': '经',
                  'unie037': '居', 'unie09d': '庄', 'unie750': '石', 'unif2c9': '顺', 'unie17a': '林', 'unie33d': '尔',
                  'unie5d2': '县', 'unif63e': '手', 'unie3b1': '厅', 'unie9f5': '销', 'unief98': '用', 'unie545': '好',
                  'unif0d0': '客', 'unie7f3': '火', 'unie903': '雅', 'uniec4f': '盛', 'unie77d': '体', 'unif555': '旅',
                  'unie945': '之', 'unif535': '鞋', 'uniea86': '辣', 'unif7be': '作', 'unif83b': '粉', 'unif8ed': '包',
                  'unie5c0': '楼', 'uniee4b': '校', 'unie83f': '鱼', 'unief15': '平', 'unif633': '彩', 'unif667': '上',
                  'unie15f': '吧', 'unie8ed': '保', 'unie3f2': '永', 'unie0c8': '万', 'unif0ba': '物', 'unif8f0': '教',
                  'unif8dc': '吃', 'unif355': '设', 'uniee21': '医', 'unif641': '正', 'unie52a': '造', 'unif843': '丰',
                  'unie441': '健', 'unie5f9': '点', 'unif7d3': '汤', 'unie7d2': '网', 'unied23': '庆', 'unie4b8': '技',
                  'unie8e2': '斯', 'unif2b2': '洗', 'unie37d': '料', 'unie1bd': '配', 'unieb83': '汇', 'unif5cc': '木',
                  'unif128': '缘', 'unie078': '加', 'unif6d4': '麻', 'unie288': '联', 'unie2bc': '卫', 'unif629': '川',
                  'unif704': '泰', 'uniec4e': '色', 'unie96f': '世', 'unie3d0': '方', 'uniec7b': '寓', 'unie284': '风',
                  'unie01a': '幼', 'unif5d4': '羊', 'unie9d5': '烫', 'unie5d7': '来', 'unif3ac': '高', 'unieaf1': '厂',
                  'unieec2': '兰', 'unif29d': '阿', 'unie0e4': '贝', 'unieae8': '皮', 'unif09e': '全', 'unif011': '女',
                  'unif70e': '拉', 'unie758': '成', 'unie830': '云', 'unie256': '维', 'unie819': '贸', 'unif7b5': '道',
                  'unie6d1': '术', 'unie153': '运', 'unieb13': '都', 'unif78b': '口', 'uniebe1': '博', 'unif00e': '河',
                  'uniec6c': '瑞', 'unif007': '宏', 'unif27d': '京', 'unief35': '际', 'unif052': '路', 'unie1d2': '祥',
                  'unie726': '青', 'unie2dd': '镇', 'unif219': '厨', 'unif756': '培', 'unie3e7': '力', 'unif21a': '惠',
                  'unie0be': '连', 'uniec99': '马', 'unie535': '鸿', 'unif345': '钢', 'unief78': '训', 'unie7ef': '影',
                  'unie1f0': '甲', 'unie130': '助', 'uniee36': '窗', 'unif5b4': '布', 'unie953': '富', 'unief50': '牌',
                  'unie046': '头', 'unif0bd': '四', 'unie433': '多', 'unif68d': '妆', 'unie230': '吉', 'unie281': '苑',
                  'unif01b': '沙', 'unie4fb': '恒', 'unie860': '隆', 'unif006': '春', 'unie4d2': '干', 'unif285': '饼',
                  'unif249': '氏', 'unif654': '里', 'unie2f9': '二', 'unie32b': '管', 'unif75c': '诚', 'unie79f': '制',
                  'unif84f': '售', 'unie8c0': '嘉', 'unif3aa': '长', 'unif230': '轩', 'unieddf': '杂', 'unif2c6': '副',
                  'unie3d2': '清', 'unied3e': '计', 'uniefc6': '黄', 'unie46a': '讯', 'unie31e': '太', 'unif4ff': '鸭',
                  'uniea14': '号', 'unieb40': '街', 'unie75f': '交', 'unif440': '与', 'unied94': '叉', 'unieef3': '附',
                  'unie47e': '近', 'unif76a': '层', 'unie80e': '旁', 'unie177': '对', 'unie745': '巷', 'unif016': '栋',
                  'uniee88': '环', 'unied93': '省', 'unied7e': '桥', 'unie04f': '湖', 'unif05d': '段', 'unie470': '乡',
                  'uniee6a': '厦', 'unie90f': '府', 'unieee8': '铺', 'unief9f': '内', 'unief6b': '侧', 'unif822': '元',
                  'unie8f3': '购', 'unieacc': '前', 'unie324': '幢', 'unif3ef': '滨', 'uniee3c': '处', 'unif246': '向',
                  'unief4e': '座', 'uniedc6': '下', 'unie965': '県', 'unie209': '凤', 'unie9ac': '港', 'unie018': '开',
                  'unief03': '关', 'unief95': '景', 'unie255': '泉', 'uniee6b': '塘', 'unif38c': '放', 'unieb89': '昌',
                  'unif1d2': '线', 'unieac5': '湾', 'uniefa3': '政', 'unif70c': '步', 'unie53f': '宁', 'uniefdc': '解',
                  'unie7d3': '白', 'unif240': '田', 'uniedfc': '町', 'unif608': '溪', 'unif2c5': '十', 'unie31c': '八',
                  'unie656': '古', 'uniebf3': '双', 'unie393': '胜', 'unif0bf': '本', 'unie2b5': '单', 'unieba7': '同',
                  'unif7da': '九', 'uniee81': '迎', 'unif39c': '第', 'unif369': '台', 'unie2cc': '玉', 'unie1f1': '锦',
                  'unie8cf': '底', 'unie724': '后', 'uniea05': '七', 'unif02b': '斜', 'unif6b9': '期', 'unie21d': '武',
                  'unif871': '岭', 'unif4a4': '松', 'unif89b': '角', 'unif7a8': '纪', 'unieed0': '朝', 'unieea7': '峰',
                  'unie91a': '六', 'unie9f4': '振', 'unie8e0': '珠', 'unie5fc': '局', 'unif507': '岗', 'unie7f2': '洲',
                  'unif585': '横', 'unieff9': '边', 'unif6a9': '济', 'unif274': '井', 'unieb2c': '办', 'uniead9': '汉',
                  'unif180': '代', 'unie546': '临', 'unie530': '弄', 'unif455': '团', 'unif268': '外', 'unie74f': '塔',
                  'unie205': '杨', 'unif03e': '铁', 'unif3f7': '浦', 'unif013': '字', 'unie4ee': '年', 'unie034': '岛',
                  'unie430': '陵', 'unie097': '原', 'unif741': '梅', 'unif142': '进', 'uniec61': '荣', 'unif201': '友',
                  'unie061': '虹', 'uniec93': '央', 'unif213': '桂', 'unif6fe': '沿', 'unied8e': '事', 'unif38a': '津',
                  'unie020': '凯', 'unif81b': '莲', 'uniece1': '丁', 'unieeb7': '秀', 'unieede': '柳', 'unie053': '集',
                  'unif700': '紫', 'unie246': '旗', 'unie217': '张', 'unif1ba': '谷', 'unie918': '的', 'unie2fd': '是',
                  'unie0d6': '不', 'unie4a1': '了', 'unif50d': '很', 'unie595': '还', 'unie13e': '个', 'unie25a': '也',
                  'unie0bd': '这', 'unif162': '我', 'unie841': '就', 'unie73a': '在', 'unif06b': '以', 'uniea20': '可',
                  'unied7b': '到', 'unif72c': '错', 'unie26a': '没', 'unie0e0': '去', 'unif0ce': '过', 'unif0c1': '感',
                  'unif3fa': '次', 'unif1c4': '要', 'unie53c': '比', 'unif867': '觉', 'unif304': '看', 'unie93d': '得',
                  'unie333': '说', 'unie091': '常', 'unie2d9': '真', 'unif816': '们', 'unie1b6': '但', 'unie2a7': '最',
                  'unie786': '喜', 'unie4c0': '哈', 'uniedb7': '么', 'unif8c5': '别', 'unieba1': '位', 'unie927': '能',
                  'unif83f': '较', 'unie83c': '境', 'unie401': '非', 'unie5f8': '为', 'unif126': '欢', 'unie5ae': '然',
                  'unie2a6': '他', 'unie542': '挺', 'unif64f': '着', 'unie0f6': '价', 'unif45f': '那', 'unie0b0': '意',
                  'unie969': '种', 'unie8da': '想', 'unie8e9': '出', 'unie366': '员', 'unie60f': '两', 'unif24d': '推',
                  'unif0a3': '做', 'unif5fd': '排', 'uniee52': '实', 'uniedd8': '分', 'unieca2': '间', 'unie999': '甜',
                  'unief11': '度', 'unif33e': '起', 'unif74c': '满', 'unif1db': '给', 'uniee28': '热', 'unie058': '完',
                  'unie9cc': '格', 'unif872': '荐', 'unieb5c': '喝', 'unief92': '等', 'unie286': '其', 'unie565': '再',
                  'unie642': '几', 'unie8dd': '只', 'unif3a2': '现', 'unie510': '朋', 'uniedeb': '候', 'uniecbe': '样',
                  'unie7c2': '直', 'unie2de': '而', 'unieb00': '买', 'unie369': '于', 'unif661': '般', 'unif636': '豆',
                  'unie048': '量', 'unif87d': '选', 'unie50b': '奶', 'uniee56': '打', 'unie91e': '每', 'unif889': '评',
                  'unie342': '少', 'unie7a0': '算', 'uniea5c': '又', 'unieb35': '因', 'uniefb8': '情', 'unif1c2': '找',
                  'unieab7': '些', 'unif05f': '份', 'unif114': '置', 'unif017': '适', 'unie91b': '什', 'unied18': '蛋',
                  'unif8c7': '师', 'unie877': '气', 'unie821': '你', 'unif623': '姐', 'unie3b9': '棒', 'unie19b': '试',
                  'unif2a1': '总', 'uniea4c': '定', 'uniea2b': '啊', 'unif798': '足', 'unie854': '级', 'unie935': '整',
                  'unief43': '带', 'unif3a0': '虾', 'unied4c': '如', 'unif597': '态', 'unie105': '且', 'uniebfa': '尝',
                  'unif84d': '主', 'unif481': '话', 'unie6ce': '强', 'unif08d': '当', 'unieed4': '更', 'unie174': '板',
                  'unie06c': '知', 'unie7d7': '己', 'uniea17': '无', 'uniecdc': '酸', 'unif5f3': '让', 'unie993': '入',
                  'unif1b7': '啦', 'unieb39': '式', 'unif77e': '笑', 'uniefa4': '赞', 'unie657': '片', 'unif5d0': '酱',
                  'unie7b9': '差', 'unie587': '像', 'unif4d4': '提', 'unied3d': '队', 'unie566': '走', 'unie456': '嫩',
                  'unif296': '才', 'unieaa4': '刚', 'unie6b7': '午', 'unie134': '接', 'uniea94': '重', 'unif5c6': '串',
                  'unif581': '回', 'unie305': '晚', 'unie0bf': '微', 'uniefe7': '周', 'unif7db': '值', 'unie8bf': '费',
                  'unif615': '性', 'unif609': '桌', 'uniebd3': '拍', 'unie5fe': '跟', 'unie89b': '块', 'unieebe': '调',
                  'unieefd': '糕'}

base_dir = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

@retry(stop_max_attempt_number=10)
def get(*args, **kwargs):
    s = requests.session()
    s.keep_alive = False
    response = s.get(*args, **kwargs)
    if response.status_code != 200:
            raise Exception
    return response

class BaseFont():
    def __init__(self, load_history=False, font_path=os.path.join(base_dir, 'font/base.woff')):
        self.base_font = TTFont(font_path)
        self.base_unis = self.base_font.getGlyphOrder()[2:]

        if load_history:
            self.font_dict = self.loadHistoryFont()
        else:
            self.font_dict = base_font_dict

    def dumpFont(self, font_dict, font_path=os.path.join(base_dir, 'font/history/font.json')):
        with open(font_path, 'w') as f:
            f.write(json.dumps(font_dict))

    def loadHistoryFont(self, path=os.path.join(base_dir, 'font/history/font.json')):
        with open(path, 'r', encoding='utf-8') as f:
            return json.loads(f.read())


class Font():
    def __init__(self, load_history=False):
        self.base_font = BaseFont(load_history=load_history)  # type:BaseFont

        if load_history:
            self.font_dict = self.base_font.font_dict
        else:
            self.font_dict = {'num': dict(), 'shopdesc': dict(), 'review': dict(),
                              'address': dict(), 'dishname': dict(), 'hours': dict(),
                              'reviewTag': dict(), 'tagName': dict(), 'shopNum': dict()}

    def loadFont(self, font_type, fontPath):
        font = TTFont(fontPath)
        font_unis = font.getGlyphOrder()[2:]
        for font_uni in font_unis:
            for base_uni in self.base_font.base_unis:
                if self.base_font.base_font['glyf'][base_uni] == font['glyf'][font_uni]:
                    self.font_dict[font_type][font_uni] = self.base_font.font_dict[base_uni]
                    break
        return self.font_dict

    def loadFontFromCSS(self, css: str) -> ...:
        urls = re.compile(',url\("//(.*?\.woff)"\)').findall(css)
        font_types = re.compile('\.(.{3,10}?){').findall(css)
        for font_type, url in zip(font_types, urls):
            filename = url.split('/')[-1]
            path = self._downloadFont(os.path.join(base_dir, 'font/temp/', filename), 'http://' + url)
            if path:
                self.loadFont(font_type, path)
            logging.info('Load {} success!'.format(url))

    def _saveFontDict(self) -> ...:
        if not os.path.exists(os.path.join(base_dir, 'font/history/')):
            os.makedirs(os.path.join(base_dir, 'font/history/'))
        for file in os.listdir(os.path.join(base_dir, 'font/temp/')):
            src = os.path.join(base_dir, 'font/temp/', file)
            if os.path.isfile(src):
                # if os.path.exists(os.path.join(base_dir, 'font/history/', file)): continue
                shutil.move(src, os.path.join(base_dir, 'font/history/', file))
        self.base_font.dumpFont(self.font_dict)
        if sys.platform == 'win32':
            logging.info('Font dict save in {}'.format(os.path.join(base_dir, r'font\history\font.json')))
        else:
            logging.info('Font dict save in {}'.format(os.path.join(base_dir, 'font/history/font.json')))

    def parseFontChar(self, code: str, font_type: str) -> str:
        if not code.startswith(r'&#x'):
            return code
        if font_type == 'shopNum': font_type = 'reviewTag'
        return self.font_dict[font_type]['uni' + code[-5:-1]]

    def parseFont(self, code_list: List[str], font_type: str) -> str:
        s = ''
        for code in code_list:
            if code: s += self.parseFontChar(code, font_type)
        return s

    def delTemp(self):
        temp_dir = os.path.join(base_dir, 'font/temp/')
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    def _downloadFont(self, path, url):
        filePath, filename = os.path.split(path)
        if os.path.exists(path):
            return
        if not os.path.exists(filePath):
            os.makedirs(filePath)
        response = get(url, timeout=5)
        with open(path, 'wb') as f:
            f.write(response.content)
        return path

    def __del__(self):
        self.delTemp()


s = """
@font-face{font-family: "PingFangSC-Regular-tagName";src:url("//s3plus.meituan.net/v1/mss_73a511b8f91f43d0bdae92584ea6330b/font/8d6e14c5.eot");src:url("//s3plus.meituan.net/v1/mss_73a511b8f91f43d0bdae92584ea6330b/font/8d6e14c5.eot?#iefix") format("embedded-opentype"),url("//s3plus.meituan.net/v1/mss_73a511b8f91f43d0bdae92584ea6330b/font/8d6e14c5.woff");} .tagName{font-family: 'PingFangSC-Regular-tagName';}@font-face{font-family: "PingFangSC-Regular-address";src:url("//s3plus.meituan.net/v1/mss_73a511b8f91f43d0bdae92584ea6330b/font/6d7cc272.eot");src:url("//s3plus.meituan.net/v1/mss_73a511b8f91f43d0bdae92584ea6330b/font/6d7cc272.eot?#iefix") format("embedded-opentype"),url("//s3plus.meituan.net/v1/mss_73a511b8f91f43d0bdae92584ea6330b/font/6d7cc272.woff");} .address{font-family: 'PingFangSC-Regular-address';}@font-face{font-family: "PingFangSC-Regular-reviewTag";src:url("//s3plus.meituan.net/v1/mss_73a511b8f91f43d0bdae92584ea6330b/font/6d7cc272.eot");src:url("//s3plus.meituan.net/v1/mss_73a511b8f91f43d0bdae92584ea6330b/font/6d7cc272.eot?#iefix") format("embedded-opentype"),url("//s3plus.meituan.net/v1/mss_73a511b8f91f43d0bdae92584ea6330b/font/6d7cc272.woff");} .reviewTag{font-family: 'PingFangSC-Regular-reviewTag';}@font-face{font-family: "PingFangSC-Regular-shopNum";src:url("//s3plus.meituan.net/v1/mss_73a511b8f91f43d0bdae92584ea6330b/font/d5dc3c57.eot");src:url("//s3plus.meituan.net/v1/mss_73a511b8f91f43d0bdae92584ea6330b/font/d5dc3c57.eot?#iefix") format("embedded-opentype"),url("//s3plus.meituan.net/v1/mss_73a511b8f91f43d0bdae92584ea6330b/font/d5dc3c57.woff");} .shopNum{font-family: 'PingFangSC-Regular-shopNum';}
"""
# f = Font()
# f.loadFontFromCSS(s)
# f._saveFontDict()
# print(len(f.font_dict))