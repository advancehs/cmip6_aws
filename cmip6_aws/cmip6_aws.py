"""Main module."""
import pandas as pd
import xarray
import re
import s3fs
import os
file_path = os.path.dirname(__file__)

class CMIP6:
    def __init__(self):
        df1 = pd.read_table( file_path+"/data/index_md5.txt", header=None)
        df2 = pd.read_table( file_path+"/data/index_v1.1_md5.txt",header=None)
        df3 = pd.read_table( file_path+"/data/index_v1.2_md5.txt",header=None)
        self.data = pd.concat([df1,df2,df3],axis=0)
        # 按空格分割数据，并取后一部分
        self.data['data'] = self.data[0].apply(lambda x: x.split(' ')[2])
        # self.df
        # 将“data”列按斜杠分开，并将每个部分赋值到新的列中
        split_data = self.data['data'].str.split('/', expand=True)
        num_cols = split_data.shape[1]
        column_names = [f'part_{i + 1}' for i in range(num_cols)]
        split_data.columns = column_names

        # 将分割后的数据合并到原始 DataFrame
        self.data = pd.concat([self.data, split_data], axis=1)

        # 删除原始列
        self.data.drop(columns=[0], inplace=True)

        def extract_year_and_version(filename):
            # 提取年份
            year_match = re.search(r'_(\d{4})', filename)
            year = year_match.group(1) if year_match else None

            # 尝试提取版本号
            version_match = re.search(r'_(v\d+\.\d+)', filename)
            version = version_match.group(1) if version_match else ''

            # 组合年份和版本号
            return f"{year}{version}"

        # 应用函数到 DataFrame
        self.data['part_6'] = self.data['part_6'].apply(extract_year_and_version)





        self.filtered_data = self.data
        self.current_download_link = None
        self.current_read_link = None

    def model(self):

        return list(self.filtered_data['part_2'].unique())

    def scenario(self, selected_model=None):
        if selected_model:
            self.filtered_data = self.filtered_data[self.filtered_data['part_2'] == selected_model]
        return list(self.filtered_data['part_3'].unique())

    def member(self, selected_scenario=None):
        if selected_scenario:
            self.filtered_data = self.filtered_data[self.filtered_data['part_3'] == selected_scenario]
        return list(self.filtered_data['part_4'].unique())

    def variable(self, selected_member=None):
        if selected_member:
            self.filtered_data = self.filtered_data[self.filtered_data['part_4'] == selected_member]
        return list(self.filtered_data['part_5'].unique())

    def year(self, selected_variable=None):
        if selected_variable:
            self.filtered_data = self.filtered_data[self.filtered_data['part_5'] == selected_variable]
        return list(self.filtered_data['part_6'].unique())

    def idm(self, outputdir, model, scenario, member, variable, year):
        selected_data = self.data[(self.data['part_2'] == model) &
                                  (self.data['part_3'] == scenario) &
                                  (self.data['part_4'] == member) &
                                  (self.data['part_5'] == variable) &
                                  (self.data['part_6'] == year)]

        ress1 = "https://nex-gddp-cmip6.s3-us-west-2.amazonaws.com/" + selected_data['data']
        ress = "\n".join(ress1)

        if not selected_data.empty:
            print("共找到{}条数据，并推送到idm下载".format(len(ress1)))
            self.current_download_link = ress1  # 假设有一个名为'download_link'的列

        else:
            self.result.setText('未找到匹配数据')
            self.current_download_link = None

        from subprocess import call

        # 启动idm下载
        IDM = r"C:\Program Files (x86)\Internet Download Manager\IDMan.exe"

        # 下载路径
        DownPath = 'D:/downloadidm/'

        # 下载文件名称

        # 下载文件链接（注意是这个列表）
        urlList = self.current_download_link
        # 将下载链接全部加入到下载列表，之后再进行下载。
        for ul in urlList:
            local_file_name = ul[-40:]

            call([IDM, '/d', ul, '/p', DownPath, '/f', local_file_name, '/n', '/a'])
        call([IDM, '/s'])

        # return ress

    def down(self, outputdir, model, scenario, member, variable, year, latminmax, lonminmax):
        if (latminmax[1] < latminmax[0]) or (lonminmax[1] < lonminmax[0]):
            raise SyntaxError("latminmax和lonminmax 中的数字必须前者小于后者")
        selected_data = self.data[(self.data['part_2'] == model) &
                                  (self.data['part_3'] == scenario) &
                                  (self.data['part_4'] == member) &
                                  (self.data['part_5'] == variable) &
                                  (self.data['part_6'] == year)]

        ress1 = "s3://nex-gddp-cmip6/" + selected_data['data']
        ress = "\n".join(ress1)

        if not selected_data.empty:
            print("共找到{}条数据，并使用xarray读取".format(len(ress1)))
            self.current_read_link = ress1  # 假设有一个名为'download_link'的列

        else:
            self.result.setText('未找到匹配数据')
            self.current_read_link = None

        # 读取文件链接（注意是这个列表）
        urlList = self.current_read_link

        fs = s3fs.S3FileSystem(anon=True)

        # 使用读取链接挨个读取文件，并切片范围。
        for ul in urlList:
            with fs.open(ul) as f:
                ds = xarray.open_dataset(f).sel(lat=slice(latminmax[0], latminmax[1]),
                                                lon=slice(lonminmax[0], lonminmax[1]))  # ['tm'].rio.write_crs("4326")
                ds.to_netcdf('{}/{}'.format(outputdir, ul.split("/")[-1]))
                print("文件已保存在{}/{}中".format(outputdir, ul.split("/")[-1]))

    def reset(self):
        self.filtered_data = self.data

