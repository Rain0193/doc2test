# 本项目为了优化和解决以下工作问题:

1) webserivce接口集成测试的特点是: 围绕集成接口规格说明书建立工作过程, 不同的目标可能需要维护多套文档. 这样造成的问题是文档与测试执行的代码存在脱节的风险, 如果能直接实现从文档到测试的过程, 简化了工作步骤, 降低了这种风险.

2) 工具化的文档读取(如loadrunner,postman,jmeter)依赖于工具本身,存在一定的约束性,扩展性也较低, 工具本身就带来一定的门槛,常规的接口测试过程使用类似工具笨重不灵活.

3) excel 文档的表现方式丰富, 优于文本\配置文件, 其维护性和可读性又优于代码脚本, 如果能快速的可视化的编写测试过程, 将减少测试代码编写和维护量. 本框架兼容 Linux 和 Windows, 直接解决 跨平台的调用和调试的统一问题(如jenkins调用) 


# 语法支持及使用方法,  请参考本项目Wiki:
http://callisto.ngrok.cc/wiki/doku.php?id=doc2test

