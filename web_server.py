#!/usr/bin/env python3
import os
import subprocess
import json
import tempfile
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import cgi

# 定义服务器地址和端口
HOST = '127.0.0.1'
PORT = 8080

# ObfuScan可执行文件路径
OBFUSCAN_EXECUTABLE = os.path.join(os.path.dirname(__file__), 'ObfuScan.exe')

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            # 主页面
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(self.get_index_html().encode('utf-8'))
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/analyze':
            # 处理文件上传和分析请求
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST',
                         'CONTENT_TYPE': self.headers['Content-Type'],
                        }
            )
            
            if 'apk' not in form:
                self.send_error(400, 'No APK file uploaded')
                return
            
            apk_file = form['apk']
            if apk_file.filename == '':
                self.send_error(400, 'No file selected')
                return
            
            # 保存上传的APK文件
            with tempfile.NamedTemporaryFile(suffix='.apk', delete=False) as temp_file:
                temp_file.write(apk_file.file.read())
                temp_apk_path = temp_file.name
            
            try:
                # 调用ObfuScan分析APK
                result = self.run_obfuscan(temp_apk_path)
                
                # 返回分析结果
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
            finally:
                # 清理临时文件
                if os.path.exists(temp_apk_path):
                    os.unlink(temp_apk_path)
        else:
            self.send_error(404)
    
    def run_obfuscan(self, apk_path):
        """运行ObfuScan并返回分析结果"""
        try:
            # 检查ObfuScan.exe是否存在
            if not os.path.exists(OBFUSCAN_EXECUTABLE):
                return {
                    'error': True,
                    'message': f'ObfuScan.exe不存在。请先构建项目。\n构建步骤：\n1. 安装CMake\n2. 运行：mkdir build && cd build && cmake .. && cmake --build . --config Release'
                }
            
            print(f"正在执行ObfuScan: {OBFUSCAN_EXECUTABLE} {apk_path}")
            
            # 运行ObfuScan命令
            result = subprocess.run(
                [OBFUSCAN_EXECUTABLE, apk_path],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            print(f"ObfuScan返回码: {result.returncode}")
            print(f"ObfuScan标准输出: {result.stdout}")
            print(f"ObfuScan标准错误: {result.stderr}")
            
            if result.returncode != 0:
                return {
                    'error': True,
                    'message': f'ObfuScan执行失败: {result.stderr}\n返回码: {result.returncode}'
                }
            
            # 解析JSON输出
            try:
                analysis_result = json.loads(result.stdout)
                return {
                    'error': False,
                    'result': analysis_result
                }
            except json.JSONDecodeError as e:
                return {
                    'error': True,
                    'message': f'ObfuScan输出不是有效的JSON: {result.stdout}\n错误: {str(e)}'
                }
        except Exception as e:
            return {
                'error': True,
                'message': f'执行ObfuScan时发生错误: {str(e)}'
            }
    
    def get_index_html(self):
        """生成主页面HTML"""
        return '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ObfuScan - APK分析工具</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f4f4f4;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            background: #35424a;
            color: #ffffff;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 5px;
        }
        
        h1 {
            font-size: 28px;
            margin-bottom: 10px;
        }
        
        .upload-section {
            background: #ffffff;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        .upload-form {
            margin-top: 20px;
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        
        input[type="file"] {
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            width: 100%;
        }
        
        button {
            background: #35424a;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        
        button:hover {
            background: #2c3e50;
        }
        
        .loading {
            display: none;
            margin-top: 20px;
            padding: 10px;
            background: #f8f8f8;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        
        .results-section {
            background: #ffffff;
            padding: 20px;
            margin-top: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            display: none;
        }
        
        .summary {
            background: #f8f9fa;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 4px;
        }
        
        .summary-item {
            margin-bottom: 10px;
        }
        
        .result-item {
            margin-bottom: 20px;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        
        .result-item.high {
            border-left: 5px solid #dc3545;
        }
        
        .result-item.medium {
            border-left: 5px solid #ffc107;
        }
        
        .result-item.low {
            border-left: 5px solid #28a745;
        }
        
        .result-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .so-name {
            font-weight: bold;
            font-size: 18px;
        }
        
        .risk-level {
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 14px;
            font-weight: bold;
        }
        
        .risk-level.high {
            background: #dc3545;
            color: white;
        }
        
        .risk-level.medium {
            background: #ffc107;
            color: #333;
        }
        
        .risk-level.low {
            background: #28a745;
            color: white;
        }
        
        .result-details {
            margin-top: 10px;
        }
        
        .detail-item {
            margin-bottom: 8px;
        }
        
        .detail-label {
            font-weight: bold;
            margin-right: 10px;
        }
        
        .suspicious-points {
            margin-top: 10px;
        }
        
        .suspicious-points ul {
            margin-left: 20px;
        }
        
        .entry-previews {
            margin-top: 10px;
        }
        
        .entry-preview {
            margin-bottom: 8px;
            padding: 8px;
            background: #f8f9fa;
            border-radius: 4px;
        }
        
        .vmp-info {
            margin-top: 10px;
            padding: 10px;
            background: #e3f2fd;
            border-radius: 4px;
        }
        
        .error-message {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border: 1px solid #f5c6cb;
            border-radius: 4px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>ObfuScan - APK分析工具</h1>
            <p>快速分析Android APK中的Native SO文件，检测混淆、加壳等保护措施</p>
        </header>
        
        <div class="upload-section">
            <h2>上传APK文件</h2>
            <form class="upload-form" id="uploadForm" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="apkFile">选择APK文件：</label>
                    <input type="file" id="apkFile" name="apk" accept=".apk">
                </div>
                <button type="submit">开始分析</button>
            </form>
            <div class="loading" id="loading">
                <p>正在分析...请稍候</p>
            </div>
        </div>
        
        <div class="results-section" id="resultsSection">
            <h2>分析结果</h2>
            <div class="summary" id="summary"></div>
            <div id="resultList"></div>
        </div>
    </div>
    
    <script>
        document.getElementById('uploadForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const apkFile = document.getElementById('apkFile').files[0];
            
            if (!apkFile) {
                alert('请选择一个APK文件');
                return;
            }
            
            // 显示加载状态
            document.getElementById('loading').style.display = 'block';
            document.getElementById('resultsSection').style.display = 'none';
            
            // 发送请求
            fetch('/analyze', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                // 隐藏加载状态
                document.getElementById('loading').style.display = 'none';
                
                if (data.error) {
                    // 显示错误信息
                    document.getElementById('resultsSection').style.display = 'block';
                    document.getElementById('summary').innerHTML = '<div class="error-message">' + data.message + '</div>';
                    document.getElementById('resultList').innerHTML = '';
                } else {
                    // 显示分析结果
                    displayResults(data.result);
                }
            })
            .catch(error => {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('resultsSection').style.display = 'block';
                document.getElementById('summary').innerHTML = '<div class="error-message">分析过程中发生错误: ' + error.message + '</div>';
                document.getElementById('resultList').innerHTML = '';
            });
        });
        
        function displayResults(result) {
            // 显示结果区域
            document.getElementById('resultsSection').style.display = 'block';
            
            // 显示汇总信息
            const summary = result['汇总'];
            let summaryHtml = '<h3>汇总信息</h3>';
            summaryHtml += '<div class="summary-item"><span class="detail-label">总SO数量:</span> ' + summary['总so数量'] + '</div>';
            summaryHtml += '<div class="summary-item"><span class="detail-label">高风险:</span> ' + summary['高风险'] + '</div>';
            summaryHtml += '<div class="summary-item"><span class="detail-label">中风险:</span> ' + summary['中风险'] + '</div>';
            summaryHtml += '<div class="summary-item"><span class="detail-label">低风险:</span> ' + summary['低风险'] + '</div>';
            summaryHtml += '<div class="summary-item"><span class="detail-label">容器SO数量:</span> ' + summary['容器SO数量'] + '</div>';
            summaryHtml += '<div class="summary-item"><span class="detail-label">内层ELF成功提取数量:</span> ' + summary['内层ELF成功提取数量'] + '</div>';
            document.getElementById('summary').innerHTML = summaryHtml;
            
            // 显示详细结果
            const results = result['结果'];
            let resultsHtml = '';
            
            results.forEach(item => {
                const riskLevel = item['风险等级'];
                let riskClass = '';
                switch(riskLevel) {
                    case '高':
                        riskClass = 'high';
                        break;
                    case '中':
                        riskClass = 'medium';
                        break;
                    case '低':
                        riskClass = 'low';
                        break;
                }
                
                resultsHtml += '<div class="result-item ' + riskClass + '">';
                resultsHtml += '<div class="result-header">';
                resultsHtml += '<span class="so-name">' + item['so文件'] + '</span>';
                resultsHtml += '<span class="risk-level ' + riskClass + '">' + riskLevel + '</span>';
                resultsHtml += '</div>';
                
                resultsHtml += '<div class="result-details">';
                resultsHtml += '<div class="detail-item"><span class="detail-label">检测结果:</span> ' + item['检测结果'] + '</div>';
                resultsHtml += '<div class="detail-item"><span class="detail-label">说明:</span> ' + item['说明'] + '</div>';
                
                if (item['容器特征']) {
                    resultsHtml += '<div class="detail-item"><span class="detail-label">容器特征:</span> ' + item['容器特征'] + '</div>';
                }
                
                if (item['可疑点'] && item['可疑点'].length > 0) {
                    resultsHtml += '<div class="suspicious-points">';
                    resultsHtml += '<span class="detail-label">可疑点:</span>';
                    resultsHtml += '<ul>';
                    item['可疑点'].forEach(point => {
                        resultsHtml += '<li>' + point + '</li>';
                    });
                    resultsHtml += '</ul>';
                    resultsHtml += '</div>';
                }
                
                if (item['入口预览'] && item['入口预览'].length > 0) {
                    resultsHtml += '<div class="entry-previews">';
                    resultsHtml += '<span class="detail-label">入口预览:</span>';
                    item['入口预览'].forEach(entry => {
                        resultsHtml += '<div class="entry-preview">';
                        resultsHtml += '<strong>' + entry['名称'] + '</strong> (地址: ' + entry['地址'] + ')';
                        resultsHtml += '<br>预览: ' + entry['预览'];
                        resultsHtml += '</div>';
                    });
                    resultsHtml += '</div>';
                }
                
                if (item['VMP判断']) {
                    resultsHtml += '<div class="vmp-info">';
                    resultsHtml += '<span class="detail-label">VMP判断:</span> ' + item['VMP判断'] + '<br>';
                    resultsHtml += '<span class="detail-label">VMP分数:</span> ' + item['VMP分数'] + '<br>';
                    if (item['VMP特征'] && item['VMP特征'].length > 0) {
                        resultsHtml += '<span class="detail-label">VMP特征:</span>';
                        resultsHtml += '<ul>';
                        item['VMP特征'].forEach(feature => {
                            resultsHtml += '<li>' + feature + '</li>';
                        });
                        resultsHtml += '</ul>';
                    }
                    resultsHtml += '</div>';
                }
                
                resultsHtml += '<div class="detail-item"><span class="detail-label">建议:</span> ' + item['建议'] + '</div>';
                resultsHtml += '</div>';
                resultsHtml += '</div>';
            });
            
            document.getElementById('resultList').innerHTML = resultsHtml;
        }
    </script>
</body>
</html>
'''

def run_server():
    """启动HTTP服务器"""
    server = HTTPServer((HOST, PORT), RequestHandler)
    print(f"服务器运行在 http://{HOST}:{PORT}")
    print("按 Ctrl+C 停止服务器")
    server.serve_forever()

if __name__ == '__main__':
    run_server()
