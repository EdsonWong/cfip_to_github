import json
import base64
import csv
import subprocess
import os
import yaml

#######################
###     mbp2015     ###
#######################

# 每天 0:15 执行 main.py 先IP优选 再将优选IP写入 json文件 并将 json文件 转为 订阅文件，最后提交github
# 15 0 * * * cd /mac/cfip_to_github && /User/mac/anaconda3/bin/python main.py

# 获取当前工作路径
current_dir = os.getcwd()

# 执行 CloudflareST 进行IP优选 
# subprocess.run(["./CloudflareST", "-n", "500", "-t", "10", "-httping", "-cfcolo", "HKG", "-tl", "100", "-tlr", "0.05", "-sl", "10", "-p" ,"5", "-f", "ip.txt", "-o", "result_hk.csv"], check=True)
# subprocess.run(["./CloudflareST", "-httping", "-cfcolo", "LAX,SEA,SJC", "-n", "400", "-t", "8", "-tl", "500", "-tlr", "0.05", "-sl", "5", "-p" ,"5", "-f", "ip.txt", "-o", "result_usa.csv"], check=True)
# subprocess.run(["./CloudflareST", "-url", "https://pencilfiles.annonymus.cf/cloudflarest-200mb.rar", "-httping", "-cfcolo", "HKG", "-n", "300", "-t", "8", "-tl", "200", "-tlr", "0.5", "-sl", "5", "-p" ,"10", "-f", "newip.txt", "-o", "result_hk.csv"], check=True)
subprocess.run(["./CloudflareST",
            "-url", "https://cdn.cloudflare.steamstatic.com/steam/apps/256843155/movie_max.mp4",
            "-n", "350",
            "-t", "8",
            "-tl", "250",
            "-sl", "10",
            "-tlr", "0.4",
            "-f", "newip.txt"],
            check=True)

# csv文件路径
csv_path = os.path.join(current_dir,"result.csv")

# 打开CSV文件并读取IP地址
with open(csv_path, 'r') as f:
    reader = csv.reader(f)
    next(reader)  # 跳过表头
    ip_addresses = [row[0] for _, row in zip(range(10), reader)]  # 获取前10个IP地址

################################
# 开始将 csv 转 sing-box 订阅链接
################################
# json文件的路径
json_path = os.path.join(current_dir,"my_cfip_with_rules.json")

# 打开JSON文件并加载数据
with open(json_path, 'r') as f:
    data = json.load(f)

# 在数据中更新服务器地址
ip_index = 0
for outbound in data['outbounds']:
    if 'server' in outbound and ip_index < len(ip_addresses):
        outbound['server'] = ip_addresses[ip_index]
        ip_index += 1

# 将更新后的数据写回JSON文件
with open(json_path, 'w') as f:
    json.dump(data, f, indent=4)
# 更新完json


################################
# 开始将 csv 转 clash 订阅链接
################################
# 读取YAML文件
with open('my_cfip.yaml', 'r') as f:
    data = yaml.safe_load(f)

# 替换server字段
for i, proxy in enumerate(data['proxies']):
    if i < len(ip_addresses):
        proxy['server'] = ip_addresses[i]

# 写入YAML文件
with open('my_cfip.yaml', 'w') as f:
    yaml.safe_dump(data, f)
# 更新完yaml


################################
# 开始将 json 转 sr 订阅链接
################################
# Load the data from the JSON file
with open(json_path) as f:
    data = json.load(f)

# Extract the vless nodes
vless_nodes = [node for node in data['outbounds'] if node['type'] == 'vless']

# Generate the links for each node
links = []
i = 1
for node in vless_nodes:
    link = f"vless://{node['uuid']}@{node['server']}:{node['server_port']}?encryption=none&sni=usip.mark-jones-w.workers.dev&fp=randomized&type=ws&host=usip.mark-jones-w.workers.dev&path=%2F%3Fed%3D2048#icon.mbp2015.dev{i}"
    i += 1
    links.append(link)

# Convert the links to a Shadowrocket subscription link
links_str = '\n'.join(links)
sr_links_base64 = base64.b64encode(links_str.encode()).decode()

# Write the base64 links to the subscribe file
sub_path = os.path.join(current_dir, "my_cfip_sr_sub.txt")
with open(sub_path, 'w') as f:
    f.write(sr_links_base64)
# 更新完 sr 订阅

# Git
# get changes
subprocess.run(["git", "pull", "gitlab", "mbp2015"], check=True)
subprocess.run(["git", "pull", "github", "mbp2015"], check=True)

# Add all changes to staging area
subprocess.run(["git", "add", "."], check=True)

# Commit changes
subprocess.run(["git", "commit", "-m", "mbp2015"], check=True)

# Pull and push to the branch
# GitLab
subprocess.run(["git", "push", "gitlab", "mbp2015"], check=True)
# GitHub
subprocess.run(["git", "push", "github", "mbp2015"], check=True)
