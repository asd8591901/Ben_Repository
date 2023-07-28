# 导入模块
import xlrd

# 输入.sql文件名、changesetID
sqlname = input('输入文件名：')
changesetID = input('请输入ChangesetID：')


# 打开excel并打开工作簿
value = [] # 获取列表第一列、第二列的值
descrition = [] # 获取excel中第三列字段描述
xls = xlrd.open_workbook('C:\\Users\\Ben\\Desktop\\test.xlsx')
sheet = xls.sheets()[0]
for row in range(sheet.nrows):
    if row > 0:
        value.append(sheet.row_values(row))
    if row > 0:
        descrition.append(sheet.row_values(row)[2])

new_file = 'C:\\Users\\Ben\\Desktop\\' + sqlname + '.sql'

# 新建.sql文件
newflie = open(new_file, 'w',encoding = 'UTF-8')

# 写入.sql文件
newflie.write('--xx\n--changeset:'+changesetID+'\ncreate table if not exists '+sqlname+'\n(\n')
for i in range(len(value)):
    if i == 0:
        newflie.write(str(value[i][0]) + ' ' + str(value[i][1]) + ' ' + ' comment ' + "'" + str(descrition[i]) + "'" + '\n')
    if i > 0:
        newflie.write(',' + str(value[i][0]) + ' ' + str(value[i][1]) + ' ' + ' comment ' + "'" + str(descrition[i]) + "'" + '\n')
newflie.write(');\n--rollback;\n')

# 关闭.sql文件
newflie.close()
