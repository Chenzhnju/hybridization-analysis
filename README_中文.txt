附录 D 精确验证代码与证书

对应论文 Hybrid correlation generation with finite shared randomness，作者为 Zihan Chen、Shengjun Wu 和 Zeng-Bing Chen。

软件版本为 31.2，证书版本为 Release 31。GitHub 发布包整理日期为 2026 年 11 月 23 日。LICENSE 采用 MIT，版权署名为上述三位作者。

完整解压后，在含 verify.py 的目录运行以下命令。

    python verify.py --check-integrity
    python verify.py
    python -m unittest discover -v
    python worked_examples.py

需要 Python 3.8 或更高版本，运行时启用断言，依赖均为 Python 标准库。Windows 可以双击 RUN_WINDOWS.cmd 完成计算验证。成功时打印 PASS_EXACT_VERIFICATION，退出码为 0。测试命令执行 23 项回归测试，算例命令最后显示 PASS_WORKED_EXAMPLES。

第一阶段检查式 (D.3) 的三标签 CC 构造、D.1 的见证和 D.2 的标量截止值。第二阶段检查 D.3 的支撑分类与完整覆盖。第三阶段检查 D.4 的局部行界、权重界、D.5 的标量估计和 D.6 的边缘等式。几何约化、平均与积分以及物理协议分类的解析论证见论文。

完整验证包含 49 个支撑轨道、2,744 个全局叶节点、467 个局部叶节点和 16,996 项局部行界，并拒绝 18 个故意设置的无效对照。

每次运行的结果保存在 reports/ 的独立子目录，reports/latest.json 指向最新摘要。随包 reference_reports/ 保存本次发布整理后的完整参考报告。docs/DOCUMENT_VERSIONS.json 记录 SciPost 34 页稿和 PRA 20 页稿的页数与 SHA-256，历史 Word 稿信息单列保存。

上传 GitHub 时，将本目录中的文件放在仓库根目录，使 README.md、verify.py、certificates/ 和 tests/ 可以直接看到。GitHub Desktop 中提交文件后，选择 Publish repository，确认账号、仓库名与公开范围。建议仓库名为 hybrid-correlation-verification。

包内已包含 .gitignore、.gitattributes 和 .github/workflows/verify.yml。提交时一并包含这些以点开头的文件。所有分发文本统一为 UTF-8、LF 换行。GitHub Actions 配置会在 Windows 和 Ubuntu 上，使用 Python 3.8、3.12、3.14 自动运行上述四项检查。

仓库创建后，在 CITATION.cff 中补上真实 repository-code 地址。实际发布时再填写 date-released。若使用 Zenodo，在生成正式 GitHub Release 前连接公开仓库，随后把取得的版本 DOI 填入引用信息，并用于论文中的软件参考文献。上述字段应采用发布服务给出的实际值。

仓库中的说明或引用信息变动后，先用 git add . 暂存需要发布的文件，再运行 python tools/update_manifest.py 更新 SHA256SUMS，然后重新执行四项检查并提交校验清单。软件或证书改动后还应刷新 reference_reports/ 中的运行证据并记录新版本。

首次正式发布可使用 v31.2 标签，并把对应 ZIP 上传到 GitHub Releases。后续版本按新的标签发布。详细步骤与可直接使用的版本说明见 docs/RELEASING.md。
