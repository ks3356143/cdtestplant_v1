#os.system(command)
import os,time
comment = input('请输入提交的标记名称：')
os.system("git add .")
os.system(f"git commit -m {comment}")
os.system("git push origin main --force")
os.system("pause")