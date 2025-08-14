from PIL import Image, ImageEnhance
import os

# 取消像素限制，允许加载大图片
Image.MAX_IMAGE_PIXELS = None

# 获取基准图片的尺寸
def get_sample_image_size(sample_folder):
    for filename in os.listdir(sample_folder):
        if filename.endswith(".png") or filename.endswith(".jpg"):
            sample_image_path = os.path.join(sample_folder, filename)
            with Image.open(sample_image_path) as sample_image:
                return sample_image.size
    raise FileNotFoundError("未找到有效的图片文件")

# 定义身高等级对应的缩放比例
height_scaling = {
    1: 0.9,
    2: 0.925,
    3: 0.95,
    4: 0.975,
    5: 1.00,
    6: 1.05
}

# 定义每排的透视缩放比例
perspective_scaling = {
    0: 1.00,  # 第一排
    1: 0.97,  # 第二排
    2: 0.95,  # 第三排
    3: 0.90,  # 第四排
    4: 0.85   # 第五排
}

# 为每个人名关联一个身高等级（按顺序）
name_height_data = {
    "萨本栋": 5, "陈达": 1, "茅以升": 2, "竺可桢": 2, "张元济": 2, "朱家骅": 5, "王宠惠": 4, "胡适": 3, "李书华": 4, "饶毓泰": 2, "庄长恭": 3,
    "周鲠生": 1, "冯友兰": 3, "杨钟健": 3, "汤佩松": 4, "陶孟和": 4, "凌鸿勋": 5, "袁贻瑾": 5, "吴学周": 1, "汤用彤": 1,
    "余嘉锡": 3, "梁思成": 1, "秉志": 5, "周仁": 4, "萧公权": 1, "严济慈": 4, "叶企孙": 3, "李先闻": 2,
    "杨树达": 3, "谢家荣": 4, "李宗恩": 3, "伍献文": 3, "陈垣": 1, "胡先骕": 2, "李济": 5, "戴芳澜": 4, "苏步青": 3,
    "邓叔群": 5, "吴定良": 4, "俞大绂": 2, "陈省身": 5, "殷宏章": 5, "钱崇澍": 5, "柳诒徵": 1, "冯德培": 3, "傅斯年": 2, "贝时璋": 2, "姜立夫": 5
}

# 根据身高和透视比例调整图像大小
def expand_image_by_height_and_perspective(image, target_size, height_level, perspective_level):
    height_scale = height_scaling.get(height_level, 1.0)  # 获取身高缩放比例
    perspective_scale = perspective_scaling.get(perspective_level, 1.0)  # 获取透视缩放比例
    
    # 计算组合后的放大/缩小比例
    combined_scale = height_scale * perspective_scale
    print(f"【Debug】height_level={height_level}, perspective_level={perspective_level}, height_scale={height_scale}, perspective_scale={perspective_scale}, combined_scale={combined_scale}")
    
    original_width, original_height = image.size
    target_width, target_height = target_size
    
    # 综合缩放比例后的高度计算
    scaled_height = int(original_height * combined_scale)
    scale_ratio = min(target_width / original_width, scaled_height / original_height)

    # 最终调整图像大小
    new_width = int(original_width * scale_ratio)
    new_height = int(original_height * scale_ratio)
    print(f"【Debug】缩放后尺寸: new_width={new_width}, new_height={new_height}, combined_scale={combined_scale}")
    
    resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # 创建和目标尺寸相同的背景，并将调整后的图像居中贴到背景上
    new_image = Image.new("RGBA", target_size, (255, 255, 255, 0))
    x_offset = (target_width - new_width) // 2
    y_offset = target_height - new_height  # 底部对齐
    new_image.paste(resized_image, (x_offset, y_offset), resized_image)
    
    return new_image

# 合成图片，添加每一排不同的列间距参数
def create_composite_image(image_data, row_sizes, row_spacing_factor, col_spacing_factors, background_color, row_offsets):
    max_height = max(image.size[1] for _, image in image_data)
    max_width = max(image.size[0] for _, image in image_data)
    max_size = (max_width, max_height)
    
    # 确保背景颜色的RGB(A)值为整数
    background_color = tuple(int(c) for c in background_color)

    row_spacing = int(max_height * row_spacing_factor)
    total_height = len(row_sizes) * max_height + (len(row_sizes) - 1) * row_spacing
    max_row_width = max([row_size * max_width + (row_size - 1) * col_spacing_factors[row] for row, row_size in enumerate(row_sizes)])

    composite = Image.new('RGBA', (max_row_width, total_height), background_color)

    image_index = 0
    y_offset = total_height - max_height
    for row, row_size in enumerate(row_sizes):
        # 直接使用整数的 col_spacing_factors 输入值
        row_width = row_size * max_width + (row_size - 1) * col_spacing_factors[row]
        x_offset = (max_row_width - row_width) // 2 + row_offsets[row]

        for i in range(row_size):
            if image_index < len(image_data):
                name, image = image_data[image_index]
                
                # 获取该图片的身高和透视缩放比例
                height_level = name_height_data.get(name, 5)  # 使用姓名获取身高等级，默认等级为5
                perspective_level = row  # 当前排数对应的透视等级
                
                # 调用调整图片大小的函数
                image = expand_image_by_height_and_perspective(image, max_size, height_level, perspective_level)
                
                composite.paste(image, (x_offset, y_offset), image)
                x_offset += max_width + col_spacing_factors[row]
                image_index += 1
        
        y_offset -= max_height + row_spacing
    
    return composite


# 调整图像亮度
def adjust_brightness(image, factor):
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(factor)

# 读取文件夹内所有符合条件的图片，按修改时间排序
def load_images(folder):
    images = []
    for filename in os.listdir(folder):
        if (filename.endswith(".png") or filename.endswith(".jpg")) and "demo" not in filename:
            filepath = os.path.join(folder, filename)
            img = Image.open(filepath)
            modified_time = os.path.getmtime(filepath)
            images.append((filename, img, modified_time))
    
    images.sort(key=lambda x: x[2])
    return images

# 更新的图片排序逻辑，删除人名中的空格以匹配文件名
def arrange_images_in_order(images):
    ordered_names = [
        "萨本栋", "陈达", "茅以升", "竺可桢", "张元济", "朱家骅", "王宠惠", "胡适", "李书华", "饶毓泰", "庄长恭",
        "周鲠生", "冯友兰", "杨钟健", "汤佩松", "陶孟和", "凌鸿勋", "袁贻瑾", "吴学周", "汤用彤",
        "余嘉锡", "梁思成", "秉志", "周仁", "萧公权", "严济慈", "叶企孙", "李先闻",
        "杨树达", "谢家荣", "李宗恩", "伍献文", "陈垣", "胡先骕", "李济", "戴芳澜", "苏步青",
        "邓叔群", "吴定良", "俞大绂", "陈省身", "殷宏章", "钱崇澍", "柳诒徵", "冯德培", "傅斯年", "贝时璋", "姜立夫"
    ]
    
    ordered_images = []
    for name in ordered_names:
        found = False
        for filename, img, _ in images:
            base_name = filename.split("_")[0]  # 仅获取名字部分
            if base_name == name:
                ordered_images.append((name, img))
                found = True
                break
        if not found:
            print(f"未找到名字：{name} 对应的图片")
    
    return ordered_images

def main():
    false_folder = os.path.expanduser("~/Desktop/Wiki-EH")
    sample_folder = os.path.expanduser("~/Desktop/sample")
    sample_size = get_sample_image_size(sample_folder)
    print(f"基准图片的尺寸是: {sample_size}")

    images = load_images(false_folder)
    ordered_images = arrange_images_in_order(images)

    row_sizes = [11, 9, 8, 9, 11]
    row_spacing_factor = -0.85
    col_spacing_factors = [-1000, -1000, -1000, -1050, -1100]  # 示例：负数表示图片交叠 # 为每一排设定不同的列间距
    row_offsets = [0, -100, 250, 100, 0]

    folder = os.path.expanduser("~/Desktop")
    
    # 生成透明底图片并调整亮度
    composite_image_transparent = create_composite_image(ordered_images, row_sizes, row_spacing_factor, col_spacing_factors, (255, 255, 255, 0), row_offsets)
    composite_image_transparent = adjust_brightness(composite_image_transparent, 3.0)
    composite_image_transparent.save(os.path.join(folder, "composite_image_transparent.png"))
    
    # 生成黑色底图片并调整亮度
    composite_image_black = create_composite_image(ordered_images, row_sizes, row_spacing_factor, col_spacing_factors, (0, 0, 0, 255), row_offsets)
    composite_image_black = adjust_brightness(composite_image_black, 3.0)
    composite_image_black.save(os.path.join(folder, "composite_image_black.png"))

    print("两张图片已保存至：", folder)

if __name__ == "__main__":
    main()
