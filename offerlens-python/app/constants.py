"""全局业务上限。

这些数字必须三层保持一致，否则会出现「前端放行、后端拒绝」或
「后端放行、数据库存不下」的中间态：

    Vue textarea maxlength  <=  MAX_TEXT_CHARS  <=  Java 校验  <=  MySQL TEXT

MySQL 的 `TEXT` 上限是 65,535 **字节**（不是字符）。UTF-8 中文占 3 字节，
所以 20,000 字符 ≈ 60,000 字节，留出 5,535 字节余量。
"""

# 单段文本（简历 / JD）的字符上限，中文 20,000 字约 60,000 字节
MAX_TEXT_CHARS = 20_000

# 上传文件体积上限
MAX_UPLOAD_BYTES = 10 * 1024 * 1024

# PDF 页数上限，防止几百页的文档卡住解析
MAX_PDF_PAGES = 50
