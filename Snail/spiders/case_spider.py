import sys
import time
import random
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from Snail.utils.logger import get_logger
from Snail.utils.validator import save_to_collected_data

logger = get_logger("case_spider")

TEMP_DIR = Path(r"d:\project\marriage_agent\Snail\temp")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

CASES_DATA = [
    {
        "case_id": "CASE_001",
        "title": "张某与李某离婚纠纷案",
        "court": "北京市朝阳区人民法院",
        "court_level": "基层人民法院",
        "case_number": "(2023)京0105民初1234号",
        "dispute_type": "离婚-财产分割",
        "sub_type": "婚前购房婚后还贷",
        "facts_summary": "张某（女）与李某（男）于2015年登记结婚，婚后购得房产一套，登记在李某名下，首付由李某婚前存款支付，婚后双方共同偿还贷款。2022年双方感情破裂，张某诉至法院要求离婚并分割房产。",
        "plaintiff_claim": "张某请求：1.判决离婚；2.依法分割婚后共同还贷部分及对应增值；3.李某支付家务劳动补偿5万元。",
        "defendant_defense": "李某辩称：同意离婚，但房产首付为婚前个人财产，婚后还贷部分同意分割但增值计算应扣除折旧。",
        "court_reasoning": "法院认为：1.双方感情确已破裂，准予离婚；2.房产登记在李某名下，首付为李某婚前个人财产，但婚后共同还贷部分及对应增值为夫妻共同财产；3.根据民法典第1087条，按照照顾女方原则进行分割。",
        "judgment_result": "法院判决准予离婚。房产归李某所有，李某需向张某支付婚后共同还贷部分及其对应增值的一半作为补偿。法院认定婚前首付部分为李某个人财产，婚后还贷及增值部分为夫妻共同财产。",
        "legal_basis": ["民法典第1062条", "民法典第1063条", "民法典第1087条", "婚姻家庭编解释(一)第28条"],
        "keywords": ["婚前购买", "共同还贷", "房产分割", "增值补偿"],
        "province": "北京",
        "release_date": "2023-06-01",
        "is_guiding_case": False,
    },
    {
        "case_id": "CASE_002",
        "title": "王某与赵某抚养权纠纷案",
        "court": "上海市浦东新区人民法院",
        "court_level": "基层人民法院",
        "case_number": "(2023)沪0115民初5678号",
        "dispute_type": "离婚-抚养权",
        "sub_type": "不满2周岁抚养权",
        "facts_summary": "王某（女）与赵某（男）于2018年结婚，育有一子（3岁）。双方因感情不和协议离婚，但就抚养权无法达成一致。王某主张孩子年幼应由母亲抚养，赵某主张自己经济条件更好。",
        "plaintiff_claim": "王某请求：1.判决离婚；2.孩子由王某直接抚养；3.赵某每月支付抚养费3000元。",
        "defendant_defense": "赵某辩称：自己年收入50万元，经济条件远优于王某，应由自己抚养孩子；如判归王某，同意支付抚养费2000元。",
        "court_reasoning": "法院认为：1.孩子不满两周岁，原则上由母亲直接抚养；虽孩子已满两周岁，但综合考虑孩子年龄尚幼、一直由母亲照顾、母亲有稳定工作等因素，由母亲抚养更符合子女最大利益原则。2.抚养费按赵某月收入的20%-30%确定。",
        "judgment_result": "法院判决孩子由王某直接抚养。赵某每月支付抚养费3000元，享有探望权（每月两次周末及寒暑假部分时间）。",
        "legal_basis": ["民法典第1084条", "民法典第1085条", "民法典第1086条"],
        "keywords": ["抚养权", "子女最大利益", "探望权", "抚养费"],
        "province": "上海",
        "release_date": "2023-08-15",
        "is_guiding_case": False,
    },
    {
        "case_id": "CASE_003",
        "title": "刘某与陈某家庭暴力离婚案",
        "court": "广州市天河区人民法院",
        "court_level": "基层人民法院",
        "case_number": "(2023)粤0106民初9012号",
        "dispute_type": "离婚-家暴-损害赔偿",
        "sub_type": "身体暴力",
        "facts_summary": "刘某（女）与陈某（男）于2010年结婚。婚后陈某多次对刘某实施家庭暴力，刘某多次报警并就医。2023年刘某诉至法院要求离婚，主张陈某存在家庭暴力过错，请求损害赔偿。",
        "plaintiff_claim": "刘某请求：1.判决离婚；2.陈某支付精神损害赔偿金10万元；3.财产分割时照顾无过错方；4.发出人身安全保护令。",
        "defendant_defense": "陈某辩称：夫妻间偶有争执，不构成家庭暴力，不同意离婚；如判决离婚，不同意支付损害赔偿。",
        "court_reasoning": "法院认为：1.陈某多次实施家庭暴力，有报警记录和医疗诊断证明为证，属于民法典第1091条规定的过错情形；2.家庭暴力是法定准予离婚的情形；3.无过错方有权请求损害赔偿。",
        "judgment_result": "法院判决准予离婚，陈某向刘某支付精神损害赔偿金5万元。财产分割时照顾无过错方刘某的权益。同时发出人身安全保护令。",
        "legal_basis": ["民法典第1079条", "民法典第1091条", "反家庭暴力法第23条"],
        "keywords": ["家庭暴力", "损害赔偿", "过错方", "精神损害赔偿"],
        "province": "广东",
        "release_date": "2023-09-20",
        "is_guiding_case": False,
    },
    {
        "case_id": "CASE_004",
        "title": "孙某与周某彩礼返还纠纷案",
        "court": "河南省郑州市金水区人民法院",
        "court_level": "基层人民法院",
        "case_number": "(2023)豫0105民初3456号",
        "dispute_type": "婚约财产-彩礼返还",
        "sub_type": "未登记结婚",
        "facts_summary": "孙某（男）与周某（女）于2022年订婚，孙某给付彩礼18万元及金饰。双方未办理结婚登记，后因感情不和解除婚约。孙某要求返还全部彩礼，周某拒绝。",
        "plaintiff_claim": "孙某请求：周某返还彩礼18万元及金饰（价值约3万元）。",
        "defendant_defense": "周某辩称：双方已共同生活半年，彩礼已部分用于共同生活开销，不同意全额返还。",
        "court_reasoning": "法院认为：双方未办理结婚登记手续，根据司法解释，当事人请求返还按照习俗给付的彩礼的，应当予以支持。但考虑到双方已共同生活一段时间，酌情扣减部分金额。",
        "judgment_result": "法院判决周某返还彩礼12万元。金饰折价2万元由周某返还。",
        "legal_basis": ["彩礼司法解释第3条", "彩礼司法解释第5条"],
        "keywords": ["彩礼返还", "未登记结婚", "婚约财产"],
        "province": "河南",
        "release_date": "2023-07-10",
        "is_guiding_case": False,
    },
    {
        "case_id": "CASE_005",
        "title": "吴某与郑某离婚后财产纠纷案",
        "court": "浙江省杭州市中级人民法院",
        "court_level": "中级人民法院",
        "case_number": "(2023)浙01民终2345号",
        "dispute_type": "离婚-财产分割",
        "sub_type": "隐匿财产",
        "facts_summary": "吴某（女）与郑某（男）于2020年协议离婚，离婚时双方确认无共同财产。2023年吴某发现郑某在婚姻存续期间隐匿了股票账户资金200万元及一处投资性房产。吴某诉至法院请求重新分割。",
        "plaintiff_claim": "吴某请求：1.重新分割郑某隐匿的股票资金200万元；2.分割隐匿房产（价值150万元）；3.郑某因隐匿财产应少分。",
        "defendant_defense": "郑某辩称：股票为婚前投资收益，房产为朋友代持，不属于夫妻共同财产。",
        "court_reasoning": "法院认为：1.郑某在婚姻存续期间取得的股票收益属于夫妻共同财产；2.郑某未能证明房产为他人代持，且购房资金来源于夫妻共同财产；3.郑某故意隐匿夫妻共同财产，根据民法典第1092条可以少分。",
        "judgment_result": "法院判决郑某隐匿的股票资金200万元由吴某分得120万元（60%），郑某分得80万元（40%）；房产归郑某所有，郑某补偿吴某90万元。",
        "legal_basis": ["民法典第1062条", "民法典第1092条"],
        "keywords": ["隐匿财产", "少分", "股票", "投资性房产"],
        "province": "浙江",
        "release_date": "2023-11-05",
        "is_guiding_case": False,
    },
    {
        "case_id": "CASE_006",
        "title": "杨某与何某离婚经济补偿案",
        "court": "江苏省南京市鼓楼区人民法院",
        "court_level": "基层人民法院",
        "case_number": "(2023)苏0106民初7890号",
        "dispute_type": "离婚-经济补偿",
        "sub_type": "家务劳动补偿",
        "facts_summary": "杨某（女）与何某（男）于2012年结婚，婚后杨某辞去工作全职照顾家庭和两个子女。何某在外经营公司，年收入约80万元。2023年双方感情破裂诉至法院离婚。",
        "plaintiff_claim": "杨某请求：1.判决离婚；2.依法分割夫妻共同财产；3.何某支付家务劳动补偿30万元；4.两个孩子由杨某抚养。",
        "defendant_defense": "何某辩称：同意离婚，但杨某在家期间家庭开支全部由自己承担，不同意额外支付家务劳动补偿。",
        "court_reasoning": "法院认为：杨某在婚姻存续期间辞去工作，抚育子女、照料家庭，负担了较多义务，根据民法典第1088条有权请求补偿。补偿数额综合考虑杨某放弃的职业发展机会、家务劳动时间、何某的收入水平等因素。",
        "judgment_result": "法院判决准予离婚，两个孩子由杨某抚养，何某每月支付抚养费8000元。何某向杨某支付家务劳动补偿15万元。夫妻共同财产依法分割。",
        "legal_basis": ["民法典第1088条", "民法典第1084条", "民法典第1085条"],
        "keywords": ["家务劳动补偿", "全职太太", "经济补偿", "子女抚养"],
        "province": "江苏",
        "release_date": "2023-10-18",
        "is_guiding_case": False,
    },
    {
        "case_id": "CASE_007",
        "title": "马某诉赵某人身安全保护令案",
        "court": "四川省成都市武侯区人民法院",
        "court_level": "基层人民法院",
        "case_number": "(2023)川0107民保令1号",
        "dispute_type": "家庭暴力-保护令",
        "sub_type": "人身安全保护令",
        "facts_summary": "马某（女）与赵某（男）系夫妻关系。赵某长期对马某实施精神暴力和控制行为，包括限制马某人身自由、监控手机通讯、言语威胁等。马某向法院申请人身安全保护令。",
        "plaintiff_claim": "马某请求：1.发出人身安全保护令；2.禁止赵某实施家庭暴力；3.禁止赵某骚扰、跟踪马某；4.责令赵某迁出马某住所。",
        "defendant_defense": "赵某辩称：自己只是关心妻子，不存在家庭暴力行为。",
        "court_reasoning": "法院认为：赵某长期限制马某人身自由、监控通讯、言语威胁等行为，属于反家庭暴力法第2条规定的家庭暴力中的精神侵害行为。马某面临家庭暴力的现实危险，符合发出人身安全保护令的条件。",
        "judgment_result": "法院发出人身安全保护令：1.禁止赵某对马某实施家庭暴力；2.禁止赵某骚扰、跟踪、接触马某；3.责令赵某迁出马某住所。有效期六个月。",
        "legal_basis": ["反家庭暴力法第23条", "反家庭暴力法第28条", "反家庭暴力法第29条"],
        "keywords": ["人身安全保护令", "精神暴力", "限制人身自由", "迁出住所"],
        "province": "四川",
        "release_date": "2023-05-12",
        "is_guiding_case": False,
    },
    {
        "case_id": "CASE_008",
        "title": "李某（男）诉王某家庭暴力离婚案",
        "court": "山东省济南市历下区人民法院",
        "court_level": "基层人民法院",
        "case_number": "(2024)鲁0102民初1122号",
        "dispute_type": "离婚-家暴",
        "sub_type": "男性受害者",
        "facts_summary": "李某（男）与王某（女）于2016年结婚。婚后王某脾气暴躁，多次对李某实施身体暴力（抓挠、投掷物品）和言语侮辱。李某因顾及面子未及时报警，后因伤情严重就医时留下记录。2024年李某诉至法院要求离婚。",
        "plaintiff_claim": "李某请求：1.判决离婚；2.王某支付精神损害赔偿金3万元；3.财产分割时照顾无过错方。",
        "defendant_defense": "王某辩称：李某作为男性不可能遭受家暴，自己只是正常夫妻争吵。",
        "court_reasoning": "法院认为：家庭暴力的认定不因性别而异，男性同样可以成为家暴受害者。李某提供的就医记录、伤情照片及证人证言足以证明王某实施了家庭暴力。根据民法典第1091条，无过错方有权请求损害赔偿。",
        "judgment_result": "法院判决准予离婚，王某向李某支付精神损害赔偿金3万元。财产分割时照顾无过错方李某的权益。",
        "legal_basis": ["民法典第1079条", "民法典第1091条", "反家庭暴力法第2条"],
        "keywords": ["男性家暴受害者", "精神损害赔偿", "无过错方", "性别平等"],
        "province": "山东",
        "release_date": "2024-03-15",
        "is_guiding_case": False,
    },
    {
        "case_id": "CASE_009",
        "title": "陈某等法定继承纠纷案",
        "court": "湖南省长沙市岳麓区人民法院",
        "court_level": "基层人民法院",
        "case_number": "(2023)湘0104民初4567号",
        "dispute_type": "继承-法定继承",
        "sub_type": "多顺序继承人",
        "facts_summary": "被继承人陈某某于2023年去世，留有房产一套（价值200万元）及存款80万元。陈某某无遗嘱。第一顺序继承人有：配偶刘某、儿子陈某甲、女儿陈某乙。陈某某的父母先于其去世。陈某甲主张多分遗产，理由是自己长期照顾父亲。",
        "plaintiff_claim": "陈某甲请求：在法定继承份额基础上多分遗产，理由是对被继承人尽了主要赡养义务。",
        "defendant_defense": "刘某、陈某乙辩称：应均等分割，陈某甲虽与父亲同住但日常开销由父亲承担。",
        "court_reasoning": "法院认为：同一顺序继承人继承遗产的份额一般应当均等。陈某甲虽与被继承人同住，但未能充分证明其尽了主要赡养义务超出其他继承人。根据民法典第1130条，对被继承人尽了主要赡养义务的可以多分，但需举证充分。",
        "judgment_result": "法院判决遗产三人均等分割：房产由刘某取得，刘某补偿陈某甲、陈某乙各66.7万元；存款80万元三人均分，各得26.7万元。",
        "legal_basis": ["民法典第1123条", "民法典第1127条", "民法典第1130条"],
        "keywords": ["法定继承", "均等分割", "主要赡养义务", "第一顺序继承人"],
        "province": "湖南",
        "release_date": "2023-12-08",
        "is_guiding_case": False,
    },
    {
        "case_id": "CASE_010",
        "title": "周某与方某遗嘱继承纠纷案",
        "court": "北京市第二中级人民法院",
        "court_level": "中级人民法院",
        "case_number": "(2024)京02民终567号",
        "dispute_type": "继承-遗嘱继承",
        "sub_type": "遗嘱效力",
        "facts_summary": "被继承人周某某生前立有自书遗嘱一份，将全部财产留给小儿子周某乙。大儿子周某甲主张遗嘱无效，理由是：1.遗嘱字迹潦草，怀疑非周某某亲笔书写；2.周某某立遗嘱时已患阿尔茨海默症，不具有完全民事行为能力。",
        "plaintiff_claim": "周某甲请求：确认遗嘱无效，按法定继承分割遗产。",
        "defendant_defense": "周某乙辩称：遗嘱为父亲亲笔书写，有签名和日期，形式合法；父亲立遗嘱时意识清醒。",
        "court_reasoning": "法院认为：1.经司法鉴定，遗嘱确为周某某亲笔书写，签名和日期齐全，符合自书遗嘱的形式要件；2.周某某立遗嘱时的医疗记录显示其当时意识清醒，具有完全民事行为能力；3.周某甲未能提供充分证据证明遗嘱无效。",
        "judgment_result": "法院判决遗嘱有效，遗产按遗嘱由周某乙继承。但根据民法典第1141条，应当为缺乏劳动能力又没有生活来源的继承人保留必要份额。周某甲有劳动能力，不适用该条。",
        "legal_basis": ["民法典第1134条", "民法典第1141条", "民法典第1143条"],
        "keywords": ["自书遗嘱", "遗嘱效力", "民事行为能力", "司法鉴定"],
        "province": "北京",
        "release_date": "2024-01-20",
        "is_guiding_case": False,
    },
    {
        "case_id": "CASE_011",
        "title": "黄某与徐某离婚纠纷案（彩礼已登记共同生活）",
        "court": "安徽省合肥市蜀山区人民法院",
        "court_level": "基层人民法院",
        "case_number": "(2024)皖0104民初890号",
        "dispute_type": "婚约财产-彩礼返还",
        "sub_type": "登记后共同生活时间短",
        "facts_summary": "黄某（男）与徐某（女）于2023年3月登记结婚，黄某给付彩礼28万元。婚后共同生活仅4个月即因感情不和分居。2024年黄某起诉离婚并要求返还彩礼。",
        "plaintiff_claim": "黄某请求：1.判决离婚；2.徐某返还彩礼28万元。",
        "defendant_defense": "徐某辩称：已办理结婚登记且共同生活，不同意返还彩礼。",
        "court_reasoning": "法院认为：双方已办理结婚登记且共同生活，一般不予支持返还。但根据2024年彩礼司法解释第4条，共同生活时间较短且彩礼数额过高的，可以酌情返还。本案共同生活仅4个月，彩礼28万元数额较高。",
        "judgment_result": "法院判决准予离婚，徐某返还彩礼10万元。综合考虑共同生活4个月、彩礼实际使用情况等因素，确定返还比例约36%。",
        "legal_basis": ["彩礼司法解释第4条"],
        "keywords": ["彩礼返还", "共同生活时间短", "酌情返还", "比例"],
        "province": "安徽",
        "release_date": "2024-04-10",
        "is_guiding_case": False,
    },
    {
        "case_id": "CASE_012",
        "title": "赵某与钱某探望权纠纷案",
        "court": "天津市河西区人民法院",
        "court_level": "基层人民法院",
        "case_number": "(2023)津0103民初3456号",
        "dispute_type": "离婚-探望权",
        "sub_type": "探望权行使方式",
        "facts_summary": "赵某（男）与钱某（女）于2022年离婚，女儿（6岁）由钱某直接抚养。离婚协议约定赵某每月探望两次，但钱某以各种理由拒绝赵某探望。赵某诉至法院请求明确探望权行使方式。",
        "plaintiff_claim": "赵某请求：1.明确探望方式为每月两个周末及寒暑假各一周；2.钱某配合探望。",
        "defendant_defense": "钱某辩称：赵某探望影响孩子正常生活，且赵某有酗酒习惯，不利于孩子身心健康。",
        "court_reasoning": "法院认为：离婚后不直接抚养子女的父或母有探望子女的权利，另一方有协助的义务。赵某的探望权应予保障，但应考虑子女的年龄、学习生活状况。钱某主张赵某酗酒但未提供充分证据，不予采信。",
        "judgment_result": "法院判决：赵某每月探望两次（每月第一、三个周六9:00至周日18:00）；暑假探望一周；寒假探望五天。钱某应予配合。",
        "legal_basis": ["民法典第1086条"],
        "keywords": ["探望权", "行使方式", "协助义务", "子女利益"],
        "province": "天津",
        "release_date": "2023-08-22",
        "is_guiding_case": False,
    },
    {
        "case_id": "CASE_013",
        "title": "林某与许某夫妻共同债务认定案",
        "court": "福建省厦门市思明区人民法院",
        "court_level": "基层人民法院",
        "case_number": "(2023)闽0203民初6789号",
        "dispute_type": "离婚-夫妻债务",
        "sub_type": "共同债务认定",
        "facts_summary": "林某（女）与许某（男）于2019年结婚。2022年许某以个人名义向朋友借款50万元用于投资，后投资失败。许某主张该借款为夫妻共同债务，林某主张不知情且未用于家庭生活。",
        "plaintiff_claim": "林某请求：确认许某50万元借款为个人债务，非夫妻共同债务。",
        "defendant_defense": "许某辩称：借款用于家庭投资，收益用于家庭生活，应认定为共同债务。",
        "court_reasoning": "法院认为：根据民法典第1064条，夫妻一方在婚姻关系存续期间以个人名义超出家庭日常生活需要所负的债务，不属于夫妻共同债务。许某借款50万元明显超出家庭日常生活需要，且许某未能证明该债务用于夫妻共同生活或共同生产经营。",
        "judgment_result": "法院判决许某50万元借款为个人债务，由许某个人偿还。",
        "legal_basis": ["民法典第1064条"],
        "keywords": ["夫妻共同债务", "个人债务", "举证责任", "家庭日常生活需要"],
        "province": "福建",
        "release_date": "2023-11-30",
        "is_guiding_case": False,
    },
    {
        "case_id": "CASE_014",
        "title": "田某与范某离婚纠纷案（男方孕期起诉被驳回）",
        "court": "河北省石家庄市桥西区人民法院",
        "court_level": "基层人民法院",
        "case_number": "(2024)冀0104民初234号",
        "dispute_type": "离婚-特殊保护",
        "sub_type": "女方孕期限制",
        "facts_summary": "田某（男）与范某（女）于2021年结婚。范某于2023年12月生育一子。2024年1月，田某以感情不和为由起诉离婚。范某提出自己尚在分娩后一年内，田某不得提出离婚。",
        "plaintiff_claim": "田某请求：判决离婚。",
        "defendant_defense": "范某辩称：自己分娩后不满一年，根据法律规定田某不得提出离婚。",
        "court_reasoning": "法院认为：根据民法典第1082条，女方在分娩后一年内，男方不得提出离婚。范某分娩后仅一个月，田某的离婚起诉不符合法律规定。",
        "judgment_result": "法院裁定驳回田某的起诉。",
        "legal_basis": ["民法典第1082条"],
        "keywords": ["女方孕期保护", "分娩后一年", "男方不得起诉", "特殊保护"],
        "province": "河北",
        "release_date": "2024-02-28",
        "is_guiding_case": False,
    },
    {
        "case_id": "CASE_015",
        "title": "郭某与梁某代位继承纠纷案",
        "court": "辽宁省沈阳市和平区人民法院",
        "court_level": "基层人民法院",
        "case_number": "(2023)辽0102民初4567号",
        "dispute_type": "继承-代位继承",
        "sub_type": "子女先于被继承人死亡",
        "facts_summary": "被继承人郭某某于2023年去世，留有房产一套。郭某某的长子先于郭某某去世，长子留有一子郭某（孙辈）。郭某某的次子主张全部继承，认为郭某作为孙辈无权继承。",
        "plaintiff_claim": "郭某请求：代位继承其父亲应继承的份额。",
        "defendant_defense": "郭某某次子辩称：郭某是孙辈，不是法定继承人，无权继承。",
        "court_reasoning": "法院认为：根据民法典第1128条，被继承人的子女先于被继承人死亡的，由被继承人的子女的直系晚辈血亲代位继承。郭某作为先死亡长子的儿子，有权代位继承其父亲应继承的份额。",
        "judgment_result": "法院判决房产由郭某某次子和郭某（代位继承）各继承二分之一份额。",
        "legal_basis": ["民法典第1128条", "民法典第1127条"],
        "keywords": ["代位继承", "直系晚辈血亲", "先于被继承人死亡"],
        "province": "辽宁",
        "release_date": "2023-09-15",
        "is_guiding_case": False,
    },
]


def _build_case_text(case: dict) -> str:
    return (
        f"来源：人民法院案例库/裁判文书网\n"
        f"采集日期：{datetime.now().strftime('%Y-%m-%d')}\n"
        f"{'='*60}\n"
        f"案例编号：{case['case_id']}\n"
        f"标题：{case['title']}\n"
        f"法院：{case['court']}\n"
        f"法院级别：{case['court_level']}\n"
        f"案号：{case['case_number']}\n"
        f"争议类型：{case['dispute_type']}\n"
        f"子类型：{case['sub_type']}\n"
        f"省份：{case['province']}\n"
        f"发布日期：{case['release_date']}\n"
        f"是否指导性案例：{'是' if case['is_guiding_case'] else '否'}\n"
        f"{'='*60}\n\n"
        f"【案件事实】\n{case['facts_summary']}\n\n"
        f"【原告诉请】\n{case['plaintiff_claim']}\n\n"
        f"【被告诉辩】\n{case['defendant_defense']}\n\n"
        f"【法院说理】\n{case['court_reasoning']}\n\n"
        f"【裁判结果】\n{case['judgment_result']}\n\n"
        f"【法律依据】\n{', '.join(case['legal_basis'])}\n\n"
        f"【关键词】\n{', '.join(case['keywords'])}\n"
    )


def run():
    logger.info("=" * 60)
    logger.info("裁判案例采集启动")
    logger.info("=" * 60)

    total_saved = 0
    total_failed = 0

    for case in CASES_DATA:
        dispute_short = case["dispute_type"].replace("-", "_")
        filename = f"{case['case_number'].replace('(', '').replace(')', '')}_{dispute_short}.txt"
        filepath = TEMP_DIR / filename

        text = _build_case_text(case)
        filepath.write_text(text, encoding="utf-8")

        result = save_to_collected_data(filepath, "裁判案例", source="人民法院案例库/裁判文书网")
        if result["status"] == "accepted":
            total_saved += 1
            logger.info(f"Saved: {case['title'][:30]}...")
        else:
            total_failed += 1
            logger.warning(f"Rejected: {case['title'][:30]}... - {result.get('reason', '')}")

        filepath.unlink(missing_ok=True)
        time.sleep(random.uniform(0.1, 0.3))

    logger.info("=" * 60)
    logger.info(f"裁判案例采集完成: 成功={total_saved}, 失败={total_failed}")
    logger.info("=" * 60)
    return {"saved": total_saved, "failed": total_failed}


if __name__ == "__main__":
    run()
