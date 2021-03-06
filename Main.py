
from PyQt5.QtWidgets import (QApplication, QMessageBox, QMainWindow, QVBoxLayout, QAction, QFileDialog, QDialog,
                             QTabWidget, QWidget, QPushButton, QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon
from PyQt5.uic import loadUiType
from os.path import dirname, realpath, join
from sys import argv
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from mpl_toolkits.mplot3d import axis3d, axes3d
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np


from feature_store import FeatureStore


scriptDir = dirname(realpath(__file__))
FROM_MAIN, _ = loadUiType(join(dirname(__file__), "mainwindow.ui"))


class Main(QMainWindow, FROM_MAIN):

    def __init__(self, parent=FROM_MAIN):
        super(Main, self).__init__()

        QMainWindow.__init__(self)
        self.setupUi(self)
        self.listWidget.addItem("Add data file")

        self.layout = QVBoxLayout(self.frame)

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.visualizations = QWidget()
        self.tables = QWidget()
        self.tabs.resize(300, 200)

        # Add tabs
        self.tabs.addTab(self.visualizations, "Visualizations")
        self.tabs.addTab(self.tables, "Tables")

        # Create first tab
        self.visualizations.layout = QVBoxLayout(self)
        self.sc = MyCanvas()
        self.visualizations.layout.addWidget(self.sc)
        self.visualizations.setLayout(self.visualizations.layout)

        # Create second tab
        self.tables.layout = QVBoxLayout(self)
        self.tableWidget = QTableWidget()
        self.tables.layout.addWidget(self.tableWidget)
        self.tables.setLayout(self.tables.layout)

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        self.Qe = False
        self.quit_switch = False

        # create toolbar
        add_file = QAction(QIcon('icons/add-file.png'), 'Add Data File', self)
        add_file.setShortcut('Ctrl+N')
        add_file.triggered.connect(self.browse_folder)

        scatter3D = QAction(QIcon('icons/cupe.PNG'), 'Scatter 3D', self)
        scatter3D.setShortcut('Ctrl+L')
        scatter3D.setEnabled(1)
        scatter3D.triggered.connect(self.pass_placeholder)

        regression3D = QAction(QIcon('icons/cupe_plan.PNG'), 'Regression 3D', self)
        regression3D.setShortcut('Ctrl+r')
        regression3D.setEnabled(1)
        regression3D.triggered.connect(self.pass_placeholder)

        scatter2D = QAction(QIcon('icons/scatter-graph.png'), 'Scatter 2D', self)
        scatter2D.setShortcut('Ctrl+L')
        scatter2D.setEnabled(1)
        scatter2D.triggered.connect(self.Plot2D)

        regression2D = QAction(QIcon('icons/linear-regression.png'), 'Regression 2D', self)
        regression2D.setShortcut('Ctrl+K')
        regression2D.setEnabled(1)
        regression2D.triggered.connect(self.Regression2d)

        self.toolbar = self.addToolBar('Add data file')
        self.toolbar.addAction(add_file)
        self.toolbar.addAction(scatter2D)
        self.toolbar.addAction(regression2D)
        self.toolbar.addAction(scatter3D)
        self.toolbar.addAction(regression3D)

        # create two tabs
        self.tabWidget.addTab(self.tab, "Results")
        self.tabWidget.addTab(self.tab_2, "Info")

        # create menu bar, to revist
        self.actionSave_2.setShortcut('Ctrl+S')
        self.actionSave_2.setStatusTip('Save')
        self.actionSave_2.triggered.connect(self.save_file)

        self.actionExit.setShortcut('Ctrl+Q')
        self.actionExit.setStatusTip('Quit')
        self.actionExit.triggered.connect(self.quit)

        self.actionNew.setShortcut('Ctrl+D')
        self.actionNew.setStatusTip('Add File')
        self.actionNew.triggered.connect(self.browse_folder)

        self.actionHelp.setShortcut('Ctrl+H')
        self.actionHelp.setStatusTip('Help')
        self.actionHelp.triggered.connect(self.help)

    def pass_placeholder(self):
        pass

    def quit(self):
        self.quit_switch = True
        self.message_save()

    def help(self):
        # not sure where to find this in the UI yet
        QMessageBox.critical(self, 'Aide', "Hello This is PyQt5 Gui and Matplotlib ")

    def save_file(self):
        # will have to modify
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self, "Save", self.name, "Text Files (*.txt);;All Files (*)")

        f = open(file_name, 'w')
        f.write(self.name)
        f.write('\n')
        f.write('Some results')
        f.write('\n')
        f.write('Some results ')
        f.write('\n')
        self.Qe = False

    def message_save(self):
        button_reply = QMessageBox.question(self, 'Soft', "  Save ?",
                                            QMessageBox.Save | QMessageBox.No | QMessageBox.Cancel,
                                            QMessageBox.Cancel)
        if button_reply == QMessageBox.Save:
            self.save_file()
        elif button_reply == QMessageBox.No:
            if self.quit_switch:
                self.close()

            else:
                self.Qe = False
                self.browse_folder()

    def browse_folder(self):
        """Select a csv file."""
        global current_file

        if self.Qe:
            self.message_save()
        else:
            current_file, _ = QFileDialog.getOpenFileName(self, "Open", "", "CSV files (*.csv)")
            if current_file:
                self.listWidget.clear()
                self.listWidget.addItem(current_file)

    def create_table(self):
        """Display table of the selected file's data."""
        csv_test = FeatureStore('data/' + current_file.split('/data/')[1])
        n, m = csv_test.df.shape

        self.tableWidget.setRowCount(n)
        self.tableWidget.setColumnCount(m)
        self.tableWidget.setHorizontalHeaderLabels(csv_test.df.columns)

        for n_range in range(n):
            for m_range in range(m):
                self.tableWidget.setItem(n_range, m_range, QTableWidgetItem(str(csv_test.df.iloc[n_range, m_range])))

        self.tableWidget.move(0, 0)

    def Plot2D(self):
        self.create_table()
        csv_test = FeatureStore('data/' + current_file.split('/data/')[1])

        n = ""
        try:
            n = csv_test.df.shape[0]

            if n < 4:
                QMessageBox.warning(self, 'Error', "Number of points < 4!")
                return
        except:
            QMessageBox.critical(self, 'Error', "   No data file!")

        if n != "":
            a, b = 1, 2

            self.lineEdit.setText(str(a))
            self.lineEdit_2.setText(str(b))
            self.lineEdit_3.setText(' ')
            self.label_7.setText(' ')
            self.reg.setText(" Z = Ax + B")

            self.Qe = True
            try:
                self.sc.plot2D(csv_test.df['age'].tolist(), csv_test.df['trestbps'].tolist())
            except:
                QMessageBox.critical(self, 'Error', "   Error plot!")

    def Regression2d(self):
        self.create_table()
        csv_test = FeatureStore('data/' + current_file.split('/data/')[1])

        n = ""
        try:
            n = csv_test.df.shape[0]

            if n < 4:
                QMessageBox.warning(self, 'Error', "Number of points < 4!")
                return
        except:
            QMessageBox.critical(self, 'Error', "   No data file!")

        if n != "":
            X = csv_test.df['age'].to_numpy().reshape(-1, 1)
            y = csv_test.df['trestbps'].to_numpy()
            reg = LinearRegression().fit(X, y)
            a, b = reg.coef_[0], reg.intercept_
            y_pred = reg.predict(X)

            self.lineEdit.setText(str(a))
            self.lineEdit_2.setText(str(b))
            self.lineEdit_3.setText(' ')
            self.label_7.setText(' ')
            self.reg.setText(" Z = Ax + B")

            self.Qe = True
            try:
                self.sc.plot2DM(X, y, y_pred)
            except:
                QMessageBox.critical(self, 'Error', "   Error plot!!")


class MyCanvas(FigureCanvas):

    def __init__(self):
        self.fig = Figure()
        FigureCanvas.__init__(self, self.fig)

    def plot2D(self, xarray, zarray):
        self.fig.clear()
        axe = self.fig.add_subplot(111)
        axe.plot(xarray, zarray, 'ok')
        axe.set_xlabel('X ')
        axe.set_ylabel('Y ')
        self.draw()

    def plot2DM(self, xarray, zarray, za):
        self.fig.clear()
        axe = self.fig.add_subplot(111)
        axe.plot(xarray, zarray, "ok")
        axe.plot(xarray, za, 'r-')
        axe.set_xlabel('X ')
        axe.set_ylabel('Y ')
        self.draw()


def main():
    app = QApplication(argv)
    window = Main()
    # window.showFullScreen() # Start at position full screen
    window.showMaximized()  # Start position max screen
    app.exec_()


if __name__ == '__main__':
    main()
