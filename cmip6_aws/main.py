"""Main module."""
import sys
import pandas as pd
import xarray as xr
import os

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QTextEdit, QPushButton, \
    QLineEdit, QFileDialog


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.loadData()

    def initUI(self):
        self.setWindowTitle('数据查询工具')
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        # 创建下拉框
        self.combo2 = QComboBox()
        self.combo3 = QComboBox()
        self.combo4 = QComboBox()
        self.combo5 = QComboBox()
        self.combo6 = QComboBox()

        layout.addWidget(QLabel('Part 2:'))
        layout.addWidget(self.combo2)
        layout.addWidget(QLabel('Part 3:'))
        layout.addWidget(self.combo3)
        layout.addWidget(QLabel('Part 4:'))
        layout.addWidget(self.combo4)
        layout.addWidget(QLabel('Part 5:'))
        layout.addWidget(self.combo5)
        layout.addWidget(QLabel('Part 6:'))
        layout.addWidget(self.combo6)

        # 添加经纬度范围输入
        lat_lon_layout = QHBoxLayout()

        self.lat_min = QLineEdit()
        self.lat_max = QLineEdit()
        self.lon_min = QLineEdit()
        self.lon_max = QLineEdit()

        lat_lon_layout.addWidget(QLabel('纬度最小值:'))
        lat_lon_layout.addWidget(self.lat_min)
        lat_lon_layout.addWidget(QLabel('纬度最大值:'))
        lat_lon_layout.addWidget(self.lat_max)
        lat_lon_layout.addWidget(QLabel('经度最小值:'))
        lat_lon_layout.addWidget(self.lon_min)
        lat_lon_layout.addWidget(QLabel('经度最大值:'))
        lat_lon_layout.addWidget(self.lon_max)

        layout.addLayout(lat_lon_layout)

        # 创建查询按钮
        query_button = QPushButton('查询')
        query_button.clicked.connect(self.onQuery)
        layout.addWidget(query_button)

        # 创建下载按钮
        download_button = QPushButton('下载')
        download_button.clicked.connect(self.onDownload)
        layout.addWidget(download_button)

        # 创建剪裁按钮
        clip_button = QPushButton('剪裁')
        clip_button.clicked.connect(self.onClip)
        layout.addWidget(clip_button)

        # 创建结果显示区域
        self.result = QTextEdit()
        self.result.setReadOnly(True)
        layout.addWidget(self.result)

        self.setLayout(layout)
        self.setWindowTitle('查询系统')

    def loadData(self):
        # 读取CSV文件
        # df1 = pd.read_table(r"https://github.com/advancehs/cmip6_aws/blob/master/index_md5.txt?raw=true",header=None)
        # df2 = pd.read_table(r"https://github.com/advancehs/cmip6_aws/blob/master/index_v1.1_md5.txt?raw=true",header=None)
        # df3 = pd.read_table(r"https://github.com/advancehs/cmip6_aws/blob/master/index_v1.2_md5.txt?raw=true",header=None)
        df1 = pd.read_table(r"index_md5.txt", header=None)
        df2 = pd.read_table(r"index_v1.1_md5.txt",header=None)
        df3 = pd.read_table(r"index_v1.2_md5.txt",header=None)
        self.df = pd.concat([df1,df2,df3],axis=0)
        # 按空格分割数据，并取后一部分
        self.df['data'] = self.df[0].apply(lambda x: x.split(' ')[2])
        # self.df
        # 将“data”列按斜杠分开，并将每个部分赋值到新的列中
        split_data = self.df['data'].str.split('/', expand=True)
        num_cols = split_data.shape[1]
        column_names = [f'part_{i + 1}' for i in range(num_cols)]
        split_data.columns = column_names

        # 将分割后的数据合并到原始 DataFrame
        self.df = pd.concat([self.df, split_data], axis=1)

        # 删除原始列
        self.df.drop(columns=[0], inplace=True)
        self.df['part_6'] = self.df['part_6'].apply(lambda x: x[-30:])

        # 填充part_2的下拉框
        self.combo2.addItems(self.df['part_2'].unique())

        # 连接part_2的下拉框变化信号到更新函数
        self.combo2.currentIndexChanged.connect(self.updatePart3Options)

        # 初始化其他下拉框
        self.updatePart3Options()

    def updatePart3Options(self):
        selected_part2 = self.combo2.currentText()
        part3_options = self.df[self.df['part_2'] == selected_part2]['part_3'].unique()

        self.combo3.clear()
        self.combo3.addItems(part3_options)

        # 连接part_3的下拉框变化信号到更新函数
        self.combo3.currentIndexChanged.connect(self.updatePart4Options)

        self.updatePart4Options()

    def updatePart4Options(self):
        selected_part2 = self.combo2.currentText()
        selected_part3 = self.combo3.currentText()
        part4_options = self.df[(self.df['part_2'] == selected_part2) &
                                (self.df['part_3'] == selected_part3)]['part_4'].unique()

        self.combo4.clear()
        self.combo4.addItems(part4_options)

        # 连接part_4的下拉框变化信号到更新函数
        self.combo4.currentIndexChanged.connect(self.updatePart5Options)

        self.updatePart5Options()

    def updatePart5Options(self):
        selected_part2 = self.combo2.currentText()
        selected_part3 = self.combo3.currentText()
        selected_part4 = self.combo4.currentText()
        part5_options = self.df[(self.df['part_2'] == selected_part2) &
                                (self.df['part_3'] == selected_part3) &
                                (self.df['part_4'] == selected_part4)]['part_5'].unique()

        self.combo5.clear()
        self.combo5.addItems(part5_options)

        # 连接part_5的下拉框变化信号到更新函数
        self.combo5.currentIndexChanged.connect(self.updatePart6Options)

        self.updatePart6Options()

    def updatePart6Options(self):
        selected_part2 = self.combo2.currentText()
        selected_part3 = self.combo3.currentText()
        selected_part4 = self.combo4.currentText()
        selected_part5 = self.combo5.currentText()

        part6_options = self.df[(self.df['part_2'] == selected_part2) &
                                (self.df['part_3'] == selected_part3) &
                                (self.df['part_4'] == selected_part4) &
                                (self.df['part_5'] == selected_part5)]['part_6'].unique()

        self.combo6.clear()
        self.combo6.addItems(part6_options)

    def onQuery(self):
        selected = self.df[(self.df['part_2'] == self.combo2.currentText()) &
                           (self.df['part_3'] == self.combo3.currentText()) &
                           (self.df['part_4'] == self.combo4.currentText()) &
                           (self.df['part_5'] == self.combo5.currentText()) &
                           (self.df['part_6'] == self.combo6.currentText())]
        ress1 = "https://nex-gddp-cmip6.s3-us-west-2.amazonaws.com/" + selected['data']

        ress = "\n".join(ress1)

        if not selected.empty:
            self.result.setText(ress)
            self.current_download_link = ress1  # 假设有一个名为'download_link'的列

        else:
            self.result.setText('未找到匹配数据')
            self.current_download_link = None

    def onDownload(self):

        # 用于调用CMD命令行
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

    def onClip(self):
        # 选择要剪裁的netCDF文件
        file_path, _ = QFileDialog.getOpenFileName(self, "选择netCDF文件", "", "NetCDF Files (*.nc)")
        if not file_path:
            self.result.append("\n未选择文件")
            return

        try:
            # 读取netCDF文件
            ds = xr.open_dataset(file_path)

            # 获取用户输入的经纬度范围
            lat_min = float(self.lat_min.text()) if self.lat_min.text() else None
            lat_max = float(self.lat_max.text()) if self.lat_max.text() else None
            lon_min = float(self.lon_min.text()) if self.lon_min.text() else None
            lon_max = float(self.lon_max.text()) if self.lon_max.text() else None

            # 进行剪裁
            ds_clipped = ds.sel(lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max))

            # 自动生成带有"clip"后缀的文件名
            file_name = os.path.basename(file_path)
            file_name_without_ext = os.path.splitext(file_name)[0]
            new_file_name = f"{file_name_without_ext}_clip.nc"
            default_save_path = os.path.join(os.path.dirname(file_path), new_file_name)

            # 保存剪裁后的文件
            save_path, _ = QFileDialog.getSaveFileName(self, "保存剪裁后的文件", default_save_path,
                                                       "NetCDF Files (*.nc)")
            if save_path:
                print(save_path)
                ds_clipped.to_netcdf(save_path)
                self.result.append(f"\n剪裁完成，文件已保存至: {save_path}")
            else:
                self.result.append("\n未选择保存路径，剪裁操作已取消")

            # 关闭数据集
            ds.close()
            ds_clipped.close()

        except Exception as e:
            self.result.append(f"\n剪裁失败: {str(e)}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
